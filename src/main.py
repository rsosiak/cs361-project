import os

import zmq

from dotenv import load_dotenv
from pokemontcgsdk import Card, Rarity, RestClient, Set, Type

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
    Given a card price object and price point, parses and returns card price,
    if available. Returns N/A if price is None.

    Available price points are: 'low', 'mid', 'high', 'market', 'directLow'.
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


def get_list_of_cards(curr_page, page_size):
    """
    Given a page and number of elements per page, returns a list of cards on
    that page.
    """
    cards = Card.where(q='set.id:base1', page=curr_page, pageSize=page_size)

    return cards


def get_set_names():
    """Returns a list of card set names."""
    sets = Set.all()
    sets = [c_set.name for c_set in sets]
    return sets


def parse_list_for_output(arr):
    """
    Given a list, iterates through each element in the list, and creates string
    output.
    """
    output = ''
    for el in arr:
        output += f'- {el}\n'

    return output


def get_random_card_name():
    """Generates a random card name."""
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect('tcp://localhost:5555')

    socket.send_string('2')
    message = socket.recv()
    message = message.decode('utf-8')

    return message


def explore(user_input):
    """
    Given a string input chosen by the user, returns a string containing the
    appropriate list of cards.
    """
    if user_input == '1':
        arr = get_set_names()
    elif user_input == '2':
        arr = Type.all()
    elif user_input == '3':
        arr = Rarity.all()
    else:
        output = 'That is not a valid option, please try againn...\n'
        return output

    return parse_list_for_output(arr)


def display_pagination_message(card_arr, curr_page, page_size):
    """
    Given an array of cards, current page, and number of elements per page,
    returns a string representing the appropriate pagination options.
    """
    if len(card_arr) < page_size:
        output = '\nP: Previous page | M: Main menu'
        return output
    if curr_page == 1:
        output = '\nN: Next page | M: Main menu'
        return output

    output = '\nP: Previous page | N: Next page | M: Main menu'
    return output


def main():

    print('\n-------------------------------------------------------------')
    print('--------------------POKEMON CARD EXPLORER--------------------')
    print('-------------------------------------------------------------')
    print(
        '\nSelect an option by entering the option\'s corresponding number ' +
        'and then hitting Enter:')

    options = [
        '1. Search for a card',
        '2. Generate random card name',
        '3. Browse individual cards',
        '4. Explore cards',
        '5. Help',
        '6. Exit'
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
                        "\nSorry, I wasn't able to find a card with that " +
                        "name, please try again...")
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
            rng_card = get_random_card_name()
            print('You selected "Generate random card name"\n')
            print(
                'Your randomly generated card name is: ' +
                f'{rng_card}'
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

                output = display_pagination_message(
                    card_arr=cards,
                    curr_page=curr_page,
                    page_size=PAGE_SIZE
                )

                print(output)

                user_input = input('\nSelect an option: ')

                if not user_input.isalpha() \
                        and int(user_input) in range(1, PAGE_SIZE+1):
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
                            print(
                                'That is not a valid option, ' +
                                'please try again...'
                            )
                            continue
                    break
                elif str(user_input).upper() == 'M':
                    break
                elif str(user_input).upper() == 'P' and curr_page > 1:
                    curr_page -= 1
                elif str(user_input).upper() == 'N'\
                        and len(cards) == PAGE_SIZE:
                    curr_page += 1
                else:
                    print('That is not a valid option, please try again...\n')

        elif user_input == '4':
            print('You selected "Explore cards"\n')

            explorables = [
                '1. Explore card sets',
                '2. Explore card types',
                '3. Explore card rarities',
                '4. Return to main menu'
            ]

            while True:
                for explorable in explorables:
                    print(explorable)
                print()
                user_input = input('What would you like to explore? ')
                print()

                if user_input == '4':
                    break
                else:
                    output = explore(user_input)
                    print(output)

        elif user_input == '5':
            print()
            print(
                'Search for a card: User inputs a card name. If the card ' +
                "exists, user will be presented with the card's attributes."
            )
            print(
                'Generate random card name: User will be presented with a ' +
                'random card name.'
            )
            print(
                'Browse cards: User is presented with a list of cards. User ' +
                'can select a card to view its attributes. User can also ' +
                'page through lists by using the appropriate keyboard ' +
                'commands.'
            )
            print(
                'Explore cards: User is presented with list of choices. ' +
                'User can select one of the choices and will be provided ' +
                'with a list corresponding to their choice.'
            )
            print()
            while True:
                user_input = input(
                    'Would you like to return to the main menu (Y/N)? '
                )
                if user_input.upper() == 'Y':
                    print()
                    break
                elif user_input.upper() == 'N':
                    continue
                else:
                    print('That is not a valid option, please try again...\n')

        elif user_input == '6':
            break

        else:
            print('That is not a valid option, please try again...')

    print('Goodbye!!\n')

    return


if __name__ == '__main__':
    main()
