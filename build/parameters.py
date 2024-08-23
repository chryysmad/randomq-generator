import tkinter as tk
from pathlib import Path
from tkinter import PhotoImage, Text

class ParametersPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#F5F5F5")

        OUTPUT_PATH = Path(__file__).parent
        self.ASSETS_PATH = OUTPUT_PATH / Path(r"/home/chrysmad/randomq-generator/build/assets/frame3")

        self.param_count = 1

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)  

        # Top section: non-scrollable
        self.top_frame = tk.Frame(self, bg="#F5F5F5")
        self.top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        self.canvas = tk.Canvas(self.top_frame, bg="#F5F5F5", bd=0, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.create_top_section()

        # Scrollable section: for parameters
        self.scrollable_frame = tk.Frame(self)
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Canvas and Scrollbar setup
        self.canvas = tk.Canvas(self.scrollable_frame, bg="#F5F5F5", bd=0, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.scrollable_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Pack the canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Frame inside the canvas to hold the scrollable content
        self.inner_frame = tk.Frame(self.canvas, bg="#F5F5F5")
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        # Update the scroll region when the size of the inner_frame changes
        self.inner_frame.bind("<Configure>", self.update_scroll_region)

        # Add initial content
        self.create_middle_section()

        # Bottom section: "+" button and "Next" button 
        self.bottom_frame = tk.Frame(self, bg="#F5F5F5")
        self.bottom_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)

        self.create_bottom_section()

        # Bind mouse scroll to canvas
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def relative_to_assets(self, path: str) -> Path:
        return self.ASSETS_PATH / Path(path)

    def create_top_section(self):
        self.canvas.create_text(
            24.0,
            54.0,
            anchor="nw",
            text="Latex Question",
            fill="#1E1E1E",
            font=("Inter", 20 * -1)
        )

        self.canvas.create_text(
            24.0,
            88.0,
            anchor="nw",
            text="Add the question you want in your h5p file in latex form.",
            fill="#757575",
            font=("Inter", 16 * -1)
        )

        entry_image_1_path = self.relative_to_assets("entry_1.png")
        entry_image_1 = PhotoImage(file=entry_image_1_path)
        self.canvas.create_image(497.0, 178.5, image=entry_image_1)
        self.entry_1 = Text(self.top_frame, bd=0, bg="#FFFFFF", fg="#000716", highlightthickness=0)
        self.entry_1.place(x=32.0, y=120.0, width=930.0, height=115.0)
        self.entry_1.insert("1.0", "Add here...")
        self.entry_1.config(fg="#C0C0C0")

    def create_middle_section(self):
        label = tk.Label(self.inner_frame, text=f"Param {self.param_count}:", bg="#F5F5F5", font=("Inter", 16 * -1))
        label.grid(row=self.param_count, column=0, padx=10, pady=5, sticky="w")

        self.entry_2 = tk.Entry(self.inner_frame, bd=0, bg="#FFFFFF", fg="#000716", highlightthickness=0)
        self.entry_2.grid(row=self.param_count, column=1, padx=5)

        tk.Label(self.inner_frame, text="from", bg="#F5F5F5", font=("Inter", 16 * -1)).grid(row=self.param_count, column=2, padx=5)

        self.entry_3 = tk.Entry(self.inner_frame, bd=0, bg="#FFFFFF", fg="#000716", highlightthickness=0)
        self.entry_3.grid(row=self.param_count, column=3, padx=5)

        tk.Label(self.inner_frame, text="to", bg="#F5F5F5", font=("Inter", 16 * -1)).grid(row=self.param_count, column=4, padx=5)

        self.entry_4 = tk.Entry(self.inner_frame, bd=0, bg="#FFFFFF", fg="#000716", highlightthickness=0)
        self.entry_4.grid(row=self.param_count, column=5, padx=5)

        tk.Label(self.inner_frame, text="excluding", bg="#F5F5F5", font=("Inter", 16 * -1)).grid(row=self.param_count, column=6, padx=5)

        self.entry_5 = tk.Entry(self.inner_frame, bd=0, bg="#FFFFFF", fg="#000716", highlightthickness=0)
        self.entry_5.grid(row=self.param_count, column=7, padx=5)

        tk.Label(self.inner_frame, text="with", bg="#F5F5F5", font=("Inter", 16 * -1)).grid(row=self.param_count, column=8, padx=5)

        self.entry_6 = tk.Entry(self.inner_frame, bd=0, bg="#FFFFFF", fg="#000716", highlightthickness=0)
        self.entry_6.grid(row=self.param_count, column=9, padx=5)

        self.param_count += 1

        # Update scroll region whenever a new parameter is added
        self.update_scroll_region()

    def create_bottom_section(self):
        self.button_image_1 = PhotoImage(file=self.relative_to_assets("button_1.png"))
        self.button_image_2 = PhotoImage(file=self.relative_to_assets("button_2.png"))

        button_1 = tk.Button(
            self.bottom_frame,
            image=self.button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=self.add_parameter,
            relief="flat"
        )
        button_1.pack(side="left", padx=5, pady=10)  # Adjusted positioning

        button_2 = tk.Button(
            self.bottom_frame,
            image=self.button_image_2,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.controller.show_frame("CorrectPage"),
            relief="flat"
        )
        button_2.pack(side="right", padx=5, pady=10)  # Adjusted positioning

    def update_scroll_region(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def add_parameter(self):
        self.create_middle_section()
