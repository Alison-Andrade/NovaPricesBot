class Item:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.orders = []

    # def set_refine(self, refine):
    #     self.orders['refine'] = refine

    # def set_enchant(self, enchant):
    #     self.enchant.append(enchant)

    def __str__(self):
        return f'Name: {self.name} Id: {self.id}'
