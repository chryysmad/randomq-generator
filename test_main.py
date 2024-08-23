import tkinter as tk
from tkinter import ttk
from test import TestPage

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Test CorrectPage")
        self.geometry("1000x600")  # Set window size
        self.configure(bg="#F5F5F5")
        
        # Initialize the CorrectPage
        self.correct_page = TestPage(self, self)
        self.correct_page.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = App()
    app.mainloop()