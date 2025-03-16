# File: intro.py
from pathlib import Path
import tkinter as tk
from tkinter import Canvas, PhotoImage
from PIL import Image, ImageDraw, ImageTk 
import backend.util as util

class IntroPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.selected_option = None
        self.configure(bg="#F5F5F5")
        
        # Main canvas with title texts.
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
        
        # MCQ and FIB selection buttons.
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
        
        # Rounded background for the "Generate Final H5P" button.
        self.rounded_bg = self.create_rounded_rectangle_image(
            width=210,    
            height=43,
            radius=10,
            fill="#2D2D2D" 
        )

        # "Generate Final H5P" button and its associated number-of-times label/entry.
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

        self.num_times_label = tk.Label(
            self,
            text="Number of times to generate randomized h5ps",
            bg="#F5F5F5",
            fg="#1E1E1E",
            font=("Inter", 12)
        )
        
        self.num_times_var = tk.StringVar(value="Enter a number...")
        self.num_times_entry = tk.Entry(
            self,
            textvariable=self.num_times_var,
            bd=0,
            bg="#FFFFFF",
            fg="#C0C0C0",
            font=("Inter", 12)
        )

        def on_focus_in(event):
            if self.num_times_var.get() == "Enter a number...":
                self.num_times_var.set("")
                self.num_times_entry.config(fg="#000716")
        def on_focus_out(event):
            if not self.num_times_var.get().strip():
                self.num_times_var.set("Enter a number...")
                self.num_times_entry.config(fg="#C0C0C0")
        self.num_times_entry.bind("<FocusIn>", on_focus_in)
        self.num_times_entry.bind("<FocusOut>", on_focus_out)
        
        # Hide the final button and number input initially.
        self.num_times_label.place_forget()
        self.num_times_entry.place_forget()
        self.final_button.place_forget()
        
        # --- NEW: Settings button (hidden until control page has been visited).
        self.settings_button = tk.Button(
            self,
            text="Settings",
            font=("Inter", 12, "bold"),
            bg="#2D2D2D",
            fg="white",
            relief="flat",
            borderwidth=0,
            command=self.open_settings
        )
        self.settings_button.place_forget()

    def create_rounded_rectangle_image(self, width, height, radius=15, fill="#2D2D2D"):
        image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((0, 0, width, height), radius=radius, fill=fill)
        return ImageTk.PhotoImage(image)

    def tkraise(self, aboveThis=None):
        super().tkraise(aboveThis)
        self.update_final_button()
        # Show the Settings button only if the control page has been visited.
        if self.controller.shared_data.get("has_visited_controller", False):
            # Place at bottom right with a 20px margin.
            self.settings_button.place(relx=1.0, rely=1.0, anchor="se", x=-20, y=-20)
        else:
            self.settings_button.place_forget()

    def relative_to_assets(self, path: str):
        OUTPUT_PATH = Path(__file__).parent
        ASSETS_PATH = OUTPUT_PATH / Path(r"./assets/frame4")
        return ASSETS_PATH / Path(path)

    def set_option(self, option):
        self.selected_option = option
        util.logger.info(f"Selected option: {option}")
        # If control page hasn't been visited yet, show it.
        if not self.controller.shared_data.get("has_visited_controller", False):
            self.controller.show_frame("ControlPage")
        else:
            self.controller.show_frame("ParametersPage")

    def open_settings(self):
        # Enter settings mode and show the ControlPage.
        self.controller.shared_data["in_settings_mode"] = True
        self.controller.show_frame("ControlPage")

    def generate_final_set(self):
        logic = self.controller.logic
        val = self.num_times_var.get().strip()
        try:
            times = int(val)
        except ValueError:
            times = 1
        logic.generate_final_h5p_set(times)
        util.logger.info(f"Final H5P Question Set generated {times} times.")

    def update_final_button(self):
        if self.controller.shared_data.get("has_visited_parameters", False):
            self.num_times_label.place(x=400.0, y=380.0)
            self.num_times_entry.place(x=400.0, y=410.0, width=192.0, height=25)
            self.final_button.place(x=400.0, y=450.0, width=192.0, height=43.0)
        else:
            self.num_times_label.place_forget()
            self.num_times_entry.place_forget()
            self.final_button.place_forget()
