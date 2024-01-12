from .offer import *
from .transaction import *
from constants.offer_type import *
from constants.materials import *
import copy

class Listing:
    
    buy_offers = dict()
    sell_offers = dict()
    completed_transactions: list[Transaction] = []
    
    def __init__(self) -> None:        
        all_ids = []
        
        for id in Materials:
            all_ids.append(id)
        
        # sort buy and sell offers by material type
        self.buy_offers = dict({k: [] for k in all_ids})
        self.sell_offers = dict({k: [] for k in all_ids})


    def marketPrices(self):
        print('prices')
    
    def addOffer(self, offer: Offer):
        self.handleOffer(offer)
        self.formatPrintCompletedTransactions()

    def handleOffer(self, offer: Offer):
        found_offer = None
        volume = 0

        if offer.offer_type == OfferType.BUY:
            # filter sell offers and order according to price, lowest first, then by date
            offers = self.sell_offers[offer.item_id]
            sorted_offers = sorted(offers, key=lambda o: o.item_price)
            for sell_offer in sorted_offers:
                if offer.item_price >= sell_offer.item_price:
                    found_offer = sell_offer
                    if found_offer.volume == offer.volume:
                        volume = offer.volume
                        offers[:] = [o for o in offers if o.offer_id != found_offer.offer_id]

                    # if they are selling more than the bidder wants, keep the offer on the market
                    elif found_offer.volume > offer.volume:
                        volume = offer.volume
                        found_offer.volume = found_offer.volume - offer.volume

                    # if they are selling less than the bidder wants sell that amount and add the bid
                    else:
                        volume = found_offer.volume
                        offer.volume = offer.volume - found_offer.volume
                        self.buy_offers[offer.item_id].append(offer)
                        offers[:] = [o for o in offers if o.offer_id != found_offer.offer_id]
                        break

            if found_offer == None:
                print('no matching offer')
                self.buy_offers[offer.item_id].append(offer)
                return

        elif offer.offer_type == OfferType.SELL:
            # filter buy offers and order according to price, highest first, then by date
            offers = self.buy_offers[offer.item_id]
            sorted_offers = sorted(offers, key=lambda o: o.item_price, reverse=True)
            
            for buy_offer in sorted_offers:
                if offer.item_price <= buy_offer.item_price:
                    found_offer = buy_offer
                    if found_offer.volume == offer.volume:
                        volume = offer.volume
                        offers[:] = [o for o in offers if o.offer_id != found_offer.offer_id]

                    # if they are selling more than the bidder wants, sell that amount and add to market, remove the bid
                    elif found_offer.volume < offer.volume:
                        volume = found_offer.volume
                        offer.volume = offer.volume - found_offer.volume
                        self.sell_offers[offer.item_id].append(offer)
                        offers[:] = [o for o in offers if o.offer_id != found_offer.offer_id]

                    # if they are selling less than the bidder wants, 
                    else:
                        volume = offer.volume
                        found_offer.volume = found_offer.volume - offer.volume
                        break

            if found_offer == None:
                print('no matching offer')
                self.sell_offers[offer.item_id].append(offer)
                return

        transaction = Transaction()
        transaction.addTransaction(offer, found_offer, volume)
        self.completed_transactions.append(transaction)

            
    def formatPrintCompletedTransactions(self):
        print("\nCompleted Transactions:")
        for transaction in self.completed_transactions:
            print(transaction.asString())
        print()


    def txToJSON(self):
        print([tx.asDict() for tx in self.completed_transactions])
        return [tx.asDict() for tx in self.completed_transactions]