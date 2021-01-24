from optibook.synchronous_client import Exchange

class LatestPriceBook:
    
    def __init__(self, exchange, instr_list):
        self.exchange = exchange
        self.instruments = {} # { instrument : {timestamp: , best_bid: , best_ask: , best_bid_volume, best_ask_volume, bid_volume: , ask_volume: , spread: , weighted_mid: }
        # e.g. access properties through self.instruments["PHILIPS_A"]["spread"]
        for instr in instr_list:
            self.instruments[instr] = {}
        
    def reset_pricebook(self, pricebook):
         self.instruments[pricebook.instrument_id]['bid_volume'] = 0
         self.instruments[pricebook.instrument_id]['ask_volume'] = 0
         self.instruments[pricebook.instrument_id]['weighted_mid'] = 0.0
         
    def refresh_price_book(self):
        for instr in self.instruments:
            pricebook = self.exchange.get_last_price_book(instr)
            self.reset_pricebook(pricebook)
            self.instruments[pricebook.instrument_id]['timestamp'] = pricebook.timestamp
            self.instruments[pricebook.instrument_id]['best_bid_volume'] = pricebook.bids[0].volume if len(pricebook.bids)>0 else 0.0
            self.instruments[pricebook.instrument_id]['best_ask_volume'] = pricebook.asks[0].volume if len(pricebook.asks)>0 else 0.0

            for bid in pricebook.bids:
                self.instruments[pricebook.instrument_id]['bid_volume'] += bid.volume
                self.instruments[pricebook.instrument_id]['weighted_mid'] += bid.volume * bid.price
            for ask in pricebook.asks:
                self.instruments[pricebook.instrument_id]['ask_volume'] += ask.volume
                self.instruments[pricebook.instrument_id]['weighted_mid'] += ask.volume * ask.price
            total_vol = self.instruments[pricebook.instrument_id]['ask_volume'] + self.instruments[pricebook.instrument_id]['bid_volume']
            if (total_vol > 0): self.instruments[pricebook.instrument_id]['weighted_mid'] /= total_vol
            
            if len(pricebook.bids) > 0:
                self.instruments[pricebook.instrument_id]['best_bid'] = pricebook.bids[0].price
            else:
                self.instruments[pricebook.instrument_id]['best_bid'] = None
            
            if len(pricebook.asks) > 0:
                self.instruments[pricebook.instrument_id]['best_ask'] = pricebook.asks[0].price
            else:
                self.instruments[pricebook.instrument_id]['best_ask'] = None
              
            if (self.instruments[pricebook.instrument_id]['best_ask'] is not None and self.instruments[pricebook.instrument_id]['best_bid'] is not None):
                self.instruments[pricebook.instrument_id]['spread'] = self.instruments[pricebook.instrument_id]['best_ask'] -  self.instruments[pricebook.instrument_id]['best_bid']
            
            #print("Updated pricebook at timestamp: ", pricebook.timestamp)
            #print("Best ask, bid, ask volume, bid volume: ", self.instruments[pricebook.instrument_id]['best_ask'], self.instruments[pricebook.instrument_id]['best_bid'], self.instruments[pricebook.instrument_id]['ask_volume'], self.instruments[pricebook.instrument_id]['bid_volume'])

    def get_best_ask_price_volume(self, instr): # best ask price, total ask volume
        return self.instruments[instr]['best_ask'], self.instruments[instr]['ask_volume']
    
    def get_best_bid_price_volume(self, instr): # best bid price, total bid volume
        return self.instruments[instr]['bid_volume'], self.instruments[instr]['bid_volume']
    
    