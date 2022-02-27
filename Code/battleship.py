#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# IMPORT declarations

import random
import re
import string
import sys


# CLASS declarations

class Player:

    def __init__(self, name):
        self.name = name
        self.create_boards()
        self.create_ships()
        print_separator()
        print(f"Player {self.name} created!\nNow positionning the ships...")
        display_board(self, self.lower_board)
        self.position_ships()
        self.hits_list = [] # Store Player's strikes

    # Create lower_board (displayed to player during positiong)
    # and upper_board (displayed to opponent during striking)
    def create_boards(self):
        self.lower_board = Board("game", "ships' board")
        self.upper_board = Board("game", "strikes' board")

    # Create the 5 ships with their model and size
    def create_ships(self):
        self.carrier = Ship("Carrier", 5)
        self.battleship = Ship("Battleship", 4)
        self.cruiser = Ship("Cruiser", 3)
        self.submarine = Ship("Submarine", 3)
        self.destroyer = Ship("Destroyer", 3)
        self.ships = [self.carrier, self.battleship, self.cruiser, self.submarine, self.destroyer]

    # For loop to position all the ships
    def position_ships(self):
        for ship in self.ships:
            if self.position_ship(ship):
                self.add_ship(ship)
            display_board(self, self.lower_board)
        return True

    # Take and check input (origin and direction of positioning) from player
    # Convert it into tuple of coordinates
    # Check if no overlap with another ship
    # Return True if all OK
    def position_ship(self, ship):
        print_separator()
        print(f"Placing {self.name}'s {ship.model} of size {ship.size}!\n")
        if not debug_mode:
            while True:
                position_input = check_input("Please enter the position with the format 'A1 r(ight)/d(own)'\nwhere A1 is the cell of origin and r/d is the direction: ", regex_pattern_position)
                if position_input:
                    break
        else:
            position_input = debug_pattern_position_ships[self.ships.index(ship)] # DEBUG
        position_input_tuple = convert_coords(position_input)
        ship.set_coords(position_input_tuple)
        if check_position_ship(self, ship):
            self.lower_board.update_filled_coords(ship.coords)
        else:
            self.position_ship(ship)
        return True

    # Add ship to board
    def add_ship(self, ship):
        self.lower_board.update_grid(ship, tuple(ship.origin), True)


class Ship:

    def __init__(self, model, size):
        self.model = model
        self.size = size
        self.life = size
        self.origin = []
        self.coords = []

    # Determine coords of all ship's cells
    # from origin = (coords_tuple[0], coords_tuple[1]) & direction = coords_tuple[2]
    def set_coords(self, coords_tuple):
        self.coords=[]
        # Ship positioned downwards
        if coords_tuple[2] == "down" or coords_tuple[2] == "d":
            for i in range(self.size):
                # Going down: increment line, same column
                self.coords.append((coords_tuple[0]+i, coords_tuple[1]))
        # By default the ship is positioned rightwards
        else:
            for i in range(self.size):
                # Going right: same line, increment column
                self.coords.append(((coords_tuple[0], coords_tuple[1]+i)))
        self.set_origin(self.coords)

    # Ship's origin cell is the first cell
    def set_origin(self, coords):
        self.origin = coords[0]


class Board:

    def __init__(self, board_type, board_name):
        self.name = board_name
        # Set the back-end system of coordinates as (0,0) - (9,9)
        if board_type == "base":
            self.grid = [(i,j) for i in range(10) for j in range(10)]
        # Players' boards to be displayed during the game
        elif board_type == "game":
            self.grid = [["-" for i in range(10)] for j in range(10)]
            self.filled_coords = []

    def update_grid(self, ship, coord, hit): # ship is optional for lower_board
        if hit and isinstance(ship, Ship):
            # Ship sunk by strike: display X for all ship.coords
            for ship_coord in ship.coords:
                self.grid[ship_coord[0]][ship_coord[1]] = "X"
        elif hit and not ship:
            # Ship hit but not sunk by strike: display *
            self.grid[coord[0]][coord[1]] = "*"
        else:
            # Strike falls into sea: display O
            self.grid[coord[0]][coord[1]] = "0"

    def update_filled_coords(self, coords):
        self.filled_coords.extend([tuple(coord) for coord in coords])


