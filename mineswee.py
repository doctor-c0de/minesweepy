import tkinter as tk
from tkinter import ttk

import numpy as np
import random

from scipy import signal

# local imports
from board import Board
from cell import Cell
from number_frame import Number_frame



def main():
    app = App()
    app.mainloop()

class App(tk.Tk):
  
    # widget size attributes
    cell_size = 30
    top_panel_height = 45


    # App CONSTRUCTOR
    def __init__(self):
        super().__init__()
        
        # TODO implement dificulty chooser
        # difficulty settings
        self.n_rows = 9
        self.n_cols = 9
        self.n_mines = 10

        

        self.title('mineswee.py')
        
        
        # App window size and position
        app_w = self.cell_size * self.n_cols
        app_h = app_w + self.top_panel_height # 330
        app_x = self.winfo_screenwidth() // 2 - app_w // 2
        app_y = self.winfo_screenheight() // 2 - app_h // 2

        self.geometry(f'{app_w}x{app_h}+{app_x}+{app_y}')
        self.resizable(False, False)
        
        # one grid slot on window for main_frame
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # Difficulty variable to change stats #TODO 0 = Easy, 1 = Intermediate, 2 = Expert, 3 = Custom
        self.difficulty = 0
        #TODO: way to check if dificulty changed, for now, a var
        self.difficulty_changed = False
        
        # Frame that occupies all the window and holds 2 childs: top_panel and board_panel
        main_frame = ttk.Frame(self)
        main_frame.grid(row=0, column=0, sticky='nsew')

        # Top bar frame that holds the flags left counter, the new game button, and the timer
        top_panel = tk.Frame(main_frame, height=str(self.top_panel_height), background='Black')
        top_panel.pack(side='top', expand=False, fill='x')

        # Frame subclass that holds the widget cells, the game board itself.
        self.board = Board(main_frame, self)
        self.board.pack(side='bottom', expand=True, fill='both')
        
        # 3 colums for 3 childs
        top_panel.columnconfigure(0, weight = 1)
        top_panel.columnconfigure(1, weight = 1)
        top_panel.columnconfigure(2, weight = 1)

        # Top bar child 1: Frame subclass to display digits (flags/mines left counter)
        self.n_mines_left_frame = Number_frame(top_panel, self, 3)
        self.n_mines_left_frame.configure(padx=0)
        self.n_mines_left_frame.grid(row=0, column=0, sticky='nw')
        self.n_mines_left_frame.set_value(10)

        # Top bar child 2: New game button
        self.new_game_btn = tk.Button(top_panel, text='New Game', justify='center', background='Black', foreground='White')
        self.new_game_btn.grid(row=0, column=1, sticky='nsew', padx=0)
        self.new_game_btn.bind('<Button-1>', self.new_game)

        # Top bar child 3: Frame subclass to display digits (time elapsed counter)
        self.time_elapsed_frame = Number_frame(top_panel, self, 3)
        self.time_elapsed_frame.configure(padx=0)
        self.time_elapsed_frame.grid(row=0, column=2, sticky='ne')
        self.time_elapsed_frame.set_value(0)

        #self.engine = Engine(self.n_rows, self.n_cols, self.n_mines)

        # prepares variables and widgets for a new game
        self.new_game('first_run')
        
    
    
    
