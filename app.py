from itertools import chain, groupby, combinations
import random

class Match:
    def __init__(self):
        self.p1 = Player('Player 1')
        self.p2 = Player('Player 2')
        self.players = [self.p1,self.p2]
        self.roundsplayed = 0
        self.currentround = None
        
    def __repr__(self):
        return str('Match started')
        
    def playmatch(self):
        while (self.p1.points < 11 and self.p2.points < 11):
            print('playing round: ',self.roundsplayed + 1)
            self.playround()
    
    def playround(self):
        self.roundsplayed += 1
        self.currentround = Round(self.createdeck(), self.players)

    def createdeck(self):
        suits = ['Bastoni','Denari','Spade','Coppe']
        ranks = [(7, 21),
            (6, 18),
            (1, 16),
            (5, 15),
            (4, 14),
            (3, 13),
            (2, 12),
            (8, 10),
            (9, 10),
            (10, 10)
            ]
        deck = [Card((a,b)) for a in suits for b in ranks]
        random.shuffle(deck)
        return deck
        
class Round:
    def __init__(self, deck, players):
        self.deck = deck
        self.lastwinner = None
        self.board = [] 
        self.players = players    
        self.resetcounts()
        while self.deck:
            self.dealsinglehand()
            self.playhand()
        self.calculateresults()
    
    def resetcounts(self):
        for p in self.players:
            p.cardstaken = []
            p.currenthand = []
            p.results = {}
            
    def dealsinglehand(self):
        """
            Deal hands to both players and a board
        """
        for p in self.players:
            p.currenthand = self.deck[0:3]
            self.deck = self.deck[3:]

        nc = self.deck[0:4]
        self.deck = self.deck[4:]
        for c in nc:
            self.board.append(c)

    def playhand(self):
        while self.players[0].currenthand:
            for p in self.players:
                self.calculateoptions(p)

        if len(self.deck) == 0:
            for c in self.board:
                self.lastwinner.cardstaken.append(c)

                
    def calculateoptions(self, player):
        """ Look through the hand and compare board.
            Calculate all possibilities for playing.
        """
        combos = self.createcombos()
        plays = []
        for c in player.currenthand:
            for combo in combos:
                if c.rank == combo.total:
                    plays.append((c,combo.cards))
        
        if len(plays) == 1:
            # Only 1 option so play it
            # Assuming we always want to take something if we can?
            self.playcard(player, plays[0][0], plays[0][1])
            self.lastwinner = player

        elif len(plays) == 0:
            # cant play - work out least bad card to play
            # but for now just play 1st card in hand
            self.playcard(player, player.currenthand[0])
        else:
            # more than 1 option - need logic
            # just do 1st option for now
            self.playcard(player, plays[0][0], plays[0][1])
            self.lastwinner = player

    def createcombos(self):
        """ 
            Create a list containing all possible,
            playable combinations on the board 
        """
        combos = []
        for i in range(len(self.board) + 1):
            for cards in combinations(self.board, i):
                cardsum = 0
                ncards = 0
                for c in cards:
                    ncards += 1
                    cardsum = cardsum + c.rank
                if cardsum <= 10:
                    combos.append(Combo(cardsum,ncards,cards))
        return combos

    def playcard(self, player, cardtoplay,cardstotake=None):
        """ Remove the card from the players Hand.
            Remove the cards from the board
            Add the cards to the players taken cards
        """
        # if there is an equivalent rank of the card being played
        # on the board it must be taken ahead of any combo
        
        player.currenthand.pop(player.currenthand.index(cardtoplay))
        if cardstotake:
            for c in cardstotake:
                player.cardstaken.append(c)
            player.cardstaken.append(cardtoplay)
            for c in cardstotake:
                self.board.pop(self.board.index(c))
        else:
            self.board.append(cardtoplay)
      
    def calculateresults(self):
        for p in self.players:
            hand = p.cardstaken
            nd, gsb = countdenari(hand)
            if gsb:
                p.points += 1
            p.results['cardstaken'] = len(hand)
            p.results['denari'] = nd
            p.results['primiera'] = calcprimes(hand)
            p.results['settebello'] = gsb
            print(p.results)
         
        p1 = self.players[0]
        p2 = self.players[1]
        
        # chuck these in a function
        
        if p1.results['cardstaken'] > p2.results['cardstaken']:
            p1.points += 1
        elif p1.results['cardstaken'] < p2.results['cardstaken']:
            p2.points += 1
        else:
            #error check
            assert(p1.results['cardstaken'] == p2.results['cardstaken'])
        
        if p1.results['denari'] > p2.results['denari']:
            p1.points += 1
        elif p1.results['denari'] < p2.results['denari']:
            p2.points += 1
        else:
            #error check
            assert(p1.results['denari'] == p2.results['denari'])      
            
        if p1.results['primiera'] > p2.results['primiera']:
            p1.points += 1
        elif p1.results['primiera'] < p2.results['primiera']:
            p2.points += 1
        else:
            #error check
            assert(p1.results['primiera'] == p2.results['primiera'])  
        
        print(p1.points)
        print(p2.points)
   
def countdenari(hand):
    nd = 0
    gotsette = False
    for c in hand:
        if c.suit == 'Denari':
            nd += 1
            if c.rank == 7:
                gotsette = True
    return nd, gotsette
    
def calcprimes(hand):
    """
        Given hand; find highest prime in each suit and sum them
    """
    hand.sort()
    carddict = {'Bastoni':[],'Coppe':[],'Denari':[],'Spade':[]}
    for s, group in groupby(hand,lambda x: x[0]):
        for c in group:
            carddict[s].append(c.prime)
    
    primsum = 0
    for k in carddict.keys():
        primsum = primsum + max(carddict[k])
    return primsum

      
class Card(tuple):
    def __init__(self, card):
        self.suit = card[0]
        self.rank = int(card[1][0])
        self.prime = int(card[1][1])

    def __repr__(self):
        return str((self.suit,self.rank))

class Combo:
    def __init__(self, total, ncards, cards):
        self.total = total
        self.ncards = ncards
        self.cards = cards
     
    def __repr__(self):
        return str((self.total,self.ncards,self.cards))

class Player:
    def __init__(self, pname):
        self.name = pname
        self.cardstaken = []
        self.currenthand = []
        self.results = {}
        self.points = 0
        
    def __repr__(self):
        return self.name
