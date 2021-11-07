import numpy as np
import pandas as pd

class Deck(object):
    """
    Creates a Deck obj.

    Parameters
    ----------
    num_decks : int
        The number of total decks in the deck. Default 6. Must be between 1 and 8 inclusive.

    cut_card_loc : float
        Approximate location of where the cut card is place (from the end of the shoe). Must be between .5 and 2 inclusive. Actual location will be randomly adjusted.
    """

    # Creates a list of card suit/values pairs as strings that represents a single deck
    
    one_deck = [f"{val}{suit}" for suit in ['D', 'H', 'C', 'S'] for val in list(range(2,11)) + ['J', 'Q', 'K', 'A']]
    
    def __init__(self, num_decks=6, cut_card_loc=1):
        if not (isinstance(num_decks, int) and (isinstance(cut_card_loc, int) or isinstance(cut_card_loc, float))):
            raise TypeError("Please enter an integer for num_decks or an interger or float for cut_card_loc!")
        if (not 0 < num_decks < 9) or (not .5 <= cut_card_loc <= 2):
            raise ValueError('Please enter a number of decks between 1 and 8 or the cut card location between .5 and 2!')
        self.num_decks = num_decks
        self.cut_card_loc = cut_card_loc
        self.full_deck = one_deck*self.num_decks
        self.current_deck = None
        
        self.shuffle()
        
    def shuffle(self):
        """
        Mutates the current_deck atrribute of the Deck object to shuffle the cards.
        """
        self.current_deck = list(np.random.choice(self.full_deck, size=len(self.full_deck)))
        
        # Add the cut card to the shuffled deck
        location = int(np.random.uniform(.5, 1.5)*(52*self.cut_card_loc))
        self.current_deck.insert(location, '0')

class Dealer(object):
    """
    Creates a Dealer obj.

    Parameters
    ----------
    num_decks : int
        The number of total decks in the deck. Default 6. Must be between 1 and 8 inclusive.

    cut_card_loc : float
        Approximate location of where the cut card is place (from the end of the shoe). Must be between .5 and 2 inclusive. Actual location will be randomly adjusted.

    hit_on_soft17 : bool
        Whether or not the dealer must hit on a soft 17 (A + 6). Default True.

    min_bet : int
        The minimum bet allowed at the table. Default 15.

    max_bet : int
        The maxiumum bet allowed at the table. Default 1000.
    """
    
    def __init__(self, num_decks = 6, cut_card_loc = 1, hit_on_soft17 = True, min_bet = 15, max_bet = 1000):
        self.hit_on_soft17 = hit_on_soft17
        self.min_bet = min_bet
        self.max_bet = max_bet
        self.deck = Deck(num_decks, cut_card_loc)
        self.current_hand = []


    def decide_next_move(self):
        """
        A method to decide what the dealer's next move will be.

        Return
        ------
        str, a string indicating what to do next.
        """
        # Check the different conditions
        if self.check_hand_total(self.current_hand) < 17:
            return 'hit'
        else:
            return 'stand'

    def deal_card(self):
        """
        Deals the first card in the current deck (deck treated like a stack so the "top card" is the last value in the array).

        Returns the value of the card as tuple, first element is the value, second element in the suit.
        """
        return self.deck.current_deck.pop()

    def reset_hand(self):
        """
        Resets the current hand.
        """
        self.current_hand = []

    def pay_out(self, player, winnings):
        """
        Pays a player for a round win.

        Parameters
        ----------
        player : Player
            The player object associated with the player who won.
        winnings: float
            The amount of money won by the player.
        """
        player.bank += winnings

    @staticmethod
    def check_blackjack(hand):
        """
        Checks whether a hand has blackjack.

        Return
        ------
        bool, whether or not the hand is blackjack.
        """
        if (hand[0][0] == 'A' and hand[1][0] in ['10', 'J', 'Q', 'K']) or (hand[1][0] == 'A' and hand[0][0] in ['10', 'J', 'Q', 'K']):
            return True
        else:
            return False

    @staticmethod
    def check_hand_total(hand):
        """
        Checks the value of a hand.

        Return
        ------
        int, the value of the current hand.
        """
        hand_vals = [int(card[0]) if card[0] not in ['A', 'J', 'Q', 'K'] else 10 if card[0] in ['J', 'Q', 'K'] else 1 for card in hand]

        # Check if any vals are aces
        aces = [val for val in hand_vals if val == 1]
        hand_sum = sum(hand_vals)
        
        if aces:
            sum_with_eleven_ace = hand_sum + 10
            
            if sum_with_eleven_ace <= 21:
                return sum_with_eleven_ace
            else:
                return hand_sum
        
        else:
            return hand_sum


