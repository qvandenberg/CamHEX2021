
class LatestPriceBook:

    def __init__(self, instr_list):
        self.instruments = {} # { instrument : {timestamp: , best_bid: , best_ask: , bid_volume: , ask_volume: , spread: , weighted_mid }
        # e.g. access properties through self.instruments["PHILIPS_A"]["spread"]
        for instr in instr_list:
            self.instruments[instr] = {}

    def reset_pricebook(self, pricebook):
         self.instruments[pricebook.instrument_id]['bid_volume'] = 0
         self.instruments[pricebook.instrument_id]['ask_volume'] = 0
         self.instruments[pricebook.instrument_id]['weighted_mid'] = 0

    def refresh_price_book(self, pricebook):
        self.reset_pricebook(pricebook)
        self.instruments[pricebook.instrument_id]['timestamp'] = pricebook.timestamp

        for bid in pricebook.bids:
            self.instruments[pricebook.instrument_id]['bid_volume'] += bid.volume
            self.instruments[pricebook.instrument_id]['weighted_mid'] += bid.volume * bid.price
        for ask in pricebook.asks:
            self.instruments[pricebook.instrument_id]['ask_volume'] += ask.volume
            self.instruments[pricebook.instrument_id]['weighted_mid'] += bid.volume * bid.price
        self.instruments[pricebook.instrument_id]['weighted_mid'] /= self.instruments[pricebook.instrument_id]['ask_volume'] + self.instruments[pricebook.instrument_id]['bid_volume']
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

        print("Updated pricebook at timestamp: ", pricebook.timestamp)
        print("Best ask, bid, ask volume, bid volume: ", self.instruments[pricebook.instrument_id]['best_ask'], self.instruments[pricebook.instrument_id]['best_bid'], self.instruments[pricebook.instrument_id]['ask_volume'], self.instruments[pricebook.instrument_id]['bid_volume'])


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

# pricebook = e.get_last_price_book(instrument_id)
# print("Timestamp: ", pricebook.timestamp)
# bids = pricebook.bids # people buying, the price they offer
# for bid in bids:
#     print("Bid price: %.2f volume: %d" %(bid.price, bid.volume))

# asks = pricebook.asks # people selling, the price they want
# for ask in asks:
#     print("Ask price: %.2f volume: %d" %(ask.price, ask.volume))
