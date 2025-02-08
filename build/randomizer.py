from pathlib import Path
import tkinter as tk 
from tkinter import Tk, Canvas, Entry, Button, PhotoImage
from build.intro import IntroPage
from backend.logic import Logic

class RandomizerPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#F5F5F5")

        self.logic = Logic(self.controller)

        self.randomization_count = 0 

        OUTPUT_PATH = Path(__file__).parent
        ASSETS_PATH = OUTPUT_PATH / Path(r"./assets/frame0")

        def relative_to_assets(path: str) -> Path:
            return ASSETS_PATH / Path(path)

        self.canvas = tk.Canvas(
            self,
            bg="#F5F5F5",
            height=547,
            width=994,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        self.canvas.place(x=0, y=0)

        self.canvas.create_text(
            24.0, 129.0,
            anchor="nw",
            text="Randomizer",
            fill="#1E1E1E",
            font=("Inter", 20 * -1)
        )

        self.canvas.create_text(
            24.0, 167.0,
            anchor="nw",
            text="Choose how many times you want to randomize the specific question.",
            fill="#757575",
            font=("Inter", 16 * -1)
        )

        self.canvas.create_text(
            330.0, 245.0,
            anchor="nw",
            text="Number of times:",
            fill="#1E1E1E",
            font=("Inter", 16 * -1)
        )

        self.entry_image_1 = tk.PhotoImage(file=relative_to_assets("entry_1.png"))
        self.canvas.create_image(
            573.0, 255.5,
            image=self.entry_image_1
        )
        self.entry_1 = tk.Entry(self, bd=0, bg="#FFFFFF", fg="#000716", highlightthickness=0)
        self.entry_1.place(x=491.0, y=237.0, width=164.0, height=35.0)

        placeholders = {
            self.entry_1: "Enter a value..."
        }

        def on_focus_in(event):
            entry = event.widget
            placeholder = placeholders.get(entry)
            if placeholder and entry.get() == placeholder:
                entry.delete(0, "end")
                entry.config(fg="#000716")

        def on_focus_out(event):
            entry = event.widget
            placeholder = placeholders.get(entry)
            if placeholder and entry.get() == "":
                entry.insert(0, placeholder)
                entry.config(fg="#C0C0C0")

        for entry in placeholders.keys():
            entry.insert(0, placeholders[entry])
            entry.config(fg="#C0C0C0")
            entry.bind("<FocusIn>", on_focus_in)
            entry.bind("<FocusOut>", on_focus_out)

        self.button_image_1 = tk.PhotoImage(file=relative_to_assets("button_1.png"))
        self.button_1 = tk.Button(
            self,
            image=self.button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=self.process_randomization_count,
            relief="flat"
        )
        self.button_1.place(x=402.0, y=299.0, width=190.0, height=34.0)

        self.canvas.pack()

    def save_randomization_count(self):
        self.controller.shared_data["randomization_count"] = self.randomization_count

    def process_randomization_count(self):
        try:
            self.randomization_count = int(self.entry_1.get().strip())
        except ValueError:
            self.randomization_count = 0

        self.save_randomization_count()

        self.logic.perform_logic()
        self.controller.show_frame("IntroPage") 
