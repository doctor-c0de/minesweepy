import tkinter as tk
from tkinter import ttk


# local import
from cell import Cell

class Board(tk.Frame):
    

    def __init__(self, master, app):
        super().__init__(master)

        self.app = app

    # creates all cell widgets, puts them on board_panel grid, and stores them in cell_array
    # called when app starts and when difficulty changed
    def create_cell_widgets(self):
        #reset cell array
        self.cell_array = []

        # for each grid space, create cell and add it
        # rows
        for r in range(self.app.n_rows):

            # configure row weight and minsize inside board_panel
            self.rowconfigure(r, weight=1, minsize=self.app.cell_size) 

            # columns
            for c in range(self.app.n_cols):

                # configure column weight and minsize inside board_panel
                self.columnconfigure(c, weight=1, minsize=self.app.cell_size)
                
                # create cell, add to grid
                cell = Cell(self, self.app, r, c)
                cell.grid(row = r, column= c, sticky='nsew')
                # add new cell to array
                self.cell_array.append(cell)

    def reset_cell_widgets(self):
        # sets all cells to closed (button mode with no text)
        for cell in self.cell_array:
                cell.set_closed()

    def set_board(self, new_board):
         
        if new_board:
              self.create_cell_widgets()
        else:
             self.reset_cell_widgets()

    # Sets a cell widget to "open" with a value (0-8)
    def open_cell_widget(self, row, column, value):
        self.cell_array[self.cell_position(row, column)].set_open(value)

    # Method to simplify getting the position of a cell object in cell_array which is internally one-dimensional
    def cell_position(self, row, column):
        return row * self.app.n_cols + column    
    