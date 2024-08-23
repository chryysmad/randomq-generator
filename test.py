import tkinter as tk
from tkinter import ttk
from pathlib import Path

class TestPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#F5F5F5")

        OUTPUT_PATH = Path(__file__).parent
        ASSETS_PATH = OUTPUT_PATH / Path(r"/home/chrysmad/randomq-generator/build/assets/frame3")

        def relative_to_assets(path: str) -> Path:
            return ASSETS_PATH / Path(path)
        
        # Top section: non-scrollable
        self.top_frame = tk.Frame(self, bg="#F5F5F5")
        self.top_frame.pack(fill="x", padx=10, pady=10)

        self.create_top_section()

        # Scrollable section: for parameters
        self.scrollable_frame = tk.Frame(self)
        self.scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(self.scrollable_frame, bg="#F5F5F5", bd=0, highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.scrollbar = ttk.Scrollbar(self.scrollable_frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.inner_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        self.inner_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.param_count = 1  # Counter for the number of parameters

        self.create_initial_widgets()

        # Bottom section: "+" button (static under the scrollable area)
        self.bottom_frame = tk.Frame(self, bg="#F5F5F5")
        self.bottom_frame.pack(fill="x", padx=10, pady=10)

        self.button_image_1 = tk.PhotoImage(file=relative_to_assets("button_1.png"))  # Replace with your image path
        button_1 = tk.Button(
            self.bottom_frame,
            image=self.button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=self.add_parameter,
            relief="flat"
        )
        button_1.pack(pady=10)

    def create_top_section(self):
        # Create the LaTeX question area or other static text content
        label_question = tk.Label(self.top_frame, text="LaTeX Question Area", bg="#F5F5F5", font=("Inter", 20))
        label_question.pack(anchor="w")

        # You can add more static elements here if needed

    def create_initial_widgets(self):
        # Create the initial set of labels and entries in the scrollable section
        self.add_parameter()

    def add_parameter(self):
        y_offset = 40  # Vertical spacing between parameter sets

        # Calculate the current y position based on the number of parameters
        current_y = 100 + (self.param_count - 1) * y_offset

        # Add the "Param X:" label
        label = tk.Label(self.inner_frame, text=f"Param {self.param_count}:", bg="#F5F5F5", font=("Inter", 14))
        label.grid(row=self.param_count, column=0, padx=10, pady=5, sticky="w")

        # Add the entry fields
        entry_name = tk.Entry(self.inner_frame, width=10)
        entry_range_from = tk.Entry(self.inner_frame, width=10)
        entry_range_to = tk.Entry(self.inner_frame, width=10)
        entry_value = tk.Entry(self.inner_frame, width=10)
        entry_step = tk.Entry(self.inner_frame, width=10)

        # Place the entry fields in the grid
        entry_name.grid(row=self.param_count, column=1, padx=5)
        tk.Label(self.inner_frame, text="Name:").grid(row=self.param_count, column=2, padx=5)
        entry_range_from.grid(row=self.param_count, column=3, padx=5)
        tk.Label(self.inner_frame, text="from").grid(row=self.param_count, column=4, padx=5)
        entry_range_to.grid(row=self.param_count, column=5, padx=5)
        tk.Label(self.inner_frame, text="to").grid(row=self.param_count, column=6, padx=5)
        entry_value.grid(row=self.param_count, column=7, padx=5)
        tk.Label(self.inner_frame, text="excluding").grid(row=self.param_count, column=8, padx=5)
        entry_step.grid(row=self.param_count, column=9, padx=5)
        tk.Label(self.inner_frame, text="with").grid(row=self.param_count, column=10, padx=5)

        # Increment the parameter count
        self.param_count += 1