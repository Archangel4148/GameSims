import random

from Spades.spades_tools import SpadesDeck, Player

PLAYER_COUNT = 4  # Number of players

# Define an arbitrary suit order for players to organize their hands into
SUIT_ORDER = {"Clubs": 0, "Diamonds": 1, "Hearts": 2, "Spades": 3}

# Create a list of players
players = [Player(f"Player {i + 1}") for i in range(PLAYER_COUNT)]

# Create a standard deck of 52 cards
deck = SpadesDeck()

# Select a dealer at random
dealer_index = random.randint(0, PLAYER_COUNT - 1)
# Evaluate deal order, starting to the left of the dealer
deal_order = players[dealer_index + 1:] + players[:dealer_index + 1]

# Deal a hand to each player
deck.deal(deal_order)

# Each player then organizes their hand by suit
for player in players:
    player.hand.sort(key=lambda card: SUIT_ORDER[card.suit])

print("Dealer:", players[dealer_index].name)
for player in players:
    print(f"({len(player.hand)})", end=" ")
    print(player)