# FUNCTIONS declarations

# Interface functions

def print_separator():
    print("\n##########################################\n")

def print_rules():
    print("""
This is a 2-player guessing game.
Your goal is to sink all of your opponent's ships by correctly guessing their locations
before your opponent sinks all of yours.
First, each player must position their 5 ships on their 10x10 board grid.
Then, players take turns calling out row and column coordinates on the other player's grid
in an attempt to identify a square that contains a ship. A ship sunk once all of its squares are identified.
""")
    print("The base board looks as follows:\n")
    display_base_board()

def display_base_board():
    display_board_return = [" ".join(["-" for i in range(10)]) for j in range(10)]
    # Add column ref 1-10 with underline
    display_board_return.insert(0, " ".join([underline(str(i)) for i in range(1,10+1)]))
    # Add line ref A-J with underline
    display_board_return = [underline(list_coords_row[i]) + " " + display_board_return[i] for i in range(10+1)]
    print("\n".join(display_board_return))

def display_board(player, board_to_display):
    print(f"\n{player.name}: your {board_to_display.name}\n")
    display_board_return = [" ".join(board_to_display.grid[i]) for i in range(10)]
    # Add column ref 1-10 with underline
    display_board_return.insert(0, " ".join([underline(str(i)) for i in range(1,10+1)]))
    # Add line ref A-J with underline
    display_board_return = [underline(list_coords_row[i]) + " " + display_board_return[i] for i in range(10+1)]
    print("\n".join(display_board_return))

def underline(string):
    return '\033[4m' + string + '\033[0m'

# Check functions

# Print message, takes input, and checks if input follows exactly regex_rule (fullmatch)
def check_input(message, regex_rule):
    input_user = input(message).strip()
    if re.fullmatch(regex_rule, input_user):
        return input_user
    else:
        print("Incorrect entry, please retry.")
        return False

# Check if position of ship fits on the board and does not overlap with another ship
def check_position_ship(player, ship):
    for coord in ship.coords:
        if tuple(coord) not in base_board.grid:
            print("The ship would not fit on the board. Please retry.")
            return False
        if tuple(coord) in player.lower_board.filled_coords:
            print("The ship would overlap with another ship. Please retry.")
            return False
    return True


# Check if player has not already tried to strike the cell
def check_strike_input(strike_input_tuple):
    if strike_input_tuple in attacker.hits_list:
        print("You already hit this spot, please try again!")
        return False
    else:
        return strike_input_tuple

# Coordinates functions

# Convert user input of 'A1' to (0,0) or 'A1 r' to (0, 0, r)
def convert_coords(coords_input):
    # Strike: return tuple (0, 0)
    if re.fullmatch(regex_pattern_strike, coords_input):
        coords_output = (dict_coords_row[coords_input[0].upper()],int(coords_input[1:])-1)
    # Position: return tuple (0, 0, direction)
    elif re.fullmatch(regex_pattern_position, coords_input):
        coords_output = (dict_coords_row[coords_input[0].upper()],int(coords_input[1:coords_input.index(" ")])-1,coords_input[coords_input.index(" ")+1:].lower())
    return coords_output

# Game functions

def start_game():
    select_first_attacker()
    strike()

def select_first_attacker():
    global attacker, defender
    attacker = random.choice([p1, p2])
    if attacker == p1:
        defender = p2
    else:
        defender = p1
    print_separator()
    print(f"The first attacker is {attacker.name}!")

# Take and check input (cell to strike) from player
# Convert it into tuple of coordinates
# Check if cell not already struck
# If all OK: call function to inflict damages

def strike():
    print_separator()
    display_board(attacker, attacker.upper_board)
    if not debug_mode:
        while True:
            attacker_input = check_input("\nPlease enter your strike with the format 'A1': ", regex_pattern_strike)
            if attacker_input:
                break
    else: # DEBUG
        global debug_pattern_strikes
        attacker_input = debug_pattern_strikes[0]
        debug_pattern_strikes.remove(debug_pattern_strikes[0])
    strike_input_tuple = convert_coords(attacker_input)
    coord_attacker_input = check_strike_input(strike_input_tuple)
    attacker.hits_list.append(coord_attacker_input)
    inflict_damages(coord_attacker_input)
    if flag_game_active:
        switch()

