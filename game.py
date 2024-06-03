import random
import os


active_game = True
cards = [2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K', 'A']
suits = ['❤️', '♦️', '♠️', '♣️']


def blinds():
   global big_blind
   global small_blind
  
   if 'big_blind' not in locals():
       big_blind = random.choice(['user', 'computer'])
       if big_blind == 'user':
           small_blind = 'computer'
       elif big_blind == 'computer':
           small_blind = 'user'
   elif big_blind == 'user':
       big_blind = 'computer'
       small_blind = 'computer'
   elif big_blind == 'computer':
       big_blind = 'user'
       small_blind = 'computer'


def create_hand():
   global user_hand
   global computer_hand
   
   user_hand = {
       'cards': [random.choice(cards), random.choice(cards)],
       'suits': [random.choice(suits), random.choice(suits)],
   }
   computer_hand = {
       'cards': [random.choice(cards), random.choice(cards)],
       'suits': [random.choice(suits), random.choice(suits)]
   }


   return user_hand, computer_hand


def chips_handler(action, quantity):
   global user_chips
   global computer_chips
   global pot
   global paid


   if 'user_chips' not in locals():
       user_chips = 10000
   if 'computer_chips' not in locals():
       computer_chips = 10000
   if 'pot' not in locals():
       pot = 0
   if 'paid' not in locals():
       paid = 0


   if action == 'add':
       user_chips += quantity
       pot -= quantity
       paid -= quantity
   elif action == 'decrease':
       user_chips -= quantity
       pot += quantity
       paid += quantity
   elif action =='computerbet':
       pot += quantity
       computer_chips -= quantity
   elif action == 'setup':
       return


def create_community_cards(series):
   global community_cards


   community_cards = {
       'flop': [],
       'turn': [],
       'river': [],
   }


   if series == 'flop':
       for _ in range(3):
           card = [random.choice(cards), random.choice(suits)]
           community_cards['flop'].append(card)
           community_cards['turn'].append(card)
           community_cards['river'].append(card)
   elif series == 'turn':
       card = [random.choice(cards), random.choice(suits)]
       community_cards['turn'].append(card)
       community_cards['river'].append(card)
   elif series == 'river':
       card = [random.choice(cards), random.choice(suits)]
       community_cards['river'].append(card)
   elif series == 'all':
       for _ in range(3):
           card = [random.choice(cards), random.choice(suits)]
           community_cards['flop'].append(card)
           community_cards['turn'].append(card)
           community_cards['river'].append(card)
           card = [random.choice(cards), random.choice(suits)]
           community_cards['turn'].append(card)
           community_cards['river'].append(card)
           card = [random.choice(cards), random.choice(suits)]
           community_cards['river'].append(card)


   return community_cards


def computer_decision():
   total_strength = 0
   suit_strength = user_hand['suits'][0] == user_hand['suits'][1]


   if type(computer_hand['cards'][0]) is str and not type(computer_hand['cards'][1]) is str:
       straight_odds = abs((cards.index(computer_hand['cards'][0]) + 1) - computer_hand['cards'][1])
       hand_strength = abs((cards.index(computer_hand['cards'][0]) + 1) - (cards.index(computer_hand['cards'][1]) + 1))
   elif type(computer_hand['cards'][1]) is str and not type(computer_hand['cards'][0]) is str:
       straight_odds = abs(computer_hand['cards'][0] - (cards.index(computer_hand['cards'][1]) + 1))
       hand_strength = abs((cards.index(computer_hand['cards'][0]) + 1) - (cards.index(computer_hand['cards'][1]) + 1))
   elif type(computer_hand['cards'][0]) is str and type(computer_hand['cards'][1]) is str:
       straight_odds = abs((cards.index(computer_hand['cards'][0]) + 1) - (cards.index(computer_hand['cards'][1]) + 1))
       hand_strength = abs((cards.index(computer_hand['cards'][0]) + 1) - (cards.index(computer_hand['cards'][1]) + 1))
   else:
       straight_odds = abs(computer_hand['cards'][0] - computer_hand['cards'][1])
       hand_strength = computer_hand['cards'][0] + computer_hand['cards'][1]


   if straight_odds <= 3:
       straight_odds = True
   else:
       straight_odds = False


   if straight_odds and suit_strength:
       total_strength += 15
   elif straight_odds or suit_strength:
       total_strength += 5
   elif computer_hand['cards'][0] == computer_hand['cards'][1]:
       total_strength += 15
  
   total_strength += hand_strength


   if total_strength > 20:
       decision = 'bet'
   elif total_strength > 15:
       decision = 'raise'
   elif total_strength > 10:
       decision = 'call'
   else:
       decision = 'fold'


   return decision


def player_decision():
   action = input(f"The pot is {pot}. Play say 'CA' to call {pot - paid} | 'F' to fold | 'R' to raise: ")


   if action == 'CA':
       chips_handler('decrease', pot - paid)
       print(f'You have called {pot - paid} chips.')
   elif action == 'F':
       active_game = True
       return
   elif action == 'R':
       raise_quantity = input('How many chips would you like to raise? Enter a number: ')
       chips_handler('decrease', raise_quantity)
       print(f'You have raised {raise_quantity} chips.')


def evaluate_hand(hand, community_cards):
   all_cards = hand['cards'] + [card[0] for card in community_cards['flop']] + [community_cards['turn'][0][0], community_cards['river'][0][0]]
   card_counts = {}
   suits = [card[1] for card in hand['suits'] + [card[1] for card in community_cards['flop']] + [community_cards['turn'][0][1], community_cards['river'][0][1]]]


   for card in all_cards:
       card_counts[card] = card_counts.get(card, 0) + 1


   sorted_values = sorted([cards.index(card) + 1 for card in all_cards])
   straight = any(sorted_values[i] == sorted_values[i + 1] - 1 for i in range(len(sorted_values) - 1))


   flush = any(suits.count(suit) >= 5 for suit in set(suits))


   if flush and straight and sorted_values[-1] == 14 and sorted_values[0] == 10:
       return 10
   elif flush and straight:
       return 9
   elif any(card_count == 4 for card_count in card_counts.values()):
       return 8
   elif any(card_count == 3 for card_count in card_counts.values()) and any(card_count == 2 for card_count in card_counts.values()):
       return 7
   elif flush:
       return 6
   elif straight:
       return 5
   elif any(card_count == 3 for card_count in card_counts.values()):
       return 4
   elif len(set(card_counts.values())) == 2 and 2 in card_counts.values():
       return 3
   elif any(card_count == 2 for card_count in card_counts.values()):
       return 2


   high_card_values = sorted([cards.index(card) + 1 for card in all_cards], reverse=True)
   return sum(high_card_values[:5])


def start_round():
   global active_game
   global round_stage


   active_round = True
   round_stage = 'preflop'


   # Betting Rounds
   while active_round:
       comp_decision = computer_decision()


       while round_stage == 'preflop':
           round_stage = ''


           print("Betting Round:")
           print('\nYour cards are: ', user_hand['cards'][0], ' of ', user_hand['suits'][0], ', ', user_hand['cards'][1], ' of ', user_hand['suits'][1])


           if comp_decision == 'fold':
               print("\nComputer folds.")
               active_round = False
               break
           else:
               if big_blind == 'user':
                   chips_handler('decrease', 500)
                   chips_handler('computerbet', 250)
                   print(f'Pot: {pot} chips | Your Balance: {user_chips} chips')
                   print('\nYou are the big blind. You have paid 500 chips as a buy-in for this round.')
                   print(f'Balance remaining: {user_chips} chips')
               elif small_blind == 'user':
                   chips_handler('decrease', 250)
                   chips_handler('computerbet', 500)
                   print(f'Pot: {pot} chips | Your Balance: {user_chips} chips')
                   print('\nYou are the small blind. You have paid 250 chips as a buy-in for this round.')


           if big_blind == 'user' and paid == pot and not comp_decision == 'fold':
               check_or_bet = input("\nComputer calls. You have the option to check or bet. Enter 'check' or 'bet': ")
               if check_or_bet.lower() == 'check':
                   print("\nYou check.")
                   round_stage = 'flop'
               else:
                   player_decision()


           if small_blind == 'user' and  not comp_decision == 'fold':
               player_decision()


       while round_stage == 'flop':
           os.system("clear")
           print("Flop Round:")
           print(f'\nPot: {pot} chips | Your Balance: {user_chips} chips')
           print('\nYour cards are: ', user_hand['cards'][0], ' of ', user_hand['suits'][0], ', ', user_hand['cards'][1], ' of ', user_hand['suits'][1])
           print(f'Community cards:\n{community_cards["flop"][0][0]} of {community_cards["flop"][0][1]}\n{community_cards["flop"][1][0]} of {community_cards["flop"][1][1]}\n{community_cards["flop"][2][0]} of {community_cards["flop"][2][1]}')
           if comp_decision == 'fold':
               print("\nComputer folds.")
               active_round = False
               break
           else:
               if big_blind == 'user':
                   player_decision()
               elif small_blind == 'user':
                   print('\nYou are the small blind. You have paid 250 chips as a buy-in for this round.')
                   chips_handler('decrease', 250)


           if big_blind == 'user' and paid == pot:
               check_or_bet = input("You have the option to check or bet. Enter 'check' or 'bet': ")
               if check_or_bet.lower() == 'check':
                   print("\nYou check.")
                   round_stage = 'flop'
               else:
                   player_decision()


   # Showdown only if the round was not ended by a fold
   if active_round:
       print("\nShowdown:")
       print(f'Your cards: {user_hand["cards"]} of {user_hand["suits"]}')
       print(f'Computer cards: {computer_hand["cards"]} of {computer_hand["suits"]}')
       print(f'Community cards: {community_cards["flop"]} {community_cards["turn"]} {community_cards["river"]}')


       winner = (evaluate_hand(user_hand, community_cards), evaluate_hand(computer_hand, community_cards))


       print(winner)


   play_again = input('Would you like to start a new round? Say "yes" or "no": ')
   if play_again == 'yes':
       os.system("clear")
       active_game = True
   else:
       return print(f'Thank you for playing. You finished with {user_chips} and started with 10,000. If you change your mind, please restart the program.')
       active_game = False


while active_game:
   active_game = False
   create_hand()
   chips_handler('setup', 0)
   blinds()
   create_community_cards('all')
   start_round()




