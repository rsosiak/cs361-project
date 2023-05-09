import os
import random
import time

import zmq

from dotenv import load_dotenv

from pokemontcgsdk import Card, Set, RestClient

load_dotenv()

RestClient.configure(os.getenv('POKEMON_API_KEY'))

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")


def generate_random_card_name():
    """Generates a random card name."""

    rand_num = random.randint(1, 999999)
    data = Set.where(q='id:base1')
    data = data[0]
    num_cards_in_set = data.printedTotal

    card = Card.where(q=f'id:base1-{rand_num % num_cards_in_set}')[0]

    return card.name


while True:
    print('Waiting for request...')
    time.sleep(1)
    #  Wait for request from client
    request = socket.recv()
    request = request.decode('utf-8')
    print('Request received...')
    time.sleep(1)
    print('Generating Pokemon card...')
    time.sleep(1)
    if request == '2':
        name = generate_random_card_name()
        #  Send reply back to client
        print(f'Sending {name} card to client...')
        socket.send_string(name)
    else:
        socket.send_string('Request failed...')
