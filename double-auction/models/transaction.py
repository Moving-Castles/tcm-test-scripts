from .offer import *
from constants.offer_type import *
from constants.materials import *
import json

class Transaction(object):
    
    tx_id = 0
    tx_price = None
    
    def __init__(self):
        self.tx_id = Transaction.tx_id
        Transaction.tx_id +=  1
        
    def addTransaction(self, offer: Offer, found_offer: Offer, volume: int):
        self.tx_price = found_offer.item_price
        self.material = found_offer.item_id
        self.volume = volume

    def asString(self):
        return "tx_id", self.tx_id, "tx_price", self.tx_price,  "material", self.material.name, "volume", self.volume

    def asDict(self):
        return {
            "tx_id": self.tx_id, 
            "tx_price": self.tx_price, 
            "material": self.material.name, 
            "volume": self.volume
        }
