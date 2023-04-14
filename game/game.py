import cell
import random
import player
import os


# Class for Game state
class Game:
    def __init__(self):
        self.board = []
        self.sensors = {
            'breeze': False,
            'stench': False,
            'glitter': False,
            'bump': False,
            'scream': False
        }
        self.player = player.Player(0, 0)
        self.game_over = False
        self.won = False

    # Create the 4x4 game board
    def create_board(self):
        board = []
        for i in range(4):
            row = []
            for j in range(4):
                row.append(cell.Cell(i, j))
            board.append(row)
        return board

    # Set the wumpus location
    def set_wumpus(self):
        # Wumpus can be placed in any cell except the starting cell
        x = random.randint(0, 3)
        y = random.randint(0, 3)

        # If the wumpus is placed in the starting cell, move it to a random cell
        while x == 0 and y == 0:
            x = random.randint(0, 3)
            y = random.randint(0, 3)

        self.board[x][y].set_wumpus()

        # Set the stench sensor to true for all adjacent cells
        if x > 0:
            self.board[x - 1][y].set_stench()
        if x < 3:
            self.board[x + 1][y].set_stench()
        if y > 0:
            self.board[x][y - 1].set_stench()
        if y < 3:
            self.board[x][y + 1].set_stench()

    # Set the pit locations
    def set_pits(self):
        # Two pits
        for i in range(2):
            x = random.randint(0, 3)
            y = random.randint(0, 3)

            # If the pit is placed in the starting cell or the same cell as another pit, move it to a random cell
            while (x == 0 and y == 0) or self.board[x][y].get_pit():
                x = random.randint(0, 3)
                y = random.randint(0, 3)

            self.board[x][y].set_pit()

            # Set the breeze sensor to true for all adjacent cells
            if x > 0:
                self.board[x - 1][y].set_breeze()
            if x < 3:
                self.board[x + 1][y].set_breeze()
            if y > 0:
                self.board[x][y - 1].set_breeze()
            if y < 3:
                self.board[x][y + 1].set_breeze()

    # Set the gold location
    def set_gold(self):
        # Gold can be placed in any cell except the starting cell or pits
        x = random.randint(0, 3)
        y = random.randint(0, 3)

        # If the gold is placed in the starting cell or a pit, move it to a random cell
        while (x == 0 and y == 0) or self.board[x][y].get_pit():
            x = random.randint(0, 3)
            y = random.randint(0, 3)

        self.board[x][y].set_gold()

    # Set the initial state of the game board
    def set_initial_state(self):
        self.board = self.create_board()
        self.set_wumpus()
        self.set_pits()
        self.set_gold()

    # Print the game board like a matrix using +, -, and |
    def print_board(self):

        # Where is the player?
        player_x = self.player.get_x()
        player_y = self.player.get_y()

        # Print the top border
        print('+' + '---+' * 4)

        # Print the board
        for i in range(4):
            for j in range(4):
                if i == player_x and j == player_y:
                    print('| P ', end='')
                else:
                    print('|   ', end='')
            print('|')
            print('+' + '---+' * 4)

    # Update game state
    def update_game_state(self, action):

        # Get the player's current location
        player_x = self.player.get_x()
        player_y = self.player.get_y()

        # Get the current cell
        current_cell = self.board[player_x][player_y]

        # If the player chooses to move forward
        if action == 'F':
            # If the player is facing north
            if self.player.get_direction() == 'N':
                # If the player is not at the top of the board
                if player_x > 0:
                    # Move the player forward
                    self.player.set_x(player_x - 1)
                else:
                    # The player bumped into the wall
                    self.sensors['bump'] = True

            # If the player is facing south
            elif self.player.get_direction() == 'S':
                # If the player is not at the bottom of the board
                if player_x < 3:
                    # Move the player forward
                    self.player.set_x(player_x + 1)
                else:
                    # The player bumped into the wall
                    self.sensors['bump'] = True

            # If the player is facing east
            elif self.player.get_direction() == 'E':
                # If the player is not at the right side of the board
                if player_y < 3:
                    # Move the player forward
                    self.player.set_y(player_y + 1)
                else:
                    # The player bumped into the wall
                    self.sensors['bump'] = True

            # If the player is facing west
            elif self.player.get_direction() == 'W':
                # If the player is not at the left side of the board
                if player_y > 0:
                    # Move the player forward
                    self.player.set_y(player_y - 1)
                else:
                    # The player bumped into the wall
                    self.sensors['bump'] = True

        # If the player chooses to turn left
        elif action == 'L':
            # Turn the player left
            self.player.turn_left()

        # If the player chooses to turn right
        elif action == 'R':
            # Turn the player right
            self.player.turn_right()

        # If the player chooses to shoot
        elif action == 'S':
            # Get the player's current direction
            direction = self.player.get_direction()

            # If the player is facing north
            if direction == 'N':
                # If there is a wumpus in the cell above the player
                if player_x > 0 and self.board[player_x - 1][player_y].get_wumpus():
                    # The player killed the wumpus
                    self.sensors['scream'] = True
                    self.board[player_x - 1][player_y].set_wumpus(False)
                else:
                    # The player missed
                    self.sensors['scream'] = False

            # If the player is facing south
            elif direction == 'S':
                # If there is a wumpus in the cell below the player
                if player_x < 3 and self.board[player_x + 1][player_y].get_wumpus():
                    # The player killed the wumpus
                    self.sensors['scream'] = True
                    self.board[player_x + 1][player_y].set_wumpus(False)
                else:
                    # The player missed
                    self.sensors['scream'] = False

            # If the player is facing east
            elif direction == 'E':
                # If there is a wumpus in the cell to the right of the player
                if player_y < 3 and self.board[player_x][player_y + 1].get_wumpus():
                    # The player killed the wumpus
                    self.sensors['scream'] = True
                    self.board[player_x][player_y + 1].set_wumpus(False)
                else:
                    # The player missed
                    self.sensors['scream'] = False

            # If the player is facing west
            elif direction == 'W':
                # If there is a wumpus in the cell to the left of the player
                if player_y > 0 and self.board[player_x][player_y - 1].get_wumpus():
                    # The player killed the wumpus
                    self.sensors['scream'] = True
                    self.board[player_x][player_y - 1].set_wumpus(False)
                else:
                    # The player missed
                    self.sensors['scream'] = False

        # If the player chooses to grab the gold
        elif action == 'G':
            # If the player is on a cell with gold
            if current_cell.get_gold():
                # The player grabbed the gold
                self.sensors['glitter'] = True
                current_cell.set_gold(False)
            else:
                # The player did not grab the gold
                self.sensors['glitter'] = False

        # If the player chooses to climb out of the cave
        elif action == 'C':
            # If the player is on the starting cell
            if player_x == 0 and player_y == 0:
                # The player climbed out of the cave
                self.sensors['climb'] = True
            else:
                # The player did not climb out of the cave
                self.sensors['climb'] = False

        # If the player chooses to do nothing
        elif action == 'N':
            # Do nothing
            pass

        # Update the player's current cell
        current_cell = self.board[player_x][player_y]

    def print_score(self):
        """Print the player's score."""
        print('Score: ' + str(self.player.get_score()))

    def print_sensors(self):
        """Print the player's sensors."""
        print('Sensors: ' + str(self.sensors))

    def start_game(self):
        """Start the game and play until the player wins or dies."""

        self.set_initial_state()

        # Print the game board
        self.print_board()


if __name__ == '__main__':
    # Create a new game to test the game class
    game = Game()
    game.set_initial_state()

    # Print the game board
    game.print_board()

    # Print the state of board cells in a matrix with W for wumpus, P for pit, G for gold, S for stench, B for breeze
    for i in range(4):
        for j in range(4):
            cell_State = game.board[i][j].get_cell_properties()
            flag = 0
            count = 0
            if cell_State['has_wumpus']:
                print('W ', end='')
                flag = 1
                count = count+1
            if cell_State['has_pit']:
                print('P ', end='')
                flag = 1
                count = count+1
            if cell_State['has_gold']:
                print('G ', end='')
                flag = 1
                count = count+1
            if cell_State['has_stench']:
                print('S ', end='')
                flag = 1
                count = count+1
            if cell_State['has_breeze']:
                print('B ', end='')
                flag = 1
                count = count+1
            if(flag == 0):
                print('E ', end='')
                count = count+1
            if(count == 1):
                print('  ', end=" ")
            if(count == 2):
                print('')
            print(',', end='')
        print()

    # Print the state of the sensors