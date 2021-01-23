
class OutstandingOrders:

    def __init__(self, instr_list):
        self.orders_bid = {} # {instrument : { order_id : {price: , volume: }} }
        self.orders_ask = {} # {instrument : { order_id : {price: , volume: }} }
        for instr in instr_list:
            self.orders_bid[instr] = {}
            self.orders_ask[instr] = {}

    def reset_outstanding_orders(self):
        for k, v in self.orders_bid.items():
            self.orders_bid[k] = {}
        for k, v in self.orders_ask.items():
            self.orders_ask[k] = {}

    def update_oustanding_orders(self, outstanding):
        for o in outstanding.values():
            if o.side == 'ask': # ask
                self.orders_ask[o.instrument_id][o.order_id] = {'price': o.price, 'volume': o.volume}
            elif o.side == 'bid': # bid
                self.orders_bid[o.instrument_id][o.order_id] = {'price': o.price, 'volume': o.volume}
            else:
                print("Side unclear.")


 
