import datetime
from datetime import datetime as dt
import numpy as np
from itertools import filterfalse

MAX_TICK_LIFETIME = 10 # seconds
'''
The TradeHistory acts as a source of truth as to what the price of each instrument is.
Price books have shown to be unreliable, so the recent trade history is what we use to
judge whether an ask or a bid is underpriced or overpriced. With time, previous trades
gradually lose their value so we compute an average volume-weighted price over the trades in the last MAX_TICK_LIFETIME
seconds.

Optionally, it can be a weighted average with a decay function to give the most recent trade ticks
a higher importance.
'''
class TradeHistory:

    def __init__(self, exchange, instr_list):
        self.exchange = exchange
        self.last_trade_nr = None
        self.instruments = {} # {instrument : { 'ticks': [ { timestamp : , price: , volume: } ] , 'real_price' : }
        for instr in instr_list:
            self.instruments[instr] = { 'ticks': [], 'real_price': None }

    def reset_tradeticks(self, instr):
        self.instruments[instr]['ticks'] = []

    def poll_new_trade_ticks(self):
        for instr in self.instruments.keys():
            tradeticks = self.exchange.poll_new_trade_ticks(instr)
            for t in tradeticks:
                if (self.last_trade_nr != t.trade_nr - 1):
                    pass
                    #print("Warning: We missed a trade! Previous: Current ", t.trade_nr, self.last_trade_nr)
                self.last_trade_nr = t.trade_nr
                tick = {'timestamp': t.timestamp, 'price': t.price, 'volume': t.volume}
                self.instruments[t.instrument_id]['ticks'].append(tick)
            self.purge_expired_trades()
            self.compute_real_price()

    def purge_expired_trades(self):
        # Remove all trades older than MAX_TICK_LIFETIME
        time_now = dt.now()
        for instr in self.instruments.keys():
            self.instruments[instr]['ticks'] = [tick for tick in self.instruments[instr]['ticks'] if not self.is_expired(time_now, tick['timestamp'])]
            # self.instruments[instr]['ticks'][:] = [tick for tick in self.instruments[instr]['ticks'] if not self.is_expired(time_now, tick['timestamp'])]

    def is_expired(self, time_now, timestamp): # (datetime.datetime obj, datetime string)
        # ts = dt.strptime(timestamp, '%Y-%M-%S %H:%M:%S')
        if (time_now - timestamp ) > datetime.timedelta(seconds = MAX_TICK_LIFETIME):
            return True
        else:
            return False

    def compute_real_price(self): # volume-weighted, equal weights w.r.t. timestamp
        for instr, param in self.instruments.items():
            if len(param['ticks']) == 0:
                self.instruments[instr]['real_price'] = None
            else:
                volume_price_sum = 0.0
                trade_volume = 0.0
                for tick in param['ticks']:
                    volume_price_sum += tick['price'] * tick['volume']
                    trade_volume += tick['volume']
                self.instruments[instr]['real_price'] = volume_price_sum/trade_volume

    def get_real_price(self, instr):
        #print("Get real price: ", self.instruments[instr]['real_price'])
        return self.instruments[instr]['real_price']
