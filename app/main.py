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
    headtoheaddanger(me[0], snakes)

    if len(directions) == 2 or diagonaldanger(me, snakes):
        board = buildboard(me, snakes, width, height)
        zeros = countmatrix0(board)
        print('zeros: ' + str(zeros))

        headx = me[0]["x"]
        heady = me[0]["y"]

        leftlist = []
        rightlist = []
        uplist = []
        downlist = []
        leftsize = rightsize = upsize = downsize = 0
        for dir in directions:
            if dir == 'left':
                floodfill(board, headx-1, heady, width, height, leftlist)
                leftsize = len(leftlist)
            if dir == 'right':
                floodfill(board, headx+1, heady, width, height, rightlist)
                rightsize = len(rightlist)
            if dir == 'up':
                floodfill(board, headx, heady-1, width, height, uplist)
                upsize = len(uplist)
            if dir == 'down':
                floodfill(board, headx, heady+1, width, height, downlist)
                downsize = len(downlist)

        print(leftsize)
        print(rightsize)
        print(upsize)
        print(downsize)
        if leftlist and leftsize < len(me) + 2 and 'left' in directions:
            directions.remove('left')
            print('removing left, size: ' + str(leftsize))
        if rightlist and rightsize < len(me) + 2 and 'right' in directions:
            directions.remove('right')
            print('removing right, size: ' + str(rightsize))
        if uplist and upsize < len(me) + 2 and 'up' in directions:
            directions.remove('up')
            print('removing up, size: ' + str(upsize))
        if downlist and downsize < len(me) + 2 and 'down' in directions:
            directions.remove('down')
            print('removing down, size: ' + str(downsize))

    if directions:
        direction = random.choice(directions)
    else:
        print('Goodbye cruel world')
        taunt = 'MICHAEL!!!!!!'
        direction = 'up'

    return {
        'move': direction,
        'taunt': taunt
    }


def printmatrix(matrix):
    for x in range(len(matrix)):
        print(matrix[x])


def floodfill(matrix, x, y, width, height, list):
    """returns a flood filled board from a given point. ALL X AND Y ARE IN REFERENCE TO BOARD COORDS"""
    if matrix[x][y] == 0:
        matrix[x][y] = 1
        list.append(1)

        if x > 0:
            floodfill(matrix, x-1, y, width, height, list)
        if x < width-1:
            floodfill(matrix, x+1, y, width, height, list)
        if y > 0:
            floodfill(matrix, x, y-1, width, height, list)
        if y < height-1:
            floodfill(matrix, x, y+1, width, height, list)


def countmatrix0(matrix):
    count = 0
    for x in range(len(matrix)):
        for y in range(len(matrix[x])):
            if matrix[x][y] == 0:
                count += 1

    return count


def buildboard(me, snakes, width, height):
    matrix = [[0] * height for _ in range(width)]

    for point in me[:-1]:  # cut off last tile of tail since it will be moved for next turn
        x = point['x']
        y = point['y']
        matrix[x][y] = 1

    for snake in snakes['data']:
        for bodypart in snake['body']['data']:
            x = bodypart['x']
            y = bodypart['y']
            matrix[x][y] = 1

    return matrix


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

    for x in me[:-1]: # it is ok to move where the last point in our tail is
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


def headtoheaddanger(head, snakes):
    """will remove spaces if it will potentially go head to head with a bigger snake"""
    global directions
    leftpoints = []
    rightpoints = []
    uppoints = []
    downpoints = []
    for direction in directions:
        if direction == 'left':
            leftpoints = getadjpoints(getleft(head))
        if direction == 'right':
            rightpoints = getadjpoints(getright(head))
        if direction == 'up':
            uppoints = getadjpoints(getup(head))
        if direction == 'down':
            downpoints = getadjpoints(getdown(head))

    for snake in snakes['data']:
        if not snake['body']['data'] == head and snake['body']['data'][0] in leftpoints:
            print('removing left for head to head danger')
            directions.remove('left')
    for snake in snakes['data']:
        if not snake['body']['data'] == head and snake['body']['data'][0] in rightpoints:
            print('removing right for head to head danger')
            directions.remove('right')
    for snake in snakes['data']:
        if not snake['body']['data'] == head and snake['body']['data'][0] in uppoints:
            print('removing up for head to head danger')
            directions.remove('up')
    for snake in snakes['data']:
        if not snake['body']['data'] == head and snake['body']['data'][0] in downpoints:
            print('removing down for head to head danger')
            directions.remove('down')



#
#
# Below here are utility functions
#
#

def isdiagonal(a, b):
    ax = a["x"]
    ay = a["y"]
    bx = b["x"]
    by = b["y"]

    if abs(ax - bx) == 1 and abs(ay - by) == 1:
        return True
    else:
        return False


def diagonaldanger(me, snakes):
    """returns true if there is a dangerous point diagonal of the point"""
    head = me[0]

    for snake in snakes['data']:
        for bodypart in snake['body']['data']:
            if isdiagonal(head, bodypart):
                return True

    for point in me[:-1]:
        if isdiagonal(head, point):
            return True

    return False


def dirtouchingsnake(point, me, snakes):
    """checks if the point is touching a snake, not including this snakes head or neck"""
    head = me[0]
    neck = me[1]

    dirs = []

    for snake in snakes['data']:
        for bodypart in snake['body']['data']:
            if bodypart not in me:
                adj = findadjacentdir(point, bodypart)
                if adj:
                    dirs.append(adj)

    return dirs


def istouchingself(point, me):
    """checks if a point is touching this snake, not including head or neck"""
    self = me[2:]

    for x in self:
        if isadjacentdiagonal(point, x):
            return x

    return False


def dirtouchingself(point, me):
    """checks if a point is touching this snake, not including head or neck"""
    dirs = []

    for x in me:
        dir = findadjacentdir(point, x)
        if dir:
            dirs.append(dir)

    return dirs


def dirtouchingwall(point, width, height):
    """returns direction of wall if any"""
    walls = []
    if point['x'] == 0:
        walls.append('left')
    if point['x'] == width - 1:
        walls.append('right')
    if point['y'] == 0:
        walls.append('up')
    if point['y'] == height - 1:
        walls.append('down')

    return walls


def getadjpoints(point):
    """returns point objects of all of the adjacent points of a given point"""
    points = []
    points.append(getleft(point))
    points.append(getright(point))
    points.append(getup(point))
    points.append(getdown(point))
    return points


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

    if xdiff in range(-1, 2) and ydiff in range(-1, 2):
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
