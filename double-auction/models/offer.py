from constants.offer_type import * 
from .player import *

class Offer:
    offer_id = 0
    offer_type = -1
    item_id = -1
    item_price = -1
    
    def __init__(self):
        self.offer_id = Offer.offer_id
        Offer.offer_id +=  1
        
    def setOfferDetails(self, offer_type: OfferType, item_id, item_price: int, proposer: Player, volume: int):
        self.offer_type = offer_type
        self.item_id = item_id
        self.item_price = item_price
        self.proposer = proposer
        self.volume = volume

    def getAsString(self) -> str:
        return "OfferID:", self.offer_id, "offer type:", self.offer_type, "itemID:", self.item_id, "item price:", self.item_price

    def asDict(self) -> dict:
        return {
            "offer_id": self.offer_id,
            "offer_type": self.offer_type,
            "item_id": self.item_id.name,
            "item_price": self.item_price,
            "volume": self.volume
        }

