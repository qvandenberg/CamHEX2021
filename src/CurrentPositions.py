
class CurrentPositions:

    def __init__(self, instr_list):
        self.delta = 0
        self.volumes = {}
        for instr in instr_list:
            self.volumes[instr] = 0

    def add_transaction(self, instr, quantity):
        self.volumes[instr] += quantity

    def get_delta(self):
        return self.delta

 
