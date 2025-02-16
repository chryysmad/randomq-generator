import tkinter as tk
from pathlib import Path
from tkinter import PhotoImage, Text
import sympy as sp
from sympy.parsing.latex import parse_latex
from PIL import Image, ImageTk
import backend.util as util

class ParametersPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#F5F5F5")

        OUTPUT_PATH = Path(__file__).parent
        self.ASSETS_PATH = OUTPUT_PATH / Path(r"./assets/frame3")

        self.param_count = 1
        self.placeholders = {}
        self.entries = []
        self.latex_question = None
        self.parameters_data = []

        # Configure grid for three rows: top, middle, bottom.
        # Row 0: Top section (fixed height)
        # Row 1: Middle (scrollable) section (expands)
        # Row 2: Bottom section (fixed height)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Top section
        self.grid_rowconfigure(1, weight=1)  # Middle section (expandable)
        self.grid_rowconfigure(2, weight=0)  # Bottom section

        # --- Top section ---
        self.top_frame = tk.Frame(self, bg="#F5F5F5")
        self.top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        # Give the top canvas an explicit height so it doesn’t expand too far.
        self.top_canvas = tk.Canvas(
            self.top_frame,
            bg="#F5F5F5",
            bd=0,
            highlightthickness=0,
            height=250  # fixed height for top section
        )
        self.top_canvas.pack(fill="both", expand=True)
        self.create_top_section()

        # --- Middle (Scrollable) section ---
        self.scrollable_frame = tk.Frame(self)
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        # Use a different variable name for the scrollable canvas
        self.scroll_canvas = tk.Canvas(
            self.scrollable_frame,
            bg="#F5F5F5",
            bd=0,
            highlightthickness=0
        )
        self.scrollbar = tk.Scrollbar(
            self.scrollable_frame,
            orient="vertical",
            command=self.scroll_canvas.yview
        )
        self.scroll_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scroll_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.inner_frame = tk.Frame(self.scroll_canvas, bg="#F5F5F5")
        self.scroll_canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
        self.inner_frame.bind("<Configure>", self.update_scroll_region)
        self.create_middle_section()

        # --- Bottom section ---
        self.bottom_frame = tk.Frame(self, bg="#F5F5F5")
        self.bottom_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        self.create_bottom_section()

        # Bind mousewheel scrolling on the scrollable canvas
        self.scroll_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def relative_to_assets(self, path: str) -> Path:
        return self.ASSETS_PATH / Path(path)

    def convert_latex_to_sympy(self):
        # Assuming the LaTeX input is entered in the text widget from the top section
        latex_input = self.entry_1.get("1.0", "end-1c")
        try:
            self.latex_question = parse_latex(latex_input) 
        except Exception as e:
            util.logger.error(f"Error parsing LaTeX: {e}")

    def create_top_section(self):
        # Use self.top_canvas for drawing top section elements.
        self.top_canvas.create_text(
            24.0,
            54.0,
            anchor="nw",
            text="Latex Question",
            fill="#1E1E1E",
            font=("Inter", 20 * -1)
        )
        self.top_canvas.create_text(
            24.0,
            88.0,
            anchor="nw",
            text="Add the question you want in your h5p file in latex form.",
            fill="#757575",
            font=("Inter", 16 * -1)
        )
        # Load the image and keep a reference to avoid garbage collection.
        entry_image_1_path = self.relative_to_assets("entry_1.png")
        self.entry_image_1 = PhotoImage(file=entry_image_1_path)
        self.top_canvas.create_image(497.0, 178.5, image=self.entry_image_1)
        # Create a text widget for LaTeX input within the top frame.
        self.entry_1 = Text(self.top_frame, bd=0, bg="#FFFFFF", fg="#000716", highlightthickness=0)
        # Use .place to position it within the top_frame (adjust coordinates/sizes as needed)
        self.entry_1.place(x=32.0, y=120.0, width=930.0, height=115.0)
        
        self.placeholders = {self.entry_1: "Add here..."}
        def on_focus_in(event):
            entry = event.widget
            placeholder = self.placeholders.get(entry)
            if placeholder and entry.get("1.0", "end-1c") == placeholder:
                entry.delete("1.0", "end")
                entry.config(fg="#000716")
        def on_focus_out(event):
            entry = event.widget
            placeholder = self.placeholders.get(entry)
            if placeholder and entry.get("1.0", "end-1c") == "":
                entry.insert("1.0", placeholder)
                entry.config(fg="#C0C0C0")
        self.entry_1.bind("<FocusIn>", on_focus_in)
        self.entry_1.bind("<FocusOut>", on_focus_out)
        self.entry_1.insert("1.0", self.placeholders[self.entry_1])
        self.entry_1.config(fg="#C0C0C0")

    def create_middle_section(self):
        param_id = self.param_count
        param_frame = {}

        # container frame for the entire row.
        row_frame = tk.Frame(self.inner_frame, bg="#F5F5F5")
        row_frame.grid(row=param_id, column=0, columnspan=11, sticky="w", pady=2)
        param_frame['row_frame'] = row_frame

        label = tk.Label(
            row_frame,
            text=f"Param {param_id}:",
            bg="#F5F5F5",
            font=("Inter", 16 * -1)
        )
        label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        entry_name = tk.Entry(row_frame, width=6, bd=0, bg="#FFFFFF", fg="#000716", highlightthickness=0)
        entry_name.grid(row=0, column=1, padx=5)
        param_frame['name'] = entry_name

        tk.Label(row_frame, text="from", bg="#F5F5F5", font=("Inter", 16 * -1)).grid(row=0, column=2, padx=5)

        entry_from = tk.Entry(row_frame, width=10, bd=0, bg="#FFFFFF", fg="#000716", highlightthickness=0)
        entry_from.grid(row=0, column=3, padx=5)
        param_frame['range_from'] = entry_from

        tk.Label(row_frame, text="to", bg="#F5F5F5", font=("Inter", 16 * -1)).grid(row=0, column=4, padx=5)

        entry_to = tk.Entry(row_frame, width=10, bd=0, bg="#FFFFFF", fg="#000716", highlightthickness=0)
        entry_to.grid(row=0, column=5, padx=5)
        param_frame['range_to'] = entry_to

        tk.Label(row_frame, text="excluding", bg="#F5F5F5", font=("Inter", 16 * -1)).grid(row=0, column=6, padx=5)

        entry_excluding = tk.Entry(row_frame, width=15, bd=0, bg="#FFFFFF", fg="#000716", highlightthickness=0)
        entry_excluding.grid(row=0, column=7, padx=5)
        param_frame['excluding'] = entry_excluding

        tk.Label(row_frame, text="with", bg="#F5F5F5", font=("Inter", 16 * -1)).grid(row=0, column=8, padx=5)

        entry_step = tk.Entry(row_frame, width=15, bd=0, bg="#FFFFFF", fg="#000716", highlightthickness=0)
        entry_step.grid(row=0, column=9, padx=5)
        param_frame['step'] = entry_step

        if self.param_count > 1:
            trash_bin_path = self.relative_to_assets("trash_bin.png")
            trash_bin_image = Image.open(trash_bin_path)
            desired_width = 20
            desired_height = 20
            trash_bin_image = trash_bin_image.resize((desired_width, desired_height), Image.Resampling.LANCZOS)
            trash_bin_photo = ImageTk.PhotoImage(trash_bin_image)

            trash_button_frame = tk.Frame(row_frame, width=desired_width + 10, height=desired_height + 10, bg="#F5F5F5")
            trash_button_frame.grid_propagate(False)
            trash_button_frame.grid(row=0, column=10, padx=5, pady=2)

            trash_button = tk.Button(
                trash_button_frame,
                image=trash_bin_photo,
                borderwidth=0,
                highlightthickness=0,
                relief="flat",
                command=lambda: self.delete_parameter(param_frame)
            )
            trash_button.image = trash_bin_photo 
            trash_button.pack(expand=True)
            param_frame['trash_button_frame'] = trash_button_frame


        new_placeholders = {
            entry_name: "Name...",
            entry_from: "Range...",
            entry_to: "Range...",
            entry_excluding: "Value...",
            entry_step: "Step..."
        }

        def on_focus_in(event):
            entry = event.widget
            placeholder = new_placeholders.get(entry)
            if placeholder and entry.get() == placeholder:
                entry.delete(0, "end")
                entry.config(fg="#000716")
        def on_focus_out(event):
            entry = event.widget
            placeholder = new_placeholders.get(entry)
            if placeholder and entry.get() == "":
                entry.insert(0, placeholder)
                entry.config(fg="#C0C0C0")
        for entry, placeholder in new_placeholders.items():
            entry.insert(0, placeholder)
            entry.config(fg="#C0C0C0")
            entry.bind("<FocusIn>", on_focus_in)
            entry.bind("<FocusOut>", on_focus_out)

        self.entries.append(param_frame)
        self.param_count += 1
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
        button_1.pack(side="left", padx=5, pady=10)

        button_2 = tk.Button(
            self.bottom_frame,
            image=self.button_image_2,
            borderwidth=0,
            highlightthickness=0,
            command=self.on_next,
            relief="flat"
        )
        button_2.pack(side="right", padx=5, pady=10)

    def update_scroll_region(self, event=None):
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))

    def _on_mousewheel(self, event):
        self.scroll_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def add_parameter(self):
        self.create_middle_section()

    def on_next(self):
        self.convert_latex_to_sympy()
        self.controller.save_latex_question(self.latex_question)

        for param_frame in self.entries:
            param_data = {
                "name": param_frame['name'].get(),
                "range_from": param_frame['range_from'].get(),
                "range_to": param_frame['range_to'].get(),
                "excluding": param_frame['excluding'].get(),
                "step": param_frame['step'].get(),
            }
            self.parameters_data.append(param_data)

        self.controller.save_parameters(self.parameters_data)
        self.controller.show_frame("CorrectPage")

    def delete_parameter(self, param_frame):
        if self.entries and self.entries[0] == param_frame:
            return

        row_frame = param_frame.get('row_frame')
        if row_frame:
            row_frame.destroy()

        if param_frame in self.entries:
            self.entries.remove(param_frame)
            self.param_count -= 1

        for new_id, p in enumerate(self.entries, start=1):
            row = p.get('row_frame')
            if row:
                row.grid_configure(row=new_id)

        self.update_scroll_region()


