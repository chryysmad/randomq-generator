from pathlib import Path
import tkinter as tk
from tkinter import Canvas, Button, PhotoImage
import backend.util as util

class IntroPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.selected_option = None
        self.configure(bg="#F5F5F5")
        canvas = tk.Canvas(
            self,
            bg="#F5F5F5",
            height=547,
            width=994,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        canvas.place(x=0, y=0)
        canvas.create_text(
            24.0,
            140.0,
            anchor="nw",
            text="Random Question Generator",
            fill="#1E1E1E",
            font=("Inter", 48 * -1)
        )
        canvas.create_text(
            24.0,
            206.0,
            anchor="nw",
            text="Choose the H5P Question Type",
            fill="#757575",
            font=("Inter", 24 * -1)
        )
        button_image_1 = tk.PhotoImage(file=self.relative_to_assets("button_1.png"))
        button_1 = tk.Button(
            self,
            image=button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.set_option("MCQ"),
            relief="flat"
        )
        button_1.image = button_image_1 
        button_1.place(x=286.0, y=316.0, width=192.0, height=43.0)
        button_image_2 = tk.PhotoImage(file=self.relative_to_assets("button_2.png"))
        button_2 = tk.Button(
            self,
            image=button_image_2,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.set_option("FIB"),
            relief="flat"
        )
        button_2.image = button_image_2
        button_2.place(x=516.0, y=316.0, width=192.0, height=43.0)
        # If there have been previous generations, display the final H5P button.
        file_counter = self.controller.shared_data.get("file_counter", 1)
        if file_counter > 1:
            final_button = tk.Button(
                self,
                text="Generate Final H5P Question Set",
                command=self.generate_final_set,
                bg="#4CAF50",
                fg="white",
                font=("Inter", 16)
            )
            final_button.place(x=400.0, y=380.0, width=250.0, height=40.0)

    def relative_to_assets(self, path: str):
        OUTPUT_PATH = Path(__file__).parent
        ASSETS_PATH = OUTPUT_PATH / Path(r"./assets/frame4")
        return ASSETS_PATH / Path(path)

    def set_option(self, option):
        self.selected_option = option
        util.logger.info(f"Selected option: {option}")
        self.controller.show_frame("ParametersPage")

    def generate_final_set(self):
        # Access the logic instance from the controller.
        logic = self.controller.logic  
        logic.generate_final_h5p_set()
        util.logger.info("Final H5P Question Set generated.")
