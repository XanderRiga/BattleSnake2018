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

    head_url = '%s://%s/static/dwight.png' % (
        bottle.request.urlparts.scheme,
        bottle.request.urlparts.netloc
    )

    # TODO: Do things with data

    return {
        'color': '#ffcc00',
        'head_url': head_url,
        'name': 'Dwight Snake',
        'taunt': 'Bears, Beets, Battlestar Galactica',
        'head_type': 'safe',
        'tail_type': 'round-bum'
    }


@bottle.post('/move')
def move():
    global directions
    directions = ['up', 'down', 'left', 'right']
    taunt = 'Bears, Beets, Battlestar Galactica'
    data = bottle.request.json

    snakes = data['snakes']
    height = data['height']
    width = data['width']
    # food = data['food']

    me = data['you']['body']['data']

    donthitsnakes(me[0], snakes)
    donthitwalls(me, width, height)
    donthittail(me)

    if adjacenttodanger(me[0], me, snakes, width, height):
        print('danger zone')

    if directions:
        direction = random.choice(directions)
    else:
        print('Goodbye cruel world')
        taunt = 'MICHAEL!!!!!!'
        direction = 'up'

    # print(direction)
    return {
        'move': direction,
        'taunt': taunt
    }


def adjacenttodanger(point, me, snakes, width, height):
    """Checks if point is adjacent to snakes, edge of board, or itself(not neck/head) including diagonally"""
    if istouchingwall(point, width, height):
        print('touching wall')
        return True
    if istouchingsnake(point, me, snakes):
        print('touching snake')
        return True


def donthitsnakes(head, snakes):
    """goes through entire snake array and stops it from directly hitting other snakes"""
    global directions

    for snake in snakes['data']:
        for bodypart in snake['body']['data']:
            adj = findadjacentdir(head, bodypart)
            if adj and adj in directions:
                directions.remove(adj)


def donthittail(me):
    global directions
    head = me[0]

    for x in me:
        adj = findadjacentdir(head, x)
        if adj and adj in directions:
            directions.remove(adj)


def donthitwalls(me, width, height):
    """Stops the snake from hitting any walls"""
    global directions
    head = me[0]

    if head['x'] == 0:
        directions.remove('left')
    if head['x'] == width-1:
        directions.remove('right')
    if head['y'] == 0:
        directions.remove('up')
    if head['y'] == height-1:
        directions.remove('down')

#
#
# Below here are utility functions
#
#


def istouchingsnake(point, me, snakes):
    """checks if the point is touching a snake, not including this snakes head or neck"""
    # head = me[0]
    # neck = me[1]
    ignore = [me[0], me[1], me[2]]

    for snake in snakes['data']:
        for bodypart in snake['body']['data']:
            if bodypart not in ignore:
                adj = isadjacentdiagonal(point, bodypart)
                if adj:
                    print('Adjacent Points:')
                    print(point)
                    print(bodypart)
                    return True

    return False


def istouchingwall(point, width, height):
    if point['x'] == 0:
        return True
    if point['x'] == width - 1:
        return True
    if point['y'] == 0:
        return True
    if point['y'] == height - 1:
        return True

    return False


def findadjacentdir(a, b):
    """Gives direction from a to b if they are adjacent(not diagonal), if they are not adjacent returns false"""
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
    else:
        return False


def isadjacentdiagonal(a, b):
    """Returns true if a is adjacent to be(with diagonal), if they are not adjacent returns false"""
    ax = a['x']
    ay = a['y']
    bx = b['x']
    by = b['y']
    xdiff = ax - bx
    ydiff = ay - by

    if xdiff in range(-1, 2) or ydiff in range(-1, 2):
        return True
    else:
        return False


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '127.0.0.1'),
        port=os.getenv('PORT', '8080'))
