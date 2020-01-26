# -*- coding: utf-8 -*-
"""
Created on Mon Dec 23 19:59:57 2019

@author: Sam Taplin
"""
import random
import decision
"""Takes in manual input and returns the move chosen by the player"""
def decidemove(playerboard, oppboard, factories, floor, game, midtake):
    chfact = input("Which factory do you want to pull from? (enter 'middle' for the middle, 1-5 for the others)")
    chcolor = input("Which color do you want to take?")
    buck = input("Which bucket do you want to place it in? (1 for the smallest bucket, 5 fot the biggest, N for discarding)")
    if chfact == 'middle':
        chind = len(factories)
        chfact = floor
    else:
        chind = int(chfact) - 1
        chfact = factories[int(chfact) - 1]
    chcolor = int(chcolor)
    if buck != "N":
        buck = int(buck) - 1
        if decision.isLegal(chind, chcolor, buck, game, playerboard):
            return chfact, chcolor, playerboard.buckets[buck]
        else:
            print("Cannot perform illegal move")
            return decidemove(playerboard, oppboard, factories, floor, game, midtake)
    else:
        if decision.isLegal(chind, chcolor, buck, game, playerboard):
            return chfact, chcolor, buck
        else:
            print("Cannot perform illegal move")
            return decidemove(playerboard, oppboard, factories, floor, game, midtake)
"""A game of Azul. Includes the bag of tiles, the boards for each player and the factories that hold the tiles."""
class Game:
    def __init__(self, size, players):
        self.size = size
        self.bag = Bag(size)
        self.players = players
        self.board0 = Board(size)
        self.goesfirst = self.board0
        self.board1 = Board(size)
        self.factories = []
        for _ in range(5):
            self.factories.append(Factory())
        if self.players > 2:
            self.board2 = Board(size)
            for _ in range(2):
                self.factories.append(Factory())
        if self.players == 4:
            self.board3 = Board(size)
            for _ in range(2):
                self.factories.append(Factory())
        self.middle = MiddleFactory()
        self.discard = []
        for fact in self.factories:
            fact.fill(self.bag.drawfour())
    """Takes in a player in a two person game and returns the next player to move."""
    def other2(self, player):
        if player == self.board0:
            return self.board1
        else:
            return self.board0
    """Completes a turn for the current player in a two-player game. Returns True if the game ends."""
    def taketurn2(self, p0movechoice, p1movechoice):
        currbo = self.goesfirst
        oppbo = self.other2(currbo)
        first = None
        while any([not fact.isempty() for fact in self.factories]) or not self.middle.isempty():
            if currbo == self.board0:
                thismove = p0movechoice
            else:
                thismove = p1movechoice
            print("Factories:")
            for i in range(len(self.factories)):
                print(i + 1)
                print(self.factories[i])
            print("Middle:")
            print(self.middle)
            print("Opponent's board:", oppbo.points)
            print(oppbo)
            print("Your board:", currbo.points)
            print(currbo)
            if not first:
                factory, color, bucket = thismove(currbo, oppbo, self.factories, self.middle, self, False)
            else:
                factory, color, bucket = thismove(currbo, oppbo, self.factories, self.middle, self, True)
            if not first and factory == self.middle or factory == len(self.factories):
                first = currbo
                currbo.points = currbo.points - 1
                print(currbo.points)
            if type(factory) == int:
                if factory == len(self.factories):
                    factory = self.middle
                else:
                    factory = self.factories[factory]
            if type(bucket) == int:
                bucket = currbo.buckets[bucket]
            draw, tomid = factory.draw(color)
            self.middle.drop(tomid)
            if bucket != "N":
                excess = bucket.insert(color, len(draw))
                currbo.subtracts.extend(excess)
            else:
                currbo.subtracts.extend(draw)
            oppbo = currbo
            currbo = self.other2(currbo)
        b0disc = self.board0.emptybuckets()
        b1disc = self.board1.emptybuckets()
        self.bag.adddiscard(b0disc)
        self.bag.adddiscard(b1disc)
        self.goesfirst = first
        if self.board0.isendstate() or self.board1.isendstate():
            self.board0.bonuspoints()
            self.board1.bonuspoints()
            print("Final Score: Player1-", self.board0.points, "Player2-", self.board1.points)
            return True
        else:
            return False
    """Plays this game instance into completion."""
    def playgame(self, p0movechoice, p1movechoice):
        over = False
        while not over:
            over = self.taketurn2(p0movechoice, p1movechoice)
            print("Player 0 points:")
            print(self.board0.points)
            print("Player 1 points:")
            print(self.board1.points)
            for fact in self.factories:
                fact.fill(self.bag.drawfour())
                
    def generatesuccessor(self, move, player, midtake):
        copy = Game(self.size, self.players)
        copy.bag = self.bag.createcopy()
        copy.board0 = self.board0.createcopy()
        copy.board1 = self.board1.createcopy()
        if self.goesfirst == self.board0:
            copy.goesfirst = copy.board0
        else:
            copy.goesfirst = copy.board1
        for i in range(len(self.factories)):
            copy.factories[i] = self.factories[i].createcopy()
        copy.middle = self.middle.createcopy()
        for tile in self.discard:
            copy.discard.append(tile.createcopy())
        if player == self.board0:
            cplayer = copy.board0
        else:
            cplayer = copy.board1
        color = decision.getmovecolor(move)
        faind = decision.getmovefact(move)
        if not midtake and faind == len(self.factories):
            copy.goesfirst = cplayer
            cplayer.points = cplayer.points - 1
            midtake = True
        if faind == len(self.factories):
            draw, tomid = copy.middle.draw(color)
        else:
            draw, tomid = copy.factories[faind].draw(color)
        copy.middle.drop(tomid)
        bucket = decision.getmovebucket(move)
        if bucket != "N":
            excess = cplayer.buckets[bucket].insert(color, len(draw))
            cplayer.subtracts.extend(excess)
        else:
            cplayer.subtracts.extend(draw)
        if all([fact.isempty() for fact in copy.factories]) and copy.middle.isempty():
            b0disc = copy.board0.emptybuckets()
            b1disc = copy.board1.emptybuckets()
            copy.bag.adddiscard(b0disc)
            copy.bag.adddiscard(b1disc)
            if copy.board0.isendstate() or copy.board1.isendstate():
                copy.board0.bonuspoints()
                copy.board1.bonuspoints()
            return copy, copy.goesfirst, copy.other2(copy.goesfirst), False
        return copy, copy.other2(cplayer), cplayer, midtake
        

