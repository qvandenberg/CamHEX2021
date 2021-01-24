from optibook.synchronous_client import Exchange
import logging
from datetime import datetime as dt
import datetime
import time

from PriceBooks import LatestPriceBook
from TradeHistory import TradeHistory
from RiskManagement import RiskManagement

# Settings
instruments = ['PHILIPS_A', 'PHILIPS_B']
LOSS_THRESHOLD = 0.95 # tolerate up to 5% drop in profit & loss
DATA_COLLECTION_TIME = 10 # seconds before we start trading
TRADE_THRESHOLD = 0.1 # difference in price before trade
MAX_POSITION = 250
STANDARD_VOLUME = 20

'''
The algorithm class is the class that orchestrates the decision making, and it makes use of
the PriceBook, RiskManagement and TradeHistory classes.

The trading logic is as follows:
- Compare the trade history price to the latest orderbook price
- If any instrument (in any direction) is mispriced, create an opposing order: provide liquidity
- When our position grows too much, to the MAX_POSITION value: only provide
    liquidity in the direction that removes our position.

It is a largely passive algorithm that snatches up other existing trades, rather than constantly quoting on bot sides of the book.
'''
class AlgoPassive:

    def __init__(self, exchange, instruments):
        # Connectivity
        self.instruments = instruments
        self.exchange = exchange
        self.exchange.connect()
        self.delete_all_outstanding_orders()
        # Bookkeeping: trades, prices, our positions
        self.pb = LatestPriceBook(exchange, instruments)
        self.th = TradeHistory(exchange, instruments)
        self.rm = RiskManagement(exchange, instruments)

    def delete_all_outstanding_orders(self):
        for instr in self.instruments:
            outstanding = self.exchange.get_outstanding_orders(instr)
            for o in outstanding.values():
                result = self.exchange.delete_order(instr, order_id=o.order_id)
                print(f"Deleted order id {o.order_id}: {result}")

    def get_latest_exchange_information(self):
        self.pb.refresh_price_book() # get latest price book
        self.rm.update_new_trades() # update our private trade history
        self.th.poll_new_trade_ticks() # update public trade history

    def search_trade_opportunity(self): # {instrument : {price: , volume: , side}}
        # Compare trade history prices to current pricebooks
        opportunities = {}
        for instr in self.instruments:
            real_price = self.th.get_real_price(instr)
            # Bid side
            bid_price, bid_vol = self.pb.get_best_bid_price_volume(instr) # best price, total volume
            best_bid_vol = self.pb.instruments[instr]['best_bid_volume']
            if ((real_price is not None and bid_price is not None )and bid_price > real_price):
                opportunities[instr] = {'price': bid_price, 'volume': best_bid_vol, 'side': 'bid'}
            # ask side
            ask_price, ask_vol = self.pb.get_best_ask_price_volume(instr) # best price, total volume
            best_ask_vol = self.pb.instruments[instr]['best_ask_volume']
            if ((real_price is not None and ask_price is not None) and ask_price < real_price):
                opportunities[instr] = {'price': bid_price, 'volume': best_bid_vol, 'side': 'ask'}
        return opportunities

    def book_limit_transaction(self, order_param): # {instrument : , price: , volume: , side:}
        vol = self.rm.get_max_trade_size(order_param['instrument'], order_param['side'])
        if (vol >= 1):
            order_id = self.exchange.insert_order(order_param['instrument'], price=order_param['price'], volume=vol, side=order_param['side'], order_type='limit')
            self.rm.archive_order_to_market({'instrument':order_param['instrument'], 'order_id': order_id, 'price': order_param['price'], 'volume': vol, 'side': order_param['side']})

    def book_ioc_transaction(self, order_param): # {instrument : , price: , volume: , side:}
        order_id = self.exchange.insert_order(order_param['instrument'], price=order_param['price'], volume=order_param['volume'], side=order_param['side'], order_type='ioc')
        self.rm.archive_order_to_market({'instrument':order_param['instrument'], 'order_id': order_id, 'price': order_param['price'], 'volume': order_param['volume'], 'side': order_param['side']})

    def run(self):
        start_time = dt.now()
        while (dt.now() - start_time < datetime.timedelta(seconds=DATA_COLLECTION_TIME)):
            # Collect data before we start trading
            self.get_latest_exchange_information()

        # while (self.rm.curr_to_prev_pnl_fraction() < LOSS_THRESHOLD): # pnl acceptable
        while (True): # test
            self.get_latest_exchange_information()

            # Restore our positions closer to zero
            for instr in self.instruments:
                if self.rm.allowed_to_mutate_orders() and abs(self.rm.positions[instr]) >= MAX_POSITION:
                    if (self.rm.positions[instr] < -MAX_POSITION): # buy some to restore position
                        best_bid, dummy = self.pb.get_best_bid_price_volume(instr)
                        self.book_ioc_transaction({'instrument': instr, 'price': best_bid, 'volume': STANDARD_VOLUME, 'side': 'bid'})
                        print("Placing restoring buy order at price %.2f." %(best_bid))
                    elif (self.rm.positions[instr] > MAX_POSITION): # sell some to restore position
                        best_ask, dummy = self.pb.get_best_ask_price_volume(instr)
                        self.book_ioc_transaction({'instrument': instr, 'price': best_ask, 'volume': STANDARD_VOLUME, 'side': 'ask'})
                        print("Placing restoring sell order at price %.2f." %(best_ask))
            # Marketmaking
            trade_opportunities = self.search_trade_opportunity()
            if len(trade_opportunities) > 0 and self.rm.allowed_to_mutate_orders():
                for instr, param in trade_opportunities.items():
                    if abs(self.rm.positions[instr]) < MAX_POSITION:
                        if param['side'] == 'bid':
                            vol = min(self.rm.get_max_trade_size(instr, 'bid'), param['volume'])
                            self.book_limit_transaction({'instrument': instr, 'price': param['price'], 'volume': vol, 'side': 'ask'})
                            print("Placing order: volume %d price %.2f" %(vol, param['price']))
                        elif param['side'] == 'ask':
                            vol = min(self.rm.get_max_trade_size(instr, param['side']), param['volume'])
                            self.book_limit_transaction({'instrument': instr, 'price': 0.985*param['price'], 'volume': vol, 'side': 'bid'})
                            print("Placing order: volume %d price %.2f" %(vol, param['price']))

        else:
            print("Stopping all trading activity. Losses are too large. PnL: %.2f" %(self.rm.curr_to_prev_pnl_fraction()))
            for instr in self.instruments:
                self.exchange.delete_orders(instr)
            self.exchange.disconnect()



if __name__ == "__main__":
    # Connect to exchange and run
    exchange = Exchange()
    algo = AlgoPassive(exchange, instruments)
    algo.run()