class Player(object):
    """
    Player class to keep track of player bank, strategy, and behavior.

    Parameters
    ----------
    bank : float
        Amount of money that the player has.
    bet_strategy : str
        The type of betting strategy used by the player. Currently only "dalembert" is supported,
        but additional strategies will be added.
    play_strategy: str
        The type of playing strategy used by the player. Currently only "basic" is supported,
        but will be adding "emotional" or something similar to simulate erratic player behavior.
    """
    move_dict = {'H': 'hit', 'S': 'stand', 'D': 'double', 'SP': 'split'}

    def __init__(self, bank, bet_strategy = 'dalembert', play_strategy = 'basic'):
        self.bank = bank
        self.bet_strategy = bet_strategy
        # Replace play_strategy with df of strat
        self.play_strategy = play_strategy
        self.current_hand = []
        self.current_bet = 0
        self.previous_bet = None
        self.previous_outcome = None

    def choose_play_strategy(self, dealer):
        """
        Filters the move df based on how many decks are being used.
        """
        df = pd.read_csv('./basic_strats.csv', index_col=0)
        if self.play_strategy == 'basic':
            if dealer.deck.num_decks == 1:
                self.play_strategy = df[df['num_decks'] == 1]
            elif dealer.deck.num_decks in [2,3]:
                self.play_strategy = df[df['num_decks'] == 2]
            else:
                self.play_strategy = df[df['num_decks'] == 4]

    def decide_next_move(self, dealer):
        """
        A method to decide what the player's next move will be.
    
        Parameters
        ----------
        dealer: Dealer
            A dealer object so we can check their face up card.

        Return
        ------
        str, a string indicating what to do next.
        """
        dealer_card = dealer.current_hand[0][0]

        # Check if player has blackjack
        if len(self.current_hand) == 2 and Dealer.check_blackjack(self.current_hand):
            return 'stand'
        else:
            if len(self.current_hand) == 2:
                if self.current_hand[0][0] == self.current_hand[1][0]:
                    return Player.move_dict[self.play_strategy.loc[f"{self.current_hand[0][0]},{self.current_hand[1][0]}", dealer_card]]
                elif self.current_hand[0][0] == 'A' or self.current_hand[1][0] == 'A':
                    if self.current_hand[0][0] == 'A':
                        return Player.move_dict[self.play_strategy.loc[f"A{self.current_hand[1][0]}", dealer_card]]
                    else:
                        return Player.move_dict[self.play_strategy.loc[f"A{self.current_hand[0][0]}", dealer_card]]
                else:
                    return Player.move_dict[self.play_strategy.loc[f"{Dealer.check_hand_total(self.current_hand)}", dealer_card]]
            else:
                return Player.move_dict[self.play_strategy.loc[f"{Dealer.check_hand_total(self.current_hand)}", dealer_card]]

    def check_bet_allowed(self, bet_amt, dealer):
        """
        Checks to see if the player's bet is greater than max or if they player doesn't have enough
        funds for the bet.

        Parameters
        ----------
        bet_amt: int
            Amount that the player is trying to bet.

        dealer: Dealer
            A dealer object so we can check the maximum bet (unit).

        Return
        ------
        bool, is the bet allowed.
        """
        if self.bank < bet_amt or bet_amt > dealer.max_bet:
            return False

        else:
            return True

    def place_initial_bet(self, dealer):
        """
        A method to decide what the player's next bet will be.
    
        Parameters
        ----------
        dealer: Dealer
            A dealer object so we can check the minimum bet (unit).

        Return
        ------
        bool, whether or not the bet goes through.
        """
        if not self.previous_bet and not self.previous_outcome:
            self.current_bet = dealer.min_bet
            self.bank -= self.current_bet
        elif self.previous_outcome == 'win':
            if self.previous_bet == dealer.min_bet:
                if check_bet_allowed(dealer.min_bet, dealer):
                    self.current_bet = dealer.min_bet
                    self.bank -= self.current_bet
                else:
                    raise ValueError('Not enough funds for bet!')
            else:
                if check_bet_allowed(self.previous_bet-dealer.min_bet, dealer):
                    self.current_bet = self.previous_bet-dealer.min_bet
                    self.bank -= self.current_bet
                else:
                    raise ValueError('Not enough funds for bet!')
        elif self.previous_outcome == 'loss':
            if self.previous_bet == dealer.min_bet:
                if check_bet_allowed(self.previous_bet+dealer.min_bet, dealer):
                    self.current_bet = self.previous_bet+dealer.min_bet
                    self.bank -= self.current_bet
                elif self.previous_bet+dealer.min_bet > self.bank:
                    raise ValueError('Not enough funds for bet!')
                elif self.previous_bet+dealer.min_bet > dealer.max_bet:
                    if check_bet_allowed(dealer.max_bet, dealer):
                        self.current_bet = dealer.max_bet
                        self.bank -= self.current_bet
                    else:
                        raise ValueError('Not enough funds for bet!')