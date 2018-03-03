import bottle
import os
import random
import copy
import math

directions = ['up', 'down', 'left', 'right']
instadeath = []
danger = {}

quotes = [
    # 'R is the most menacing sound in the English language. That\'s why it\'s called murder and not mukduk',
    'Bears, Beets, Battlestar Galactica',
    'The eyes are the groin of the head',
    # 'In an ideal world I would have all ten fingers on my left hand and the right one would just be left for punching',
    'I am fast. I am somewhere between a snake and a mongoose... And a panther',
    'D.W.I.G.H.T - Determined, Worker, Intense, Good worker, Hard worker, Terrific',
    'Through concentration, I can raise and lower my cholesterol at will'
]

taunt = 'Bears, Beets, Battlestar Galactica'

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

    taunt = 'D.W.I.G.H.T - Determined, Worker, Intense, Good worker, Hard worker, Terrific'

    head_url = '%s://%s/static/dwight.png' % (
        bottle.request.urlparts.scheme,
        bottle.request.urlparts.netloc
    )

    return {
        'color': '#ffcc00',
        'head_url': head_url,
        'name': 'Dwight Snake',
        'taunt': taunt,
        'head_type': 'safe',
        'tail_type': 'round-bum'
    }


@bottle.post('/move')
def move():
    global directions
    global danger
    global instadeath

    directions = ['up', 'down', 'left', 'right']
    data = bottle.request.json

    snakes = data['snakes']
    height = data['height']
    width = data['width']
    food = data['food']

    me = data['you']['body']['data']
    mylength = data['you']['length']
    myhealth = data['you']['health']

    donthitsnakes(me[0], snakes)
    donthitwalls(me, width, height)
    donthittail(me)
    avoidheadtohead(me[0], mylength, snakes)

    if len(directions) == 2 or diagonaldanger(me, snakes):
        print('doing flood fill checks')
        board = buildboard(me, snakes, width, height)
        zeros = countmatrix0(board)
        # print('zeros: ' + str(zeros))

        headx = me[0]["x"]
        heady = me[0]["y"]

        leftlist = []
        rightlist = []
        uplist = []
        downlist = []
        leftsize = rightsize = upsize = downsize = 0
        for dir in directions:
            # print('headx: ' + str(headx) + ' heady: ' + str(heady))
            if dir == 'left':
                # print('flood fill on left, x ' + str(headx-1) + ' y: ' + str(heady))
                floodfill(board, headx-1, heady, width, height, leftlist)
                leftsize = len(leftlist)
            if dir == 'right':
                # print('flood fill on right, x ' + str(headx+1) + ' y: ' + str(heady))
                floodfill(board, headx+1, heady, width, height, rightlist)
                rightsize = len(rightlist)
            if dir == 'up':
                # print('flood fill on up, x ' + str(headx) + ' y: ' + str(heady-1))
                floodfill(board, headx, heady-1, width, height, uplist)
                upsize = len(uplist)
            if dir == 'down':
                # print('flood fill on down, x ' + str(headx) + ' y: ' + str(heady+1))
                floodfill(board, headx, heady+1, width, height, downlist)
                downsize = len(downlist)

        print(leftsize)
        print(rightsize)
        print(upsize)
        print(downsize)
        if leftlist and leftsize < len(me) + 2 and 'left' in directions:
            if 'left' not in danger.keys() or ('left' in danger.keys() and danger['left'] < leftsize):
                danger['left'] = leftsize
            directions.remove('left')
            # print('removing left, size: ' + str(leftsize))
        if rightlist and rightsize < len(me) + 2 and 'right' in directions:
            if 'right' not in danger.keys() or ('right' in danger.keys() and danger['right'] < rightsize):
                danger['right'] = rightsize
            directions.remove('right')
            # print('removing right, size: ' + str(rightsize))
        if uplist and upsize < len(me) + 2 and 'up' in directions:
            if 'up' not in danger.keys() or ('up' in danger.keys() and danger['up'] < upsize):
                danger['up'] = upsize
            directions.remove('up')
            # print('removing up, size: ' + str(upsize))
        if downlist and downsize < len(me) + 2 and 'down' in directions:
            if 'down' not in danger.keys() or ('down' in danger.keys() and danger['down'] < downsize):
                danger['down'] = downsize
            directions.remove('down')
            # print('removing down, size: ' + str(downsize))

    print(danger)
    fooddir = []
    if myhealth < 80:
        closestfood = findclosestfood(me, food)
        fooddir = dirtopoint(me, closestfood)

    taunt = 'D.W.I.G.H.T - Determined, Worker, Intense, Good worker, Hard worker, Terrific'
    if directions:
        direction = random.choice(directions)
        if fooddir:
            for x in fooddir:
                if x in directions:
                    direction = x
                    break
    else:
        taunt = 'MICHAEL!!!!!!'
        direction = 'up'
        safest = 0
        # print('We are in danger, here is the direction dict:')
        # print(directions)
        # print('We are in danger, here is the danger dict:')
        # print(danger)
        for key, value in danger.items():
            if value > safest and key not in instadeath:
                safest = value
                direction = key

    instadeath = []
    return {
        'move': direction,
        'taunt': taunt
    }


#
# KENDRAS CODE

