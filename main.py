from playing_card_tools import Card

def main():
    cards = [Card("KH"), Card("AS"), Card("3C")]

    for card in cards:
        print(card.get_full_card_name())

if __name__ == '__main__':
    main()