import tkinter as tk
from pathlib import Path

# Add this import for the new ControlPage:
from build.control import ControlPage

from build.parameters import ParametersPage
from build.intro import IntroPage
from build.correct import CorrectPage
from build.wrongs import WrongsPage
from build.randomizer import RandomizerPage
import argparse
import backend.logic as logic
import json

class BaseApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.shared_data = {
            "question_text": None,
            "latex_question": None,
            "has_visited_parameters": False,
            "has_visited_controller": False, 
            "parameters": [], 
            "correct_answer": None, 
            "wrong_answers": [], 
            "answer_number": None,
            "randomization_count": 0,
            "precision": 0
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

        # Insert ControlPage between IntroPage and ParametersPage
        for F in (IntroPage, ControlPage, ParametersPage, CorrectPage, WrongsPage, RandomizerPage):
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
    
    def save_has_visited_parameters(self, bool):
        self.shared_data["has_visited_parameters"] = bool

    def save_parameters(self, parameters):
        self.shared_data["parameters"] = parameters

    def save_question_text(self, question_text):
        self.shared_data["question_text"] = question_text

    def save_precision(self, precision):
        self.shared_data["precision"] = precision

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Random Question Generator")
    parser.add_argument("--json-path", type=str, help="Path to the JSON file containing the question data.")
    args = parser.parse_args()

    if args.json_path:
        json_path = Path(args.json_path)
        print("Multi-input mode enabled.")
        with open(json_path, "r") as f:
            data_list = json.load(f)
        if not isinstance(data_list, list):
            print("The JSON file is not a list.")
            exit(1)
        # Create a Logic instance and process all questions in the JSON list.
        logic_instance = logic.Logic()
        all_questions = logic_instance.perform_logic_all(data_list)
        print(all_questions)
        exit(0)

    app = BaseApp()
    app.resizable(False, False)
    app.mainloop()
