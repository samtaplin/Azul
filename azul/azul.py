# -*- coding: utf-8 -*-
"""
Created on Mon Dec 23 19:59:57 2019

@author: Sam Taplin
"""
import random
"""Takes in manual input and returns the move chosen by the player"""
def decidemove(playerboard, oppboard, factories, floor):
    chfact = input("Which factory do you want to pull from? (enter 'middle' for the middle, 1-5 for the others)")
    chcolor = input("Which color do you want to take?")
    buck = input("Which bucket do you want to place it in? (1 for the smallest bucket, 5 fot the biggest)")
    if chfact == 'middle':
        chfact = floor
    else:
        chfact = factories[int(chfact) - 1]
    chcolor = int(chcolor)
    buck = int(buck) - 1
    return chfact, chcolor, playerboard.buckets[buck]
"""A game of Azul. Includes the bag of tiles, the boards for each player and the factories that hold the tiles."""
class Game:
    def __init__(self, size, players):
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
    def taketurn2(self):
        currbo = self.goesfirst
        oppbo = self.other2(currbo)
        first = None
        while any([not fact.isempty() for fact in self.factories]) or not self.middle.isempty():
            print("Factories:")
            for i in range(len(self.factories)):
                print(i + 1)
                print(self.factories[i])
            print("Middle:")
            print(self.middle)
            print("Opponent's board:")
            print(oppbo)
            print("Your board:")
            print(currbo)
            factory, color, bucket = decidemove(currbo, oppbo, self.factories, self.middle)
            if not first and factory == self.middle:
                first = currbo
                currbo.points = currbo.points - 1
            draw, tomid = factory.draw(color)
            self.middle.drop(tomid)
            excess = bucket.insert(color, len(draw))
            currbo.subtracts.extend(excess)
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
    def playgame(self):
        over = False
        while not over:
            over = self.taketurn2()
            print("Player 0 points:")
            print(self.board0.points)
            print("Player 1 points:")
            print(self.board1.points)
            for fact in self.factories:
                fact.fill(self.bag.drawfour())

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
    """Returns True if the factory is empty. False if not."""
    def isempty(self):
        return not self.tiles
    def __str__(self):
        if self.isempty():
            return "|||X|||"
        else:
            return "<" + str([str(tile) for tile in self.tiles]) + ">"

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
    """Copies another board into this board."""
    def copy(self, board):
        self.tiles = board.tiles
        self.size = board.size
        self.buckets = board.buckets
        self.subtracts = board.subtracts
        self.points = board.points
    """Counts the number of filled columns in the board."""
    def countcolumns(self):
        full = 0
        for i in range(self.size):
            if all([row[i].isfull() for row in self.tiles]):
                full += 1
        return full
    """Counts the number of filled rows in the board."""
    def countrows(self):
        full = 0
        for row in self.tiles:
            if all([tile.isfull() for tile in row]):
                full += 1
        return full
    """Returns the number of sets of a color filled in a board."""
    def countofacolor(self):
        full = 0
        for i in range(self.size):
            colfl = 0
            for j in range(self.size):
                tile = self.tiles[j][(j + i) % self.size]
                if tile.isfull():
                    colfl += 1
            if colfl == self.size:
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
                todiscard.extend([Tile(bcolor)] * (i - 1))
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
        numdisc = len(todiscard)
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
        return "Buckets: " + str([str(self.buckets[i]) for i in range(self.size)]) + "\n Tiles: \n" + rows[0] + rows[1] + rows[2] + rows[3] + rows[4]
                
class Tile:
    def __init__(self, color):
        self.color = color
    """Returns the color of the tile."""
    def getcolor(self):
        return self.color
    def __repr__(self):
        return '|' + str(self.color) + "|"
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
            self.holds = self.size
            self.color = color
            return [Tile(self.color)] * (self.holds + amount - self.size)
    """Return the number of tiles currently in the bucket."""
    def getholds(self):
        return self.holds
    """Returns the color of the tiles in the bucket."""
    def getcolor(self):
        return self.color
    def __str__(self):
        return "|_" + str(self.color) * self.holds + "X" * (self.size - self.holds)

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
class GameError(Exception):
    def __init__(self, message):
        self.message = message
        
g = Game(5, 2)
g.playgame()
        