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
        self.all_ids = []
        
        for id in Materials:
            self.all_ids.append(id)
        
        # sort buy and sell offers by material type
        self.buy_offers = dict({m: [] for m in self.all_ids})
        self.sell_offers = dict({m: [] for m in self.all_ids})
        self.guide_prices = dict({m: {"volume": 0, "price": 0} for m in self.all_ids})

    def marketPrices(self):
        print('prices')
        # todo: window by timestamp
        for material in self.all_ids:
            cumulative_price = 0
            volume = 0
            guide_price = 0
            filtered_txs = [tx for tx in self.completed_transactions if tx.material == material]
            for tx in filtered_txs:
                cumulative_price += tx.tx_price * tx.volume
                volume += tx.volume
            
            if volume != 0: 
                guide_price = cumulative_price/volume

            self.guide_prices[material] = {"volume": volume, "price": guide_price}
                
        return self.guide_prices


    def addOffer(self, offer: Offer):
        self.handleOffer(offer)
        self.formatPrintCompletedTransactions()

    def handleOffer(self, offer: Offer):
        volume = 0
        found_offer = None
        offer_complete = False

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
                        offer_complete = True

                    # if they are selling more than the bidder wants, keep the offer on the market
                    elif found_offer.volume > offer.volume:
                        volume = offer.volume
                        found_offer.volume = found_offer.volume - offer.volume
                        offer_complete = True

                    # if found offer is selling less than the bidder wants, sell that much and remove it
                    else:
                        volume = found_offer.volume
                        offer.volume = offer.volume - found_offer.volume
                        offers[:] = [o for o in offers if o.offer_id != found_offer.offer_id]

                if found_offer:
                    transaction = Transaction()
                    transaction.addTransaction(offer, found_offer, volume)
                    self.completed_transactions.append(transaction)
                    found_offer = None

                if offer_complete: break

            if not offer_complete: 
                self.buy_offers[offer.item_id].append(offer)


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
                        offer_complete = True

                    # if they are selling more than the bidder wants, sell that amount and add to market, remove the bid
                    elif found_offer.volume < offer.volume:
                        volume = found_offer.volume
                        offer.volume = offer.volume - found_offer.volume
                        offers[:] = [o for o in offers if o.offer_id != found_offer.offer_id]

                    # if they are selling less than the bidder wants, complete the bid
                    else:
                        volume = offer.volume
                        found_offer.volume = found_offer.volume - offer.volume
                        offer_complete = True

                if found_offer:
                    transaction = Transaction()
                    transaction.addTransaction(offer, found_offer, volume)
                    self.completed_transactions.append(transaction)
                    found_offer = None
                
                if offer_complete: break

            if not offer_complete: 
                self.sell_offers[offer.item_id].append(offer)

            
    def formatPrintCompletedTransactions(self):
        print("\nCompleted Transactions:")
        for transaction in self.completed_transactions:
            print(transaction.asString())
        print()


    def txToJSON(self):
        print([tx.asDict() for tx in self.completed_transactions])
        return [tx.asDict() for tx in self.completed_transactions]