# Inflict damages
def inflict_damages(coord_attacker_input):
    # Attacker hits a defender's ship
    if coord_attacker_input in defender.lower_board.filled_coords:
        for ship in defender.ships:
            if coord_attacker_input in ship.coords:
                # Reduce ship's lifepoints by 1
                ship.life -= 1
                # Ship sunk if no lifepoint remains
                if ship.life == 0:
                    attacker.upper_board.update_grid(ship, coord_attacker_input, True)
                    defender.ships.remove(ship)
                    if defender.ships == []:
                        endgame()
                    else:
                        print(f"\n{ship.model} sunk!\n{defender.name} still has {', '.join([ship.model for ship in defender.ships])}\n")
                        display_board(attacker, attacker.upper_board)
                # Ship not sunk
                else:
                    attacker.upper_board.update_grid(False, coord_attacker_input, True)
                    print(f"\n{ship.model} hit! Still {ship.life}/{ship.size} to go to sink it!\n")
                    display_board(attacker, attacker.upper_board)
    # Attacker hits the sea
    else:
        attacker.upper_board.update_grid(False, coord_attacker_input, False)
        print("\nMissed!\n")
        display_board(attacker, attacker.upper_board)
    input("\nPress Enter to continue...")

# Attacker becomes defender, defender becomes attacker
def switch():
    global attacker, defender
    attacker, defender = defender, attacker
    print_separator()
    print(f"Now {attacker.name} attacks!")
    strike()

# The winner is found!
def endgame():
    global flag_game_active
    print_separator()
    display_board(attacker, attacker.upper_board)
    print(f"\nYou sunk the last ship of {defender.name}! {attacker.name} wins!")
    flag_game_active = False


# GLOBAL VARIABLES declaration

base_board = Board("base", "base board")
flag_game_active = True
list_coords_row = [i for i in "▣" + string.ascii_uppercase[0:10]] # List ['▣', 'A', ..., 'J']
dict_coords_row = dict(zip(string.ascii_uppercase, range(0,10))) # Dictionary {"A":1, ..., "J":9}
# User-friendly format 'A1 - J10' for strike input
regex_pattern_strike = "[a-jA-J][0-9]|[a-jA-J]10"
# User-friendly format 'A1 direction - J10 direction' for position input
regex_pattern_position = "[a-jA-J][0-9] [a-zA-Z]+|[a-jA-J]10 .+"


# DEBUG mode (full game played by computer)

debug_mode = False
if len(sys.argv) >=2:
    if sys.argv[1] == "-debug":
        debug_mode = True

debug_pattern_position_ships = ["A1 r", "B2 r", "C3 r", "D4 r", "E5 d"] # Same for both players
debug_pattern_strikes_winner = ["A1", "A2", "A3", "A4", "A5", "B2", "B3", "B4", "B5", "C3",  "C4", "C5", "D4", "D5", "D6", "E5", "F5", "G5"]
debug_pattern_strikes_loser = ["A1", "B2", "C3", "D4", "E5", "F6", "G7", "H8", "I9", "J10",  "A2", "B3", "C4", "D5", "E6", "F7", "G8", "H9"]
debug_pattern_strikes = [None] * (len(debug_pattern_strikes_winner) + len(debug_pattern_strikes_loser))
debug_pattern_strikes[::2] = debug_pattern_strikes_winner
debug_pattern_strikes[1::2] = debug_pattern_strikes_loser


# GAME

print_separator()
print("---------------")
print("BATTLESHIP GAME")
print("---------------")

print_rules()
print_separator()

if not debug_mode:
    p1 = Player(input("Player 1: please enter your name: "))
    print_separator()
    p2 = Player(input("Player 2: please enter your name: "))
else: # DEBUG
    p1 = Player("Ting")
    p2 = Player("Eric")

start_game()
