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
        # Need to do something here to handle the not going inside on itself
        print('danger zone')
        left = True
        right = True
        up = True
        down = True

        for x in directions:
            if x == 'left':
                left = checkenclosed(getleft(me[0]), me, snakes, width, height, len(me))
            if x == 'right':
                right = checkenclosed(getright(me[0]), me, snakes, width, height, len(me))
            if x == 'up':
                up = checkenclosed(getup(me[0]), me, snakes, width, height, len(me))
            if x == 'right':
                down = checkenclosed(getdown(me[0]), me, snakes, width, height, len(me))

        if not left and 'left' in directions:
            directions.remove('left')
        if not right and 'right' in directions:
            directions.remove('right')
        if not up and 'up' in directions:
            directions.remove('up')
        if not down and 'down' in directions:
            directions.remove('down')

        print('left: ' + str(left))
        print('right: ' + str(right))
        print('up: ' + str(up))
        print('down: ' + str(down))

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


def donthitsnakes(head, snakes):
    """goes through entire snake array and stops it from directly hitting any snakes"""
    global directions

    for snake in snakes['data']:
        for bodypart in snake['body']['data']:
            adj = findadjacentdir(head, bodypart)
            if adj and adj in directions:
                directions.remove(adj)


def donthittail(me):
    """Stops the snake from hitting it's own tail(anything past its head and neck)"""
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


# TODO Check if there is food in the area, could make the snake longer and make you not fit
def checkenclosed(point, me, snakes, width, height, snakelength):
    """Returns true if the snake can fit in the space along an edge"""
    dirarray = ['up', 'down', 'left', 'right']

    dirarray = getlegalmoves(dirarray, me[0], me, snakes, width, height)
    print('Legal Moves:')
    print(dirarray)

    if snakelength > 0:
        if 'left' in dirarray:
            left = getleft(point)
            if adjacenttodanger(left, me, snakes, width, height):
                checkenclosed(left, me, snakes, width, height, snakelength-1)
        if 'right' in dirarray:
            right = getright(point)
            if adjacenttodanger(right, me, snakes, width, height):
                checkenclosed(right, me, snakes, width, height, snakelength-1)
        if 'up' in dirarray:
            up = getup(point)
            if adjacenttodanger(up, me, snakes, width, height):
                checkenclosed(up, me, snakes, width, height, snakelength-1)
        if 'down' in dirarray:
            down = getdown(point)
            if adjacenttodanger(down, me, snakes, width, height):
                checkenclosed(down, me, snakes, width, height, snakelength-1)
    else:
        return True

    return False


def getlegalmoves(dirarray, head, me, snakes, width, height):
    # Don't hit other snakes
    for snake in snakes['data']:
        for bodypart in snake['body']['data']:
            adj = findadjacentdir(head, bodypart)
            if adj and adj in directions:
                dirarray.remove(adj)

    # Don't hit own tail
    for x in me:
        adj = findadjacentdir(head, x)
        if adj and adj in directions:
            dirarray.remove(adj)

    if head['x'] == 0:
        dirarray.remove('left')
    if head['x'] == width-1:
        dirarray.remove('right')
    if head['y'] == 0:
        dirarray.remove('up')
    if head['y'] == height-1:
        dirarray.remove('down')

    return dirarray


def adjacenttodanger(point, me, snakes, width, height):
    """Checks if point is adjacent to snakes, edge of board, or itself(not neck/head) including diagonally"""
    if istouchingwall(point, width, height):
        print('touching wall')
        return True
    if istouchingsnake(point, me, snakes):
        print('touching snake')
        return True
    if istouchingself(point, me):
        print('touching self')
        return True


def istouchingsnake(point, me, snakes):
    """checks if the point is touching a snake, not including this snakes head or neck"""
    head = me[0]
    neck = me[1]

    for snake in snakes['data']:
        for bodypart in snake['body']['data']:
            if bodypart not in me:
                adj = isadjacentdiagonal(point, bodypart)
                if adj:
                    return True

    return False


def istouchingself(point, me):
    """checks if a point is touching this snake, not including head or neck"""
    self = me[2:]

    for x in self:
        adj = findadjacentdir(point, x)
        if adj:
            return True

    return False


def istouchingwall(point, width, height):
    """returns true if the point is adjacent to a wall"""
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

    if xdiff in range(-1, 1) and ydiff in range(-1, 1):
        return True
    else:
        return False


def getleft(point):
    point['x'] -= 1
    return point


def getright(point):
    point['x'] += 1
    return point


def getup(point):
    point['y'] -= 1
    return point


def getdown(point):
    point['y'] += 1
    return point

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '127.0.0.1'),
        port=os.getenv('PORT', '8080'))
