import tkinter as tk
from tkinter import ttk
from PIL import ImageTk
import PIL



# Frame subclass with n labels in them to display numbers with images for each digit (n = length in constructor)
class Number_frame(tk.Frame):
    
    def __init__(self, parent, app, length):
        super().__init__(parent)

        self.app = app
        
        self.load_images()    
        
        self.configure(background='Black')
        
        self.labels = []
        
        
        self.length = length

        # Configures columns and adds a new label on each with number 0
        for i in range(self.length):
            self.columnconfigure(i, weight=1)
            self.labels.append( ttk.Label(self, image=self.numeric_digit_images[0], background='Black'))
            self.labels[i].grid(row=0, column=i, sticky='nsew')


    # Sets a numeric value on the frame, asigning one digit to each label, only if the value size is equal or smaller than the current size
    # Returns 0 when value was assigned correctly, -1 otherwise
    def set_value(self, value):
        string = str(value)
        length = len(string)
        if length <= self.length:
            offset = self.length - length
            for i in range (offset):
                string = '0' + string
            for i in range(self.length):
                int_value = int(string[i])
                if int_value in range (10):
                    self.labels[i].configure(image=self.numeric_digit_images[int_value])
                    self.labels[i].image = self.numeric_digit_images[int_value]
            return 0        
                
        else:
            return -1
    
    def load_images(self):
        #ratio = 62/88
        ##width = height * 62 // 88
        # array of 10 images with 0 to 9 digits
        self.numeric_digit_images = []
        for i in range(10):
            self.numeric_digit_images.append(ImageTk.PhotoImage(PIL.Image.open('img/scoreboard_' + str(i) + '.png', 'r').resize((20, 28)))) #.resize((width, height))))