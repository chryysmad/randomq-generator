import tkinter as tk
from pathlib import Path
from build.parameters import ParametersPage
from build.intro import IntroPage
from build.correct import CorrectPage
from build.wrongs import WrongsPage
from build.randomizer import RandomizerPage

class BaseApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.shared_data = {
            "latex_question": None,
            "parameters": [], 
            "correct_answer": None, 
            "wrong_answers": [], 
            "answer_number": None,
            "randomization_count": 0
        }

        self.title("Random Question Generator")
        self.resizable(True, True)
        self.geometry("1280x900")
        self.configure(bg="#F5F5F5")

        # make a container that stores all the pages
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (IntroPage, ParametersPage, CorrectPage, WrongsPage, RandomizerPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("IntroPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

    def save_latex_question(self, sympy_expr):
        self.shared_data["latex_question"] = sympy_expr

    def save_parameters(self, parameters):
        self.shared_data["parameters"] = parameters

if __name__ == "__main__":
    app = BaseApp()
    app.resizable(False, False)
    app.mainloop()
