from .offer import *
from .transaction import *
from constants.offer_type import *
from constants.materials import *

class Listing:
    
    buy_offers = dict()
    sell_offers = dict()
    completed_transactions: list[Transaction] = []
    
    def __init__(self) -> None:
        """Initialise all dictionaries for offer lists
        """
        
        # avoid same reference issue by initialising each one with its own list
        # TODO: how to we deep clone?
        
        all_ids1 = []
        all_ids2 = []
        
        for id in ItemIds:
            all_ids1.append((id, dict()))
            all_ids2.append((id, dict()))
        
        self.buy_offers            = dict(all_ids1)
        self.sell_offers           = dict(all_ids2)
        
    
    def addOffer(self, offer: Offer):
        """[summary]

        Args:
            offer (Offer): Offer to add
        """
        #TODO: check if the offer will complete any offer, otherwise, add it to the listing
        
        if (offer.offer_type == OfferType.BUY):
            self.handleAnyOffer(offer, self.buy_offers, self.sell_offers, True)
        elif (offer.offer_type == OfferType.SELL):
            self.handleAnyOffer(offer, self.sell_offers, self.buy_offers, False)
            
        print('buy_offers', self.buy_offers)
        print('sell_offers', self.sell_offers)
        self.formatPrintCompletedTransactions()
        print()
        
        
    # TODO: maybe we can be smart and just use one for optimisation 
    #
            # self.handleBuyOffer(offer, self.sell_offers, self.buy_offers)
    def handleAnyOffer(self, offer: Offer, offer_dict_1, offer_dict_2, is_buy_offer):
        """[summary]

        Args:
            offer (Offer): [description]
            offer_dict_1 ([type]): [description]
            offer_dict_2 ([type]): [description]
            reverse ([type]): [description]
        """
        
        offer_keys = list(offer_dict_2[offer.item_id].keys())
        # offer_keys.sort(reverse=is_buy_offer) 
        # look at note in DoubleAuction: if we remove this, then buy offers will always look for lowest seller and work their way up
        
        found_offer_price = None
        
        print("offer_keys", offer_keys)
        
        for offer_prices in offer_keys:
            if is_buy_offer == True and offer_prices > offer.item_price:
                continue
            elif is_buy_offer == False and offer_prices < offer.item_price:
                continue
            else:
                found_offer_price = offer_prices
                break
        
        
        print("found_offer_price", found_offer_price)
        
        if (found_offer_price != None):
            
            # remove the offer and add it to completed offers
            found_offer: Offer = offer_dict_2[offer.item_id][found_offer_price].pop()
            
            # if key list is empty, we delete it
            if (len(offer_dict_2[offer.item_id][found_offer_price]) == 0):
                offer_dict_2[offer.item_id].pop(found_offer_price)
                
            transaction = Transaction()
            transaction.addTransactionByDeterminingOfferType(offer, found_offer)
            self.completed_transactions.append(transaction)
            
        else:
            # if can't complete an offer, then we put it into the dictionary to wait for an applicable offer
            
            if offer.item_price in offer_dict_1[offer.item_id]:
                offer_dict_1[offer.item_id][offer.item_price] += [offer]
            else:
                offer_dict_1[offer.item_id][offer.item_price] = [offer]

            
    def formatPrintCompletedTransactions(self):
        print("\nCompleted Transactions:")
        for transaction in self.completed_transactions:
            print(transaction.getAsString())
        print()