class Factory:
    def __init__(self):
        self.tiles = []
    """Draws all times of a particular color from a factory. Takes in a color and returns
    a list of tiles drawn and a list of tiles that are placed in the middle of the game."""
    def draw(self, color):
        thedraw = []
        thedrop = []
        for tile in self.tiles:
            if tile.getcolor() == color:
                thedraw.append(tile)
            else:
                thedrop.append(tile)
        self.tiles = []
        return thedraw, thedrop
    """Takes in a list of four tiles and fills the factory with them."""
    def fill(self, tiles):
        if len(tiles) == 4:
            self.tiles = tiles
        else:
            raise GameError("Wrong number of tiles for a factory")
    """Takes in a color and returns True if the factory contains at lease one tile of that color"""
    def contains(self, color):
        for tile in self.tiles:
            if tile.getcolor() == color:
                return True
        return False
    """Returns True if the factory is empty. False if not."""
    def isempty(self):
        return not self.tiles
    def __str__(self):
        if self.isempty():
            return "|||X|||"
        else:
            return "<" + str([str(tile) for tile in self.tiles]) + ">"
    
    def createcopy(self):
        copy = Factory()
        for tile in self.tiles:
            tcop = tile.createcopy()
            copy.tiles.append(tcop)
        return copy

class MiddleFactory(Factory):
    """Draws all tiles of a color from the factory. Takes in a color and returns a list of tiles
    drawn and an empty list of tiles."""
    def draw(self, color):
        thedraw = []
        thedrop = []
        for tile in self.tiles:
            if tile.getcolor() == color:
                thedraw.append(tile)
            else:
                thedrop.append(tile)
        self.tiles = thedrop
        return thedraw, []
    """Takes in a list of tiles of any length and adds it to the middle factory."""
    def drop(self, tiles):
        self.tiles.extend(tiles)
    def fill(self, tiles):
        raise GameError("Can't fill the middle of the floor")
    def createcopy(self):
        copy = MiddleFactory()
        for tile in self.tiles:
            tcop = tile.createcopy()
            copy.tiles.append(tcop)
        return copy
