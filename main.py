from playing_card_tools import Card, Deck


def main():
    # Create a deck (pre-shuffled)
    deck = Deck(standard_deck=True)

    # for _ in range(5):
    #     print(deck.draw_card())
    print(deck)

if __name__ == '__main__':
    main()