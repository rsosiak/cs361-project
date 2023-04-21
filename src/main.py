import os
import random

from dotenv import load_dotenv
from pokemontcgsdk import Card, RestClient, Set

load_dotenv()

RestClient.configure(os.getenv('POKEMON_API_KEY'))


def search_for_card(name_input):
    """
    Given a card name, outputs a list of cards that match.
    """

    card = Card.where(q=f'set.id:base1 name:{name_input}')

    return card


def parse_card_info(card):
    """
    Given a card object, parses the object and returns a string containing card
    attributes.
    """

    name = card.name
    set_name = card.set.name
    id = card.id.split('-')[1]
    rarity = card.rarity

    tcgplayer_normal_market = parse_tcgplayer_card_price(
        card.tcgplayer.prices.normal, 'market'
    )

    tcgplayer_holofoil_market = parse_tcgplayer_card_price(
        card.tcgplayer.prices.holofoil, 'market'
    )

    output = (
    f'Name: {name}\n'
    f'Set Name: {set_name}\n'
    f'Number: {id}\n'
    f'Rarity: {rarity}\n'
    f'Normal (Market Price): {tcgplayer_normal_market}\n'
    f'Holofoil (Market Price): {tcgplayer_holofoil_market}'
    )

    return output


def parse_tcgplayer_card_price(price_obj, price_point):
    """
    Given a card price object and price point, parses and returns card price, if
    available. Returns N/A if price is None.

    The available price points are: 'low', 'mid', 'high', 'market', 'directLow'.
    """

    if price_obj:
        price = str(getattr(price_obj, price_point))
        price = '{0:.2f}'.format(float(price))
        price = f'${price}'
    else:
        price = 'N/A'

    return price


def parse_additional_prices(card):
    """
    Given a card object, get additional prices.
    """

    tcgplayer_normal_low = parse_tcgplayer_card_price(
        card.tcgplayer.prices.normal, 'low'
    )

    output = (
        f'Normal (Low Price): {tcgplayer_normal_low}'
    )

    return output


def generate_random_card_name():
    """Generates a random card name."""

    rand_num = random.randint(1, 999999)
    data = Set.where(q='id:base1')
    data = data[0]
    num_cards_in_set = data.printedTotal

    card = Card.where(q=f'id:base1-{rand_num % num_cards_in_set}')[0]
    
    return card.name


def get_list_of_cards(curr_page, page_size):
    """
    Given a page and number of elements per page, returns a list of cards on 
    that page.
    """
    cards = Card.where(q=f'set.id:base1', page=curr_page, pageSize=page_size)

    return cards


def main():

    print('\n-----------------------------------------------------------------')
    print('----------------------POKEMON CARD EXPLORER----------------------')
    print('-----------------------------------------------------------------')
    print(
        '\nSelect an option by entering the option\'s corresponding number and ' +
        'then hitting Enter:')
    
    options = [
        '1. Search for a card',
        '2. Generate random card name',
        '3. Browse cards',
        '4. Exit'
    ]

    while True:

        for option in options:
            print(option)

        user_input = input('\nSelect an option: ')

        if user_input == '1':
            print('You selected "Search for a card"\n')

            while True:
                card_name = input('Please enter a card name: ')
                card = search_for_card(card_name)
            
                if len(card) == 0:
                    print(
                        "\nSorry, I wasn't able to find a card with that name, " +
                        "please try again...")
                else:
                    card = card[0]
                    break

            print(parse_card_info(card))
            
            while True:
                price_input = input(
                    '\nWould you like to view more card prices (Y/N)? '
                )
                if price_input.upper() == 'Y':
                    print(f'{parse_additional_prices(card)}\n')
                    break
                elif price_input.upper() == 'N':
                    break
                else:
                    print('That is not a valid option, please try again...\n')

        elif user_input == '2':
            print('You selected "Generate random card name"\n')
            print(
                f'Your randomly generated card name is: ' +
                f'{generate_random_card_name()}' +
                '\n'
            )

        elif user_input == '3':
            print('You selected "Browse cards"\n')
            
            curr_page = 1
            PAGE_SIZE = 5
            
            while True:
                cards = get_list_of_cards(curr_page, PAGE_SIZE)
                
                for i, card in enumerate(cards):
                    print(f'{i%PAGE_SIZE+1}. {card.name}')

                if len(cards) < PAGE_SIZE:
                    print('\nP: Previous page | M: Main menu')
                elif curr_page == 1:
                    print('\nN: Next page | M: Main menu')
                else:
                    print('\nP: Previous page | N: Next page | M: Main menu')
                
                user_input = input('\nSelect an option: ')
                if not user_input.isalpha() and int(user_input) in range(1, PAGE_SIZE+1):
                    user_input = int(user_input)
                    print(parse_card_info(cards[user_input-1]))
                    print()
                    while True:
                        price_input = input(
                            'Would you like to view more card prices (Y/N)? '
                        )
                        if price_input.upper() == 'Y':
                            print(parse_additional_prices(card))
                            break
                        elif price_input.upper() == 'N':
                            break
                        else:
                            print('That is not a valid option, please try again...')
                            continue
                    break
                elif str(user_input).upper() == 'M':
                    break
                elif str(user_input).upper() == 'P' and curr_page > 1:
                    curr_page -= 1
                elif str(user_input).upper() == 'N' and len(cards) == 10:
                    curr_page += 1
                else:
                    print('That is not a valid option, please try again...\n')

        elif user_input == '4':
            break

        else:
            print('That is not a valid option, please try again...')
    
    print('Goodbye!!\n')

    return


if __name__ == '__main__':
    main()