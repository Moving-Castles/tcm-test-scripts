from .offer import *
from constants.offer_type import *
from constants.materials import *
import json
import datetime

class Transaction(object):
    
    tx_id = 0
    tx_price = None
    
    def __init__(self):
        self.tx_id = Transaction.tx_id
        Transaction.tx_id +=  1
        
    def addTransaction(self, offer: Offer, found_offer: Offer, volume: int):
        self.tx_price = found_offer.unit_price
        self.material = found_offer.material
        self.volume = volume
        self.type = offer.offer_type
        self.timestamp = datetime.datetime.now()

        offer_cost = offer.unit_price*volume
        actual_cost = found_offer.unit_price*volume

        if offer.offer_type == OfferType.BUY:
            self.buyer = offer.proposer
            self.seller = found_offer.proposer
            self.buyer.points += offer_cost - actual_cost
        else:
            self.buyer = found_offer.proposer
            self.seller = offer.proposer

        self.seller.points += actual_cost
        self.buyer.materials[found_offer.material.name] += volume
        
        print('buyer gets', offer_cost-actual_cost)
        
        print('seller gets', actual_cost)

    def asString(self) -> str:
        return "tx_id", self.tx_id, "tx_price", self.tx_price,  "material", self.material.name, "volume", self.volume

    def asDict(self) -> dict:
        return {
            "tx_id": self.tx_id, 
            "tx_price": self.tx_price, 
            "material": self.material.name, 
            "volume": self.volume,
            "timestamp": self.timestamp
        }