class Board:
    
    def __init__(self, size):
        self.tiles = []
        self.size = size
        self.buckets = {}
        self.subtracts = []
        self.points = 0
        for i in range(size):
            row = []
            for j in range(size):
                row.append(BoardTile((j - i) % size))
            self.tiles.append(row)
            self.buckets[i] = Bucket(i + 1)
    """Returns a copy of this board."""
    def createcopy(self):
        copy = Board(self.size)
        for i in range(self.size):
            for j in range(self.size):
                copy.tiles[i][j] = self.tiles[i][j].createcopy()
            copy.buckets[i] = self.buckets[i].createcopy()
        for tile in self.subtracts:
            copy.subtracts.append(tile.createcopy())
        copy.points = self.points
        return copy
    """Counts the number of filled columns in the board."""
    def countcolumns(self):
        return self.countcolumnsofx(self.size)
    def countcolumnsofx(self, x):
        full = 0
        for i in range(self.size):
            if sum([row[i].isfull() for row in self.tiles]) == x:
                full += 1
        return full
    """Counts the number of filled rows in the board."""
    def countrows(self):
        return self.countrowsofx(self.size)
    def countrowsofx(self, x):
        full = 0
        for row in self.tiles:
            if sum([tile.isfull() for tile in row]) == x:
                full += 1
        return full
    """Returns the number of sets of a color filled in a board."""
    def countofacolor(self):
        return self.countxofacolor(self.size)
    def countxofacolor(self, x):
        full = 0
        for i in range(self.size):
            colfl = 0
            for j in range(self.size):
                tile = self.tiles[j][(j + i) % self.size]
                if tile.isfull():
                    colfl += 1
            if colfl == x:
                full += 1
        return full
    """Adds bonus points to the board based on filled rows, columns and colors."""
    def bonuspoints(self):
        self.points += 2 * self.countrows() + 7 * self.countcolumns() + 10 * self.countofacolor()
    """Empties filled buckets at the end of turn, adding points to the board based on
    the rules of azul."""
    def emptybuckets(self):
        totalpoints = 0
        todiscard = []
        for i in range(self.size):
            bu = self.buckets[i]
            if bu.isfull():
                bcolor = bu.getcolor()
                bu.empty()
                col = (i + bcolor) % self.size
                todiscard.extend([Tile(bcolor)] * (i))
                self.tiles[i][col].fill()
                row = self.tiles[i]
                rowtot = 0
                for k in range(1, 5):
                    if col + k < self.size and row[col + k].isfull():
                        rowtot += 1
                    else:
                        break
                for k in range(1, 5):
                    if col - k >= 0 and row[col - k].isfull():
                        rowtot += 1
                    else:
                        break
                totalpoints += 1
                totalpoints += rowtot
                coltot = 0
                for k in range(1, 5):
                    if i + k < self.size and self.tiles[i + k][col].isfull():
                        coltot += 1
                    else:
                        break
                for k in range(1, 5):
                    if i - k >= 0 and self.tiles[i - k][col].isfull():
                        coltot += 1
                    else:
                        break
                totalpoints += coltot
                if rowtot > 0 and coltot > 0:
                    totalpoints += 1
        todiscard.extend(self.subtracts)
        numdisc = len(self.subtracts)
        if numdisc < 3:
            pointdisc = 1 * numdisc
        elif numdisc < 6:
            pointdisc = 2 + (2 * (numdisc - 2))
        else:
            pointdisc = 8 + (3 * (numdisc - 5))
        self.points += totalpoints
        self.points = self.points - pointdisc
        self.subtracts = []
        return todiscard
    """Returns True if the game is in a terminal state."""
    def isendstate(self):
        return self.countrows() > 0
    def __str__(self):
        rows = [str(row) + "\n" for row in self.tiles]
        rowstr = ""
        for row in rows:
            rowstr += row
        return "Buckets: " + str([str(self.buckets[i]) for i in range(self.size)]) + "\n Tiles: \n" + rowstr
                
