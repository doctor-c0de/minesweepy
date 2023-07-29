import tkinter as tk
from tkinter import ttk 
from PIL import Image, ImageTk, ImageDraw, ImageFont
import PIL

class Cell(tk.Label):
    

    def __init__(self, parent, app, row, column):
        super().__init__(parent)
        self.root = parent
        
        self.app = app
        
        self.grid(row=row, column= column, sticky='nsew')

        self.row = row
        self.column = column

        self.cell_images = []
        self.load_images()
        

        self.closed_color = 'Dark grey'
        self.open_color = 'Light grey'

        self.bind('<Button-1>', lambda event, r=self.row, c=self.column: self.app.cell_clicked(r,c))
        self.bind('<Button-2>', lambda event, r=self.row, c=self.column: self.app.cell_right_clicked(r,c))
        self.bind('<Button-3>', lambda event, r=self.row, c=self.column: self.app.cell_right_clicked(r,c))
        
        self.configure(text='', anchor=tk.CENTER, image='', compound='none', background=self.closed_color, relief='raised', borderwidth=2) 
        
        self.state = 'closed'


    # Set status methods
    def set_open(self, cell_value):
        self.configure(text=None, image=self.cell_images[cell_value], background=self.open_color, relief='sunken')
        self.state = 'open'
    
    def set_closed(self):
        self.configure(text='', image='', background=self.closed_color, relief='raised')
        self.state = 'closed'

    def set_flagged(self):
        self.configure(text='', image=self.cell_images[11], background=self.closed_color, relief='raised')
        self.state = 'flagged'

    # The following are end_game states (show correct/wrong flags and clicked/remaining mines)
    # so no state needed (it will be reset on next game anyway)    
    def set_green_flag(self):
        self.configure(text='', image=self.cell_images[12], background=self.closed_color, relief='raised')

    def set_red_flag(self):
        self.configure(text='', image=self.cell_images[13], background=self.closed_color, relief='raised')
    
    def set_orange_mine(self):
        self.configure(text='', image=self.cell_images[10], background=self.closed_color, relief='raised')
        
    def set_red_mine(self):
        self.configure(text='', image=self.cell_images[9], background=self.open_color, relief='sunken')

    # Load image files for cell states in a list
    def load_images(self):
        # image size 60% of cell size to fit on label without making it bigger
        img_size = int(self.app.cell_size * 0.6)
        # array with images for cell label (open cell) 
        for i in range(14):
            self.cell_images.append(ImageTk.PhotoImage(PIL.Image.open('img\cell_' + str(i) + '.png').resize((img_size, img_size))))
        # Images:
        # 0-8 just numbers for adjacent mines
        # 9 clicked mine (red)
        # 10 remaining mine (orange)
        # 11 normal flag 
        # 12 correct flag (green)
        # 13 wrong flag (crossed out)