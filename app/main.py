import bottle
import os
import random

directions = ['up', 'down', 'left', 'right']


@bottle.route('/')
def static():
    return "the server is running"


@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')


@bottle.post('/start')
def start():
    data = bottle.request.json
    game_id = data.get('game_id')
    board_width = data.get('width')
    board_height = data.get('height')

    head_url = '%s://%s/static/head.png' % (
        bottle.request.urlparts.scheme,
        bottle.request.urlparts.netloc
    )

    # TODO: Do things with data

    return {
        'color': '#00FF00',
        'taunt': '{} ({}x{})'.format(game_id, board_width, board_height),
        'head_url': head_url,
        'name': 'battlesnake-python'
    }


@bottle.post('/move')
def move():
    global directions
    data = bottle.request.json

    print(data)

    snakes = data['snakes']
    height = data['height']
    width = data['width']
    food = data['food']

    me = data['you']
    donthitneck(me)

    direction = random.choice(directions)
    print(direction)
    return {
        'move': direction,
        'taunt': 'battlesnake-python!'
    }


def donthitneck(me):
    """Stops the snake from hitting its own neck"""
    global directions
    print(me)
    head = me[0]
    neck = me[1]
    neckdir = findadjacentdir(head, neck)


def findadjacentdir(a, b):
    print(a)
    print(b)


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'))
