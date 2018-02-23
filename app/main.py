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
    directions = ['up', 'down', 'left', 'right']
    data = bottle.request.json

    snakes = data['snakes']
    height = data['height']
    width = data['width']
    food = data['food']

    me = data['you']['body']['data']

    donthitneck(me)
    donthitwalls(me, width, height)

    direction = random.choice(directions)
    print(direction)
    return {
        'move': direction,
        'taunt': 'battlesnake-python!'
    }


def donthitwalls(me, width, height):
    global directions
    head = me[0]

    if head['x'] == 0:
        directions.remove('left')
        print('wall on left')
    if head['x'] == width-1:
        directions.remove('right')
        print('wall on right')
    if head['y'] == 0:
        directions.remove('up')
        print('wall up')
    if head['y'] == height-1:
        directions.remove('down')
        print('wall down')

def donthitneck(me):
    """Stops the snake from hitting its own neck"""
    global directions
    head = me[0]
    neck = me[1]
    neckdir = findadjacentdir(head, neck)
    print('neck direction: ' + str(neckdir))
    if neckdir and neckdir in directions:
        directions.remove(neckdir)


def findadjacentdir(a, b):
    """Gives direction from a to b if they are adjacent, if they are not adjacent returns false"""
    ax = a['x']
    ay = a['y']
    bx = b['x']
    by = b['y']
    xdiff = ax - bx
    ydiff = ay - by

    if (xdiff in range(-1, 2) and ydiff == 0) or (ydiff in range(-1, 2) and xdiff == 0):
        if xdiff != 0:
            if xdiff > 0:
                return 'left'
            else:
                return 'right'
        if ydiff != 0:
            if ydiff > 0:
                return 'up'
            else:
                return 'down'
        print('first few game moves')
    else:
        return False


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '127.0.0.1'),
        port=os.getenv('PORT', '8080'))
