from .offer import *
from constants.offer_type import *

class Transaction:
    
    transaction_id = 0
    transaction_price = None
    buy_offer_id = None
    sell_offer_id = None

    
    def __init__(self):
        self.transaction_id = Transaction.transaction_id
        Transaction.transaction_id +=  1

        
    def addTransaction(self, buy_offer: Offer, sell_offer: Offer):
        self.transaction_price = sell_offer.item_price
        self.buy_offer_id      = buy_offer.offer_id
        self.sell_offer_id     = sell_offer.offer_id
        
        
    def addTransactionByDeterminingOfferType(self, offer_1: Offer, offer_2: Offer):
        if (offer_1.offer_type == OfferType.BUY):
            self.addTransaction(offer_1, offer_2)
        else:
            self.addTransaction(offer_2, offer_1)
    
    def getAsString(self) -> str:
        return "Transaction ID:", self.transaction_id, "Transaction Price:", self.transaction_price, "Buy Offer ID:",\ 
        self.buy_offer_id, "Sell Offer ID:", self.sell_offer_id