from pathlib import Path
import tkinter as tk
from tkinter import Canvas, Button, PhotoImage
from PIL import Image, ImageDraw, ImageTk 
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
        button_2.place(x=516.0, y=316.0, width=200.0, height=43.0)
        
        
        self.rounded_bg = self.create_rounded_rectangle_image(
            width=210,    
            height=43,
            radius=10,
            fill="#2D2D2D" 
        )

        self.final_button = tk.Button(
            self,
            image=self.rounded_bg,             
            text="Generate Final H5P",        
            compound="center",   
            fg="white",             
            font=("Inter", 13),
            borderwidth=0,
            highlightthickness=0,
            relief="flat",
            command=self.generate_final_set, 
            bg="#2D2D2D", 
            activebackground="#2D2D2D",
            activeforeground="white" 
        )


    def create_rounded_rectangle_image(self, width, height, radius=15, fill="#2D2D2D"):
        image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((0, 0, width, height), radius=radius, fill=fill)
        return ImageTk.PhotoImage(image)

    def tkraise(self, aboveThis=None):
        super().tkraise(aboveThis)
        self.update_final_button()

    def relative_to_assets(self, path: str):
        OUTPUT_PATH = Path(__file__).parent
        ASSETS_PATH = OUTPUT_PATH / Path(r"./assets/frame4")
        return ASSETS_PATH / Path(path)

    def set_option(self, option):
        self.selected_option = option
        util.logger.info(f"Selected option: {option}")
        self.controller.show_frame("ParametersPage")

    def generate_final_set(self):
        logic = self.controller.logic  
        logic.generate_final_h5p_set()
        util.logger.info("Final H5P Question Set generated.")

    def update_final_button(self):
        if self.controller.shared_data.get("has_visited_parameters", False):
            self.final_button.place(x=400.0, y=380.0, width=192.0, height=43.0)
        else:
            self.final_button.place_forget()