def dirtopoint(me, foodpoint):
    """Returns array of directions to foodpoint"""
    global directions
    head = me[0]
    xdiff = abs(head['x'] - foodpoint['x'])
    ydiff = abs(head['y'] - foodpoint['y'])

    newlist = []
    if xdiff >= ydiff and head['x'] - foodpoint['x'] >= 0:
        newlist.append('left')

    if xdiff >= ydiff and head['x'] - foodpoint['x'] < 0:
        newlist.append('right')

    if xdiff < ydiff and head['y'] - foodpoint['y'] >= 0:
        newlist.append('up')

    if xdiff < ydiff and head['y'] - foodpoint['y'] < 0:
        newlist.append('down')

    return newlist


def findclosestfood(me, food):
    """Returns point of food piece that is closest to snake"""
    head = me[0]
    distance = findpointdistance(head, food['data'][0])
    closestfood = food['data'][0]

    for pieceoffood in food['data']:
        if findpointdistance(head, pieceoffood) < distance:
            closestfood = pieceoffood
            distance = findpointdistance(head, pieceoffood)

    return closestfood


def findpointdistance(a, b):
    """Used to find the closest food"""

    xdiff = a['x'] - b['x']
    ydiff = a['y'] - b['y']

    distance = math.sqrt(xdiff**2 + ydiff**2)

    return distance


def closestsnaketofood(me, snakes, food):
    head = me[0]
    for pieceoffood in food['data']:
        for snake in snakes:
            if findpointdistance(head, pieceoffood) >= findpointdistance(snake['body']['data']['0'], pieceoffood):
                return False
    return True

## END KENDRAS CODE



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


# # TODO This is still picking up non dangerous things as danger, and the diagonal stuff isn't working
# def adjacenttodanger(point, me, snakes, width, height):
#     """Checks if point is adjacent to snakes, edge of board, or itself(not neck/head) including diagonally"""
#     if istouchingwall(point, width, height):
#         print('touching wall')
#         return True
#     if istouchingsnake(point, me, snakes):
#         print('touching snake')
#         return True
#     if istouchingself(point, me):
#         print('touching self')
#         return True

def donthitsnakes(head, snakes):
    """goes through entire snake array and stops it from directly hitting any snakes"""
    global directions
    global instadeath

    for snake in snakes['data']:
        for bodypart in snake['body']['data']:
            adj = findadjacentdir(head, bodypart)
            if adj and adj in directions:
                directions.remove(adj)
            if adj and adj not in instadeath:
                instadeath.append(adj)


def donthittail(me):
    """Stops the snake from hitting it's own tail(anything past its head and neck)"""
    global directions
    global instadeath

    head = me[0]

    for x in me[:-1]: # it is ok to move where the last point in our tail is
        adj = findadjacentdir(head, x)
        if adj and adj in directions:
            directions.remove(adj)
        if adj and adj not in instadeath:
            instadeath.append(adj)


def donthitwalls(me, width, height):
    """Stops the snake from hitting any walls"""
    global directions
    global instadeath

    head = me[0]

    if head['x'] == 0:
        if 'left' in directions:
            directions.remove('left')
        if 'left' not in instadeath:
            instadeath.append('left')
    if head['x'] == width-1:
        if 'right' in directions:
            directions.remove('right')
        if 'right' not in instadeath:
            instadeath.append('right')
    if head['y'] == 0:
        if 'up' in directions:
            directions.remove('up')
        if 'up' not in instadeath:
            instadeath.append('up')
    if head['y'] == height-1:
        if 'down' in directions:
            directions.remove('down')
        if 'down' not in instadeath:
            instadeath.append('down')


def avoidheadtohead(head, mylength, snakes):
    global directions
    global danger
    myadj = getadjpoints(head)

    othersnakeadj = []
    for snake in snakes['data']:
        if snake['body']['data'][0] != head and snake['length'] >= mylength:
            snakeadjpts = getadjpoints(snake['body']['data'][0])
            for z in snakeadjpts:
                othersnakeadj.append(z)

    for x in myadj:
        for y in othersnakeadj:
            if x == y:
                dir = findadjacentdir(head, x)
                if dir not in danger:
                    # print('adding ' + str(dir) + 'to danger array with value ' + str(mylength+1))
                    danger[dir] = mylength+1
                if dir and dir in directions:
                    # print('head to head, removing ' + dir)
                    directions.remove(dir)


#
#
# Below here are utility functions
#
#


def getadjpoints(point):
    """returns point objects of all of the adjacent points of a given point"""
    superduperpoint = copy.deepcopy(point)
    # print('Point: ')
    # print(superduperpoint)

    left = copy.deepcopy(superduperpoint)
    left['x'] = left['x']-1
    # print('left:')
    # print(left)

    right = copy.deepcopy(superduperpoint)
    right['x'] = right['x']+1
    # print('right:')
    # print(right)

    up = copy.deepcopy(superduperpoint)
    up['y'] = up['y']-1
    # print('up')
    # print(up)

    down = copy.deepcopy(superduperpoint)
    down['y'] = down['y']+1
    # print('down')
    # print(down)

    points = [left, right, up, down]
    # print(points)
    return points


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
                print('There is danger diagonally')
                return True

    for point in me[:-1]:
        if isdiagonal(head, point):
            print('There is danger diagonally')
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
    newpoint = point
    newpoint['x'] = point['x']-1
    return newpoint


def getright(point):
    newpoint = point
    newpoint['x'] = point['x']+1
    return newpoint


def getup(point):
    newpoint = point
    newpoint['y'] = point['y']-1
    return newpoint


def getdown(point):
    newpoint = point
    newpoint['y'] = point['y']+1
    return newpoint


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '127.0.0.1'),
        port=os.getenv('PORT', '8080'))
