# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 22:58:14 2020

@author: sctap
"""
def getmovefact(move):
    return move[0]
def getmovecolor(move):
    return move[1]
def getmovebucket(move):
    return move[2]
def LegalMoves(game, playerboard):
    for faind in range(len(game.factories) + 1):
        for co in range(game.size):
            for buind in range(game.size):
                if isLegal(faind, co, buind, game, playerboard):
                    yield (faind, co, buind)
            if isLegal(faind, co, "N", game, playerboard):
                yield (faind, co, "N")
def move(factory, color, bucket):
    return (factory, color, bucket)
    
def aimove(playerboard, oppboard, factories, floor, game, midtake=False, depth=3):
    m = None
    mv = -float("inf")
    a = -float("inf")
    b = float("inf")
    for move in LegalMoves(game, playerboard):
        successor, nextpb, noppb, nmidtake = game.generatesuccessor(move, playerboard, midtake)
        v = value(successor, nextpb, noppb, nmidtake, depth, a, b)
        if v >= mv:
            mv = v
            m = move
        a = max(a, v)
    return m
def value(game, playerboard, oppboard, midtake, depth, a, b):
    #if playerboard == game.board0:
    #    depth = depth - 1
    depth = depth - 1
    if playerboard.isendstate() or oppboard.isendstate():
        return evaluation(game, playerboard)
    elif depth == 0:
        return evaluation(game, playerboard)
    elif playerboard == game.board0:
        return maxp0(game, playerboard, oppboard, midtake, depth, a, b)
    else:
        return minp1(game, playerboard, oppboard, midtake, depth, a, b)
def maxp0(game, playerboard, oppboard, midtake, depth, a, b):
    v = -float("inf")
    for move in LegalMoves(game, playerboard):
        successor, nextpb, noppb, nmidtake = game.generatesuccessor(move, playerboard, midtake)
        v = max(v, value(successor, nextpb, noppb, nmidtake, depth, a, b))
        if v > b:
            return v
        a = max(a, v)
    return v
    
def minp1(game, playerboard, oppboard, midtake, depth, a, b):
    v = float("inf")
    for move in LegalMoves(game, playerboard):
        successor, nextpb, noppb, nmidtake = game.generatesuccessor(move, playerboard, midtake)
        v = min(v, value(successor, nextpb, noppb, nmidtake, depth, a, b))
        if v < a:
            return v
        b = min(b, v)
    return v    
def evaluation(game, playerboard):
    if game.board0.isendstate() or game.board1.isendstate():
        if game.board0.points > game.board1.points:
            return float("inf")
        elif game.board0.points < game.board1.points:
            return -float("inf")
        elif game.board0.countrows() > game.board1.countrows():
            return float("inf")
        elif game.board0.countrows() < game.board1.countrows():
            return -float("inf")
    game.board0.bonuspoints()
    game.board1.bonuspoints()
    pointspread = game.board0.points - game.board1.points
    b04ofac = game.board0.countxofacolor(4)
    b04col = game.board0.countcolumnsofx(4)
    b04row = game.board0.countrowsofx(4)
    b14ofac = game.board1.countxofacolor(4)
    b14col = game.board1.countcolumnsofx(4)
    b14row = game.board1.countrowsofx(4)
    b0bucketsfull = sum([bu.isfull() for bu in game.board0.buckets.values()])
    b1bucketsfull = sum([bu.isfull() for bu in game.board1.buckets.values()])
    pointspread += b0bucketsfull * max(b04col, b04row, game.board0.countrows(), game.board0.countcolumns(), 1)
    pointspread -= b1bucketsfull * max(b14col, b14row, game.board1.countrows(), game.board1.countcolumns(), 1)
    pointspread += b0bucketsfull * 2 * (b04row / 5)
    pointspread += b0bucketsfull * 7 * (b04col / 5)
    pointspread += b0bucketsfull * 10 * (b04ofac / 5)
    pointspread -= b1bucketsfull * 2 * (b14row / 5)
    pointspread -= b1bucketsfull * 7 * (b14col / 5)
    pointspread -= b1bucketsfull * 10 * (b14ofac / 5)
    numdisc = len(game.board0.subtracts)
    if numdisc < 3:
        pointdisc = 1 * numdisc
    elif numdisc < 6:
        pointdisc = 2 + (2 * (numdisc - 2))
    else:
        pointdisc = 8 + (3 * (numdisc - 5))
    pointspread -= pointdisc
    numdisc1 = len(game.board1.subtracts)
    if numdisc < 3:
        pointdisc1 = 1 * numdisc1
    elif numdisc < 6:
        pointdisc1 = 2 + (2 * (numdisc1 - 2))
    else:
        pointdisc1 = 8 + (3 * (numdisc1 - 5))
    pointspread += pointdisc1
    return pointspread
def isLegal(faind, color, bucket, game, playerboard):
    if faind == len(game.factories):
        fact = game.middle
    else:
        fact = game.factories[faind]
    if not fact.isempty() and fact.contains(color):
        if bucket == "N":
            return True
        bucketcol = playerboard.buckets[bucket].getcolor()
        if bucketcol != None and bucketcol != color:
            return False
        for tile in playerboard.tiles[bucket]:
            if tile.getcolor() == color and tile.isfull():
                return False
            elif tile.getcolor() == color:
                return True
        
    else:
        return False