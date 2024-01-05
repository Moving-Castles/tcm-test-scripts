from constants.offer_type import * 
from .player import *

class Offer:
    """Definition of an Offer
    """
    offer_id = 0
    offer_type = -1
    item_id = -1
    item_price = -1
    
    def __init__(self):
        self.offer_id = Offer.offer_id
        Offer.offer_id +=  1
        

    def setOfferDetails(self, offer_type: OfferType, item_id, item_price: int, proposer: Player):
        """Assign values to the Offer

        Args:
            offer_type (Enum): Type of Offer
            item_id (int): ID of the Item
            item_price (int): Price of the Item
        """
        self.offer_type = offer_type
        self.item_id = item_id
        self.item_price = item_price
        self.proposer = proposer

    def getAsString(self) -> str:
        return "OfferID:", self.offer_id, "offer type:", self.offer_type, "itemID:", self.item_id, "item price:", self.item_price