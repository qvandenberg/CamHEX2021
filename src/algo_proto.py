from optibook.synchronous_client import Exchange
import logging
from datetime import datetime as dt
import time

from pricebooks import LatestPriceBook
from OutstandingOrders import OutstandingOrders
from CurrentPositions import CurrentPositions

logger = logging.getLogger('client')
logger.setLevel('ERROR')

print("Setup was successful.")

# Settings
instruments = ['PHILIPS_A', 'PHILIPS_B']
MAX_TRADE_QUANTITY = 1
MAX_TRADE_FREQUENCY = 25
SPREAD_THRESHOLD = 0.2

# Connect to exchange and run
e = Exchange()
a = e.connect()

# Storage containers for price books, outstanding orders
pb = LatestPriceBook(instruments)
oo = OutstandingOrders(instruments)
cp = CurrentPositions(instruments)

timestamps = []
trade_quantity = 0

while (quantity < MAX_TRADE_QUANTITY): # risk condition
    for instr in instruments:
        # Download latest market information and outstanding orders
        pb.refresh_price_book(e.get_last_price_book(instr))
        oo.update_oustanding_orders(e.get_outstanding_orders(instr))


        if ((timestamps[0] - dt.now()) < dt.timedelta(seconds=1) or len(timestamps)<MAX_TRADE_FREQUENCY):
            # trade
            bid_A, bid_B = pb.instruments["PHILIPS_A"]['best_bid'], pb.instruments["PHILIPS_B"]['best_bid']
            ask_A, ask_B = pb.instruments["PHILIPS_A"]['best_ask'], pb.instruments["PHILIPS_B"]['best_ask']
            mid_A, mid_B = pb.instruments["PHILIPS_A"]['weighted_mid'], pb.instruments["PHILIPS_B"]['weighted_mid']

            if (mid_A > mid_B and ( ask_A - bid_B > 2. * SPREAD_THRESHOLD)):
                # buy B, sell at A
                result = e.insert_order("PHILIPS_B", price=bid_B + SPREAD_THRESHOLD, volume=1, side='bid', order_type='limit')
                result = e.insert_order("PHILIPS_A", price=ask_A - SPREAD_THRESHOLD, volume=1, side='ask', order_type='limit')

                # cp.add_transaction("PHILIPS_A", -1)
                # cp.add_transaction("PHILIPS_B", 1)

                timestamps.append(dt.now())
                timestamps.append(dt.now())
                trade_quantity += 1
            if (mid_A < mid_B and ( ask_B - bid_A > 2. * SPREAD_THRESHOLD)):
                # buy A, sell at B
                result = e.insert_order("PHILIPS_B", price=ask_B - SPREAD_THRESHOLD, volume=1, side='ask', order_type='limit')
                result = e.insert_order("PHILIPS_A", price=bid_A + SPREAD_THRESHOLD, volume=1, side='bid', order_type='limit')

                timestamps.append(dt.now())
                timestamps.append(dt.now())
                trade_quantity += 1

        else:
            # Sleep
            remaining_time = dt.timedelta(seconds=1) - (timestamps[0] - dt.now())
            time.sleep(remaining_time)





        # Trade and archive transactions

        # Each transaction: cp.add_transaction(instr, quantity)

        # Update risk metrics

'''
Strategy 1 - Scalping

First – calculate bid_volume and ask_volume
Two entry conditions
Which is higher ( bid or ask volume) – say bid
In the past 1 minutes if bid volume has been increasing
If both yes, we enter 3 limit orders simultaneously
Buy order at current market price
Sell order  3 ticks higher than buy order [ target price]
Sell order  5 ticks lower than sell order [ stop loss]
Whenever TP or SL gets hit, cancel the other one and book the profit

#strategy 1 - basic scalping
        # Decide whether to trade or not
        if(pb.get_bid_volume() > pb.get_ask_volume):
            price_level = pb.get_best_bid_price()
            stop_loss =  price_level - 0.5 # (5 ticks below)
            target_price = price_level + 0.2 # (2 ticks above)

            result_1 = e.insert_order(instrument_id, price=pb.get_b, volume= quantity, side='bid', order_type='limit')
            #if above transaction executed, place two more orders
                result_2 = e.insert_order(instrument_id, price=stop_loss, volume= quantity, side='ask', order_type='limit')
                result_3 = e.insert_order(instrument_id, price=target_price, volume= quantity, side='ask', order_type='limit')
                #if any o above two orders ( TP or SL executed, cancel the other order)
                if (result_2 == True):
                    cancel (result_3)
                else:
                    cancel (result_2)
'''
'''
Strategy 2 - Exchange arbitrage

count = 0

if count >20 :  wait it till it comes down , then reset
else:
    if delta >= 450 ; dont do anything
    else:

check bid prices at exchange 1 (bid_1) and 2(bid_2)
check ask prices at exchange 1 (ask_1) and 2(ask_2)

if bid_1 + 0.2 >= bid_2
    buy at bid_1, sell at bid_2
    count = count + 2

elif bid_2 + 0.2 >= bid_1 :
    sell at bid_2, buy at bid_1
    count+=2

elif ask_1 > ask_2 + 0.2 :
    sell at ask_1, buy at ask_2
    count+=2

elif ask_2 > ask_1 + 0.2 :
    sell at ask_2, buy at ask_1
    count+=2

'''
'''
risk management

in addition to limits from optiver, to further improve risk management, we mplement two algorithms
1st Stoploss - can use rolling stoploss ( keeping storing pnl, if current_pnl < 0.9*previous_pnl, halt the algorithm )
2nd Delta Hedging - If the delta increases beyond (say 200), execute quantity/2, immediate limit orders one tick above/below to reduce it to 50. sell order would go at ask/mid price  -0.1

'''





# if __name__ == "__main__":






# {
#     Philips_A : {
#         best_bid: ,
#         best_ask: ,
#         bid_volume: ,
#         ask_volume: ,
#         ask_bid_spread: ,
#         volume_weighted_ask: ,

#     },
#     Philips_B : {
#         best_bid: ,
#         best_ask: ,
#         bid_volume: ,
#         ask_volume:
#     }
# }
