import numpy as np
import datetime
import time 

MAX_ORDER_MUTATIONS_PER_SECOND = 24
MAX_POSITION_PER_INSTRUMENT = 500
MAX_TOTAL_POSITION = 500


class RiskManagement:
    
    def __init__(self, exchange, instr_list):
        self.exchange = exchange
        # tracking number of units per instrument that we own
        self.positions = {} # { instrument: position }
        for instr in instr_list:
            self.positions[instr] = 0 
        # track pending orders including price, id, volume
        self.orders_bid = {} # {instrument : { order_id : {price: , volume: }} }
        self.orders_ask = {} # {instrument : { order_id : {price: , volume: }} }
        for instr in instr_list:
            self.orders_bid[instr] = {}
            self.orders_ask[instr] = {}
        # tracking frequency of order mutations we are submitting
        self.last_timestamps = []
        # Track profit and loss
        self.previous_pnl = 1.0
    
    def update_position(self, instr, quantity):
        self.positions[instr] += quantity

    def get_delta(self):
        delta = 0
        for instr, pos in self.positions.items():
            delta += pos
        return delta
       
    def reset_outstanding_orders(self):
        for k, v in self.orders_bid.items():
            self.orders_bid[k] = {}
        for k, v in self.orders_ask.items():
            self.orders_ask[k] = {}  
        
    def update_oustanding_orders(self, outstanding):
        # Process information from the exchange venue
        for o in outstanding.values():
            if o.side == 'ask': # ask
                self.orders_ask[o.instrument_id][o.order_id] = {'price': o.price, 'volume': o.volume}
            elif o.side == 'bid': # bid
                self.orders_bid[o.instrument_id][o.order_id] = {'price': o.price, 'volume': o.volume}
            else:
                print("Side unclear.")
                
    def update_new_trades(self):
        for instr in self.positions.keys():
            trades = self.exchange.poll_new_trades(instr)
            # Process information from the exchange venue: incremental update to trades
            for t in trades:
                if t.side == 'ask':
                    self.positions[t.instrument_id] -= t.volume
                elif t.side == 'bid':
                    self.positions[t.instrument_id] += t.volume
                else:
                    raise Exception("Invalid trade received, side cannot be identified.")
            # update outstanding orders as well
            self.update_oustanding_orders(self.exchange.get_outstanding_orders(instr))
            self.update_position(instr, self.exchange.get_positions()[instr])
        
    def get_pending_exposure(self, instr, side):
        pos = 0
        if side == 'bid':
            for id, order in self.orders_bid[instr].items():
                pos += order['volume']
        if side == 'ask':
            for id, order in self.orders_ask[instr].items():
                pos -= order['volume']
        return pos
    
    def get_max_trade_size(self, instr, side):
        # return positions + pending orders
        allowance = MAX_POSITION_PER_INSTRUMENT
        # re-do this function @Quincy 
        if side == 'ask': # selling
            net_position = self.positions[instr] - self.get_pending_exposure(instr, side)  # position + pending orders in the market
            allowance = MAX_POSITION_PER_INSTRUMENT + net_position
            allowance = min(np.abs(allowance), np.abs(MAX_POSITION_PER_INSTRUMENT - net_position))
            allowance = min(allowance, np.abs(MAX_TOTAL_POSITION - self.positions[instr]))
        elif side == 'bid': # buying
            net_position = self.positions[instr] + self.get_pending_exposure(instr, side)
            print("Net position: ", net_position)
            allowance = MAX_POSITION_PER_INSTRUMENT - net_position
            allowance = min(np.abs(allowance), np.abs(MAX_POSITION_PER_INSTRUMENT - net_position))
            print("92 allowance: ", allowance)
            allowance = min(allowance, MAX_TOTAL_POSITION + self.positions[instr])
            print("Final allowance: ", allowance)
        else:
             print("Looking for side: ", side)
             raise Exception("Invalid side received, side cannot be identified.")
        allowance = int(min(abs(allowance), 25))
        print("Allowing %d trade units" %(allowance))
        return allowance
    
    def count_active_order_mutation(self):
        self.last_timestamps.append(datetime.datetime.now())
        if len(self.last_timestamps) > MAX_ORDER_MUTATIONS_PER_SECOND:
            new_last_timestamps = self.last_timestamps[-MAX_ORDER_MUTATIONS_PER_SECOND:]
            sleep_time = (datetime.datetime.now()-new_last_timestamps[0]).total_seconds()
            #print("Entering sleep for: ", sleep_time)
            #time.sleep(sleep_time)
            self.last_timestamps = new_last_timestamps

    def allowed_to_mutate_orders(self):
        if (len(self.last_timestamps) < 1):
            return True
        elif (datetime.datetime.now() - self.last_timestamps[0] > datetime.timedelta(seconds=1.2)):
            return True
        else:
            return False
        
    def archive_order_to_market(self, order_dict): # {instrument :, order_id : , price: , volume: , side:}
        # internally track state of our pending orders
        self.count_active_order_mutation()
        if order_dict['side'] == 'ask':
            self.orders_ask[order_dict['instrument']][order_dict['order_id']] = {'price': order_dict['price'], 'volume': order_dict['volume']} 
        elif order_dict['side'] == 'bid':
            self.orders_bid[order_dict['instrument']][order_dict['order_id']] = {'price': order_dict['price'], 'volume': order_dict['volume']} 

    def curr_to_prev_pnl_fraction(self):
        prev_pnl = self.previous_pnl
        self.previous_pnl = self.exchange.get_pnl()
        if self.exchange.get_pnl() is None or self.previous_pnl is None:
            return 1.0 
        else:
            if (prev_pnl > 0.0):
                return (prev_pnl / self.previous_pnl)
            else:
                return (self.previous_pnl / prev_pnl )
        