######## METHODS                
                        
    # NEW GAME method - prepares/resets mostly everything
    def new_game(self, event=None):

        # Prepares/resets game logic (engine)
        self.set_game()

        # Prepares/resets game board (GUI)
        # If called from constructor (first_run) or board size changes: create new cells
        # If new game button pressed: only reset the cells
        self.board.set_board(event == 'first_run' or self.difficulty_changed)

        # Set/reset flag counter 
        self.n_mines_left_frame.set_value(self.n_mines)

        # Set/reset timer counter  
        self.time_elapsed_frame.set_value('000')
    
    
    # Prepares game logic matrices and variables
    def set_game(self):

    ##### GAME LOGIC
        
        # MATRICES:

        # value_matrix: 2D array containing count of mines around them, 9 for mines
        self.value_matrix = np.zeros((self.n_rows, self.n_cols), dtype='u1')
        # boolean 2D array telling which cell has a mine
        self.is_mine = np.full(self.value_matrix.shape, False, dtype=bool)
        # boolean 2D array telling which cell is open already
        self.is_open = np.full(self.value_matrix.shape, False, dtype=bool)
        # boolean 2D array telling which cell has a flag
        self.is_flagged = np.full(self.value_matrix.shape, False, dtype=bool)


        # LIST
        
        # list of cell coordinates (tuple) to be opened (kind of a queue)
        self.cells_to_be_opened = []

        # BOOLEAN:

        # boolean to know if game has not started yet (mines not generated and clock not ticking)
        self.first_move = True

        # boolean to stop game when there's victory or defeat
        self.game_over = False

        # INTEGER:

        # counts flags on the board        
        self.flag_count = 0

        # Counts cells already open to simplify one of the two types of victory 
        self.open_count = 0
        
        # Time counter to update timer ( +1 / second )
        self.time_elapsed = 0

    ### END OF set_game()

    def generate_mines(self, fist_move):
        mine_list = []
        # place n_mines mines
        while len(mine_list) < self.n_mines:
            # Generates 2 pseudo-random integers for the position of the new mine to be placed
            mine_to_be_placed = (random.randint(0, self.n_rows-1), random.randint(0, self.n_cols-1))
        
            # Checks that the generated coordinate is NOT the first cell clicked AND NOT an already placed mine
            if mine_to_be_placed != fist_move and mine_to_be_placed not in mine_list:
                mine_list.append(mine_to_be_placed)
                self.is_mine[mine_to_be_placed[0],mine_to_be_placed[1]] = True
    

    # Fills the value_matrix with the count of surrounding mines
    def populate_matrix(self):
        for row in range(self.n_rows):
            for column in range(self.n_cols):
                if self.is_mine[row, column] == True:
                    self.value_matrix[row, column] = 9
                else:
                    self.value_matrix[row, column] = int(self.count_around(row, column))


    # Returns count of mines surrounding (row, column)
    def count_around(self, row, column):
        start_row = max((row-1),0)
        end_row = min((row + 2),(self.n_rows))
        start_column = max((column-1), 0)
        end_column = min((column + 2), (self.n_cols))
        neighbors = self.is_mine[start_row:end_row, start_column:end_column]
        return neighbors.sum()

    
    # Method to open cell at given coordinates. 
    # Called when clicking on a cell AND recursively by itself when an empty (value 0) cell is being open
    def open_coordinates(self, row, column):

        # Game needs to be running to open cells
        if not self.game_over:

            # Cell must be closed and not flagged
            if not self.is_open[row, column] and not self.is_flagged[row, column]:
                
                # Sets the cell open in the boolean matrix
                self.is_open[row, column] = True
                self.open_count += 1
                
                # If the cell is a mine, game ends in defeat. 
                if self.is_mine[row, column]:
                    # Coordinates are provided to mark clicked mine differently than the rest
                    self.end_game(row, column)
                    return

                # Else, if the cell is empty (value = 0) surrounding cells are queued to be open
                elif self.value_matrix[row, column] == 0:
                    
                    # Opens current cell widget
                    self.board.open_cell_widget(row, column, 0)

                    # Puts surrounding cells into queue (if they meet conditions)
                    self.add_neighbours_to_queue(row, column)
                    
                    # open cells in queue_list while queue_list has items
                    while len(self.cells_to_be_opened) > 0:
                        
                        # Extract last element of the queue 
                        next_cell = self.cells_to_be_opened.pop()
                        
                        # vars for code clarity, not really needed
                        next_cell_row = next_cell[0]
                        next_cell_column = next_cell[1]
                        next_cell_value = self.value_matrix[next_cell_row, next_cell_column]

                        # Count it open
                        self.is_open[next_cell_row, next_cell_column] = True
                        self.open_count += 1

                        # Open cell widget
                        self.board.open_cell_widget(next_cell_row, next_cell_column, next_cell_value)

                        # If current cell is also empty, add surrounding cells also to the queue
                        if next_cell_value == 0:
                            self.add_neighbours_to_queue(next_cell_row,  next_cell_column)

                # If cell is not a mine nor it is empty, just open the cell widget
                else:
                    self.board.open_cell_widget(row, column, self.value_matrix[row, column])

                # Finally, check if all non-mine cells have been open
                self.check_victory_by_tiles_open() #TODO
    
    # Checks all coordinates surrounding (row, column) 
    # and adds them to opening queue if requisites are met
    def add_neighbours_to_queue(self, row, column):
        # all the posible values to add to a simple index to find neibouring cells
        possible_neighbors = np.array = [ - self.n_cols -1 , -1, - self.n_cols + 1, -1, +1, self.n_cols - 1, self.n_cols, self.n_cols + 1 ]

        # find the simple (one-dimensional) index of given (row, column)
        simple_idx = np.ravel_multi_index((row, column), (self.n_rows, self.n_cols))
        
        # get all the simple indexes of possible neighbours
        possible_neighbors += simple_idx

        # filter negative and over the size indexes
        neighbors = list(filter(lambda x : x >= 0 and x < (self.n_rows * self.n_cols), possible_neighbors.tolist()))

        # transform the simple (one-dimensional) indexes to 2-dimensional tuples
        cells_to_add = np.unravel_index(neighbors, shape=(self.n_rows, self.n_cols))
        cells_to_add = np.transpose(cells_to_add)
       
        
        # add real neighbours to queue if not already in or open or flagged
        for cell in cells_to_add:
            tuple_cell = (cell[0], cell[1])
            print('TUPLE CELL:', tuple_cell)
            print('cells to be opened:', self.cells_to_be_opened)
            if not self.is_open[cell[0], cell[1]] and not self.is_flagged[cell[0], cell[1]]:
                if tuple_cell not in self.cells_to_be_opened:
                    self.cells_to_be_opened.insert(0, tuple_cell)
                    #self.cells_to_be_opened.append(tuple_cell)

    # method called from cell object being clicked with left mouse button
    def cell_clicked(self, row, column):

        # if it's the first cell clicked this game generates the board (mines and numbers)
        # this is done to prevent clicking on a mine on the first click, which is frustrating and silly
        if self.first_move:
            
            self.generate_mines((row, column))
            self.populate_matrix()
            self.first_move = False
            
            # starts timer
            self.after(1000, self.update_timer)
        
        # call to the main method for opening cells at (row, column) coordinate. (will trigger recursion if cell is empty (value=0) ) 
        self.open_coordinates(row, column)



    # method called from cell object being clicked with right mouse button (actually mouse button-2 and mouse button-3, since it changes depending on system)
    def cell_right_clicked(self, row, column):
        
        # Can only place flags if game is running (after first cell is open, timer running, no game over)
        if not self.game_over and not self.first_move:
            
            # if cell not flagged and flags placed < total number of mines
            # place flag
            if not self.is_flagged[row, column] and self.flag_count < self.n_mines:
                self.is_flagged[row, column] = True
                self.flag_count +=1
                self.board.cell_array[self.board.cell_position(row, column)].set_flagged()
                self.check_victory_by_flags()

            # else, if cell is flagged, remove flag
            elif self.is_flagged[row, column]:            
                # set cell in buton mode
                self.is_flagged[row, column] = False
                self.board.cell_array[self.board.cell_position(row, column)].set_closed()
                self.flag_count -= 1
            
            # update flag counter
            self.n_mines_left_frame.set_value(str(self.n_mines - self.flag_count))


    # If all mines are correctly flagged, game ends in victory
    # TODO
    def check_victory_by_flags(self):
        # precheck to avoid matrix comparison unnecesarily 
        if self.flag_count == self.n_mines:
            # if flags placed == amount of mines, compare positions.
            if np.array_equal(self.is_mine, self.is_flagged):
                # if all flags are mines -> VICTORY
                self.victory("Victory by flagging all mines!!")
                #TODO Rewrite message

    # If all non-mine cells are open, game ends in victory 
    # TODO
    def check_victory_by_tiles_open(self):
        # if all cells are open except mines -> VICTORY
        if self.open_count == self.n_rows * self.n_cols - self.n_mines:
            self.victory("Victory by opening all non-mine cells!!")
            # TODO: Rewrite message
    
    # Stops game. Triggered by clicking a mine or running out of time (999 seconds limit)
    # if no (row, col) provided, it's being called from the timer reaching limit.
    # TODO 
    def end_game(self, row=None, column=None):
        
        # Setting this boolean True prevents further clicking and timer advancing further
        self.game_over = True
        # If row and col provided, it means a mine was clicked
        clicked_mine = row != None and column != None
        
        mine_list = np.argwhere(self.is_mine)
        
        flag_list = np.argwhere(self.is_flagged)

        # Checks all placed flags to mark correct ones in green, and put a red cross on wrong ones
        for flag in flag_list:
            flag_position = self.board.cell_position(flag[0], flag[1])
            if flag in mine_list:
                self.board.cell_array[flag_position].set_green_flag()
            else:
                self.board.cell_array[flag_position].set_red_flag()

        # Checks all mine positions and marks the non flagged ones with orange
        for mine in mine_list:
            if mine not in flag_list:
                mine_position = self.board.cell_position(mine[0], mine[1])
                self.board.cell_array[mine_position].set_orange_mine()
        
        # Finally, if the game ended by clicking on a mine, mark it red
        if clicked_mine:
            self.board.cell_array[self.board.cell_position(row, column)].set_red_mine()        

        # TODO: Show defeat dialog. Maybe animation.


    # Victory achieved. Stops game for now. 
    # TODO
    def victory(self, reason):
        self.game_over = True
        # TODO: Show victory dialog
        # TODO: Maybe implement high-scores

    # Updates the GUI timer. Called every second after first click until the game ends
    def update_timer(self):
        
        if not self.game_over and not self.first_move:

            # Every time 1 second is added 
            self.time_elapsed += 1

            # Checks if time limit is reached
            if self.time_elapsed == 999:
                self.end_game()

            # Updates timer widget 
            self.time_elapsed_frame.set_value(self.time_elapsed)

            # Recursively calls itself after 1 second
            self.after(1000, self.update_timer)



if __name__ == '__main__':
    main()