class Tile:
    def __init__(self, color):
        self.color = color
    """Returns the color of the tile."""
    def getcolor(self):
        return self.color
    def __repr__(self):
        return '|' + str(self.color) + "|"
    def createcopy(self):
        return Tile(self.color)
class BoardTile(Tile):
    def __init__(self, color, filled=False):
        self.color = color
        self.filled = filled
    """Fills the tile."""
    def fill(self):
        self.filled = True
    "Unfills the tile."""
    def unfill(self):
        self.filled = False
    """Returns True if the tile is full."""
    def isfull(self):
        return self.filled
    def __repr__(self):
        if self.filled:
            return "|F" + str(self.color) + "|"
        else:
            return '|' + str(self.color) + "|"
    def createcopy(self):
        return BoardTile(self.color, self.filled)
class Bucket:
    def __init__(self, size):
        self.size = size
        self.holds = 0
        self.color = None
    """Returns True if the bucket is full."""
    def isfull(self):
        if self.size == self.holds:
            return True
        return False
    """Empties the bucket of tiles."""
    def empty(self):
        self.holds = 0
        self.color = None
    """Takes in AMOUNT tiles of COLOR. Inserts them into the bucket and returns a 
    list of excess tiles to be discarded."""
    def insert(self, color, amount):
        if self.size >= self.holds + amount and (self.color == color or not self.color):
            self.color = color
            self.holds = self.holds + amount
            return []
        elif self.color != color and self.color:
            return [Tile(color)] * amount
        elif self.size < self.holds + amount:
            held = self.holds
            self.holds = self.size
            self.color = color
            return [Tile(self.color)] * (held + amount - self.size)
    """Return the number of tiles currently in the bucket."""
    def getholds(self):
        return self.holds
    """Returns the color of the tiles in the bucket."""
    def getcolor(self):
        return self.color
    def __str__(self):
        return "|_" + str(self.color) * self.holds + "X" * (self.size - self.holds)
    def createcopy(self):
        copy = Bucket(self.size)
        if self.color != None:
            copy.insert(self.holds, self.color)
        return copy

class Bag:
    def __init__(self, size):
        self.squares = []
        self.discard = []
        for i in range(size):
            for _ in range(20):
                self.squares.append(Tile(i))
        random.shuffle(self.squares)
    """Returns a tile drawn from the bag."""
    def draw(self):
        if not self.isempty():
            return self.squares.pop()
        else:
            self.refill()
            return self.squares.pop()
    """Returns a list of four tiles drawn from the bag."""
    def drawfour(self):
        tiles = []
        for _ in range(4):
            tiles.append(self.draw())
        return tiles
    """Returns True if the bag is empty."""
    def isempty(self):
        return len(self.squares) == 0
    """Adds a list of tiles to the bag's discard."""
    def adddiscard(self, disc):
        self.discard.extend(disc)
    """Refills the draw pile of the bag with the tiles in its discard pile."""
    def refill(self):
        if len(self.squares) == 0:
            self.squares = self.discard
            random.shuffle(self.squares)
    
    def createcopy(self):
        copy = Bag(0)
        for tile in self.squares:
            copy.squares.append(tile.createcopy())
        for dtile in self.discard:
            copy.discard.append(dtile.createcopy())
        return copy
class GameError(Exception):
    def __init__(self, message):
        self.message = message

def main():
    option = input("Welcome to Azul! Enter 'AI' to play against the AI and 'MAN' to play against a manual player")
    g = Game(5, 2)
    if option == "AI":
        g.playgame(decision.aimove, decidemove)
    elif option == "MAN":
        g.playgame(decidemove, decidemove)
    else:
        main()
main()
        