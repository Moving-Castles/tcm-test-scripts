from constants.offer_type import * 
from .player import *
import datetime

class Offer:
    offer_id = 0
    offer_type = -1
    material = -1
    unit_price = -1
    
    def __init__(self):
        self.offer_id = Offer.offer_id
        Offer.offer_id +=  1
        
    def setOfferDetails(self, offer_type: OfferType, material, unit_price: int, volume: int, proposer: Player):
        self.offer_type = offer_type
        self.material = material
        self.unit_price = unit_price
        self.proposer = proposer
        self.volume = volume
        self.timestamp = datetime.datetime.now()

    def getAsString(self) -> str:
        return "OfferID:", self.offer_id, "offer type:", self.offer_type, "itemID:", self.material, "item price:", self.unit_price

    def asDict(self) -> dict:
        return {
            "offer_id": self.offer_id,
            "offer_type": self.offer_type.name,
            "material": self.material.name,
            "unit_price": self.unit_price,
            "volume": self.volume,
            "timestamp": self.timestamp
        }

