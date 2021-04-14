class Order:

    def __init__(self, price, location, qty):
        self.price = price
        self.location = location
        self.qty = qty

    def set_refine(self, refine):
        self.refine = refine

    def set_enchant(self, enchant):
        self.enchant.append(enchant)

    def __lt__(self, other):
        if self.price < other.price:
            return True
        return False

    def __gt__(self, other):
        if self.price > other.price:
            return True
        return False

    def __le__(self, other):
        if self.price <= other.price:
            return True
        return False

    def __ge__(self, other):
        if self.price >= other.price:
            return True
        return False

    def __eq__(self, other):
        if self.price == other.price:
            return True
        return False

    def __str__(self):
        return f'Price: {self.price} Qty: {self.qty} Location: {self.location}'
