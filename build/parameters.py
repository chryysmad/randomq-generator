import tkinter as tk
from pathlib import Path
from tkinter import PhotoImage, Text
import sympy as sp
from sympy.parsing.latex import parse_latex
from PIL import Image, ImageTk
import backend.util as util
import re

class ParametersPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#F5F5F5")

        OUTPUT_PATH = Path(__file__).parent
        self.ASSETS_PATH = OUTPUT_PATH / Path(r"./assets/frame3")

        self.param_counter = 1
        self.entries = []
        self.placeholders = {}

        # Variables to store the question text and formula info
        self.question_full_text = ""
        self.latex_question = None
        self.formula_index = None
        self.formula_length = 0

        self.parameters_data = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)

        # --- Top section with ONE Text Box ---
        self.top_frame = tk.Frame(self, bg="#F5F5F5")
        self.top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.top_canvas = tk.Canvas(
            self.top_frame,
            bg="#F5F5F5",
            bd=0,
            highlightthickness=0,
            height=220
        )
        self.top_canvas.pack(fill="both", expand=True)
        self.create_top_section()

        # --- Middle (Scrollable) section ---
        self.scrollable_frame = tk.Frame(self)
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

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

        self.add_parameter_row()

        # --- Bottom section ---
        self.bottom_frame = tk.Frame(self, bg="#F5F5F5")
        self.bottom_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        self.create_bottom_section()

        # --- Back Button (returns to ControlPage) ---
        self.back_button = tk.Button(
            self,
            text="Back",
            font=("Inter", 12),
            bg="#F5F5F5",
            fg="#1E1E1E",
            relief="flat",
            borderwidth=0,
            command=self.go_back
        )
        self.back_button.grid(row=3, column=0, sticky="w", padx=20, pady=(0,10))

        self.scroll_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def relative_to_assets(self, path: str) -> Path:
        return self.ASSETS_PATH / Path(path)

    def convert_latex_to_sympy(self):
        """
        Parses the combined text input.
        Looks for a LaTeX expression enclosed in [ ... ], and if found, records:
         - The full text as entered,
         - The starting index and length of the bracketed substring,
         - Parses the LaTeX expression.
        """
        full_text = self.entry_combined.get("1.0", "end-1c")
        self.question_full_text = full_text
        self.controller.save_has_visited_parameters(True)

        match = re.search(r'\$\$([^$]+)\$\$', full_text)
        if match:
            self.formula_index = match.start()
            self.formula_length = match.end() - match.start()
            formula_text = match.group(1)
            try:
                util.logger.info(f"Formula text: {formula_text}")
                self.latex_question = parse_latex(formula_text)
                util.logger.info(f"Parsed expression: {self.latex_question}")
                return True
            except Exception as e:
                util.logger.error(f"Error parsing LaTeX: {e}")
                self.latex_question = None
                return False
        else:
            util.logger.error("No LaTeX expression found in the input.")
            self.latex_question = None
            self.formula_index = None
            self.formula_length = 0
            return False

    def create_top_section(self):
        """
        Creates a single text box where the user can enter text in the form:
          <some text> [LaTeX expression] <some text>
        """
        self.top_canvas.create_text(
            32.0,
            10.0,
            anchor="nw",
            text=("Enter your entire question in one line. You may add non-evaluated LaTeX formulas using \\(<formula>\\):\n"
              "(e.g. 'Solve the equation $$x^2 + 3x = 0$$ for \\(x\\)')."),
            fill="#1E1E1E",
            font=("Inter", 16 * -1)
        )

        self.entry_combined = tk.Text(
            self.top_frame,
            bd=0,
            bg="#FFFFFF",
            fg="#C0C0C0",
            highlightthickness=0
        )
        self.entry_combined.place(x=32.0, y=60.0, width=930.0, height=80)
        self.placeholders[self.entry_combined] = "Type your question here: text [LaTeX] text..."

        def on_focus_in(event):
            widget = event.widget
            placeholder = self.placeholders.get(widget)
            if placeholder and widget.get("1.0", "end-1c") == placeholder:
                widget.delete("1.0", "end")
                widget.config(fg="#000716")

        def on_focus_out(event):
            widget = event.widget
            placeholder = self.placeholders.get(widget)
            if placeholder and widget.get("1.0", "end-1c") == "":
                widget.insert("1.0", placeholder)
                widget.config(fg="#C0C0C0")

        self.entry_combined.bind("<FocusIn>", on_focus_in)
        self.entry_combined.bind("<FocusOut>", on_focus_out)
        self.entry_combined.insert("1.0", self.placeholders[self.entry_combined])

        self.top_canvas.create_text(
            32.0,
            155.0,
            anchor="nw",
            text="Precision:",
            fill="#1E1E1E",
            font=("Inter", 16 * -1)
        )

        def validate_digit(P):
            return P.isdigit() or P == ""
        vcmd = self.register(validate_digit)
        self.precision_entry = tk.Entry(
            self.top_frame,
            bd=0,
            bg="#FFFFFF",
            fg="#000716",
            highlightthickness=0,
            validate="key",
            validatecommand=(vcmd, '%P')
        )
        self.precision_entry.place(x=150.0, y=150.0, width=100.0, height=30)
        self.precision_entry.insert(0, "0")

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
        self.add_parameter_row()

    def add_parameter_row(self):
        grid_row = len(self.entries) + 1
        row_frame = tk.Frame(self.inner_frame, bg="#F5F5F5")
        row_frame.grid(row=grid_row, column=0, columnspan=11, sticky="w", pady=2)

        param_label = f"Param {self.param_counter}:"
        self.param_counter += 1

        label = tk.Label(
            row_frame,
            text=param_label,
            bg="#F5F5F5",
            font=("Inter", 16 * -1)
        )
        label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        entry_name = tk.Entry(row_frame, width=6, bd=0, bg="#FFFFFF", fg="#000716", highlightthickness=0)
        entry_name.grid(row=0, column=1, padx=5)

        tk.Label(row_frame, text="from", bg="#F5F5F5", font=("Inter", 16 * -1)).grid(row=0, column=2, padx=5)

        entry_from = tk.Entry(row_frame, width=10, bd=0, bg="#FFFFFF", fg="#000716", highlightthickness=0)
        entry_from.grid(row=0, column=3, padx=5)

        tk.Label(row_frame, text="to", bg="#F5F5F5", font=("Inter", 16 * -1)).grid(row=0, column=4, padx=5)

        entry_to = tk.Entry(row_frame, width=10, bd=0, bg="#FFFFFF", fg="#000716", highlightthickness=0)
        entry_to.grid(row=0, column=5, padx=5)

        tk.Label(row_frame, text="excluding", bg="#F5F5F5", font=("Inter", 16 * -1)).grid(row=0, column=6, padx=5)

        entry_excluding = tk.Entry(row_frame, width=15, bd=0, bg="#FFFFFF", fg="#000716", highlightthickness=0)
        entry_excluding.grid(row=0, column=7, padx=5)

        tk.Label(row_frame, text="with", bg="#F5F5F5", font=("Inter", 16 * -1)).grid(row=0, column=8, padx=5)

        entry_step = tk.Entry(row_frame, width=15, bd=0, bg="#FFFFFF", fg="#000716", highlightthickness=0)
        entry_step.grid(row=0, column=9, padx=5)

        if len(self.entries) >= 1:
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

        new_placeholders = {
            entry_name: "Name...",
            entry_from: "Range...",
            entry_to: "Range...",
            entry_excluding: "Value...",
            entry_step: "Step..."
        }

        def on_focus_in(event):
            widget = event.widget
            placeholder = new_placeholders.get(widget)
            if placeholder and widget.get() == placeholder:
                widget.delete(0, "end")
                widget.config(fg="#000716")

        def on_focus_out(event):
            widget = event.widget
            placeholder = new_placeholders.get(widget)
            if placeholder and widget.get() == "":
                widget.insert(0, placeholder)
                widget.config(fg="#C0C0C0")

        for entry_widget, placeholder_text in new_placeholders.items():
            entry_widget.insert(0, placeholder_text)
            entry_widget.config(fg="#C0C0C0")
            entry_widget.bind("<FocusIn>", on_focus_in)
            entry_widget.bind("<FocusOut>", on_focus_out)

        param_frame = {
            'row_frame': row_frame,
            'label': label,
            'name': entry_name,
            'range_from': entry_from,
            'range_to': entry_to,
            'excluding': entry_excluding,
            'step': entry_step
        }

        self.entries.append(param_frame)
        self.update_scroll_region()

    def on_next(self):
        # Parse the combined text input and extract formula info.
        
        if not self.convert_latex_to_sympy():
            util.logger.error("No valid LaTeX expression found.")
            return
        self.controller.save_latex_question(self.latex_question)
        self.controller.save_question_text(self.question_full_text)
        self.controller.save_precision(self.precision_entry.get())
        # Save formula index and length if available
        if self.formula_index is not None:
            self.controller.save_formula_index(self.formula_index)
            self.controller.save_formula_length(self.formula_length)

        self.parameters_data.clear()
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

        for new_row_index, p in enumerate(self.entries, start=1):
            row = p.get('row_frame')
            if row:
                row.grid_configure(row=new_row_index)

        self.update_scroll_region()

    def go_back(self):
        self.controller.show_frame("ControlPage")
