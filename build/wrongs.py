import tkinter as tk
from pathlib import Path
from tkinter import PhotoImage
from sympy.parsing.latex import parse_latex 
from PIL import Image, ImageTk

class WrongsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#F5F5F5")

        self.visible_options = 1  
        self.entries = []  
        self.wrong_answers = []
        self.answer_number = 0

        # Top section: Non-scrollable
        self.top_frame = tk.Frame(self, bg="#F5F5F5")
        self.top_frame.pack(side="top", fill="x")
        self.create_top_section()

        # Middle section: Scrollable (this is where options will be added)
        self.scrollable_frame = tk.Frame(self, bg="#F5F5F5")
        self.scrollable_frame.pack(side="top", fill="both", expand=True)

        self.canvas = tk.Canvas(self.scrollable_frame, bg="#F5F5F5", bd=0, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.scrollable_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.inner_frame = tk.Frame(self.canvas, bg="#F5F5F5")
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
        self.inner_frame.bind("<Configure>", self.update_scroll_region)

        # Bottom section: Non-scrollable
        self.bottom_frame = tk.Frame(self, bg="#F5F5F5")
        self.bottom_frame.pack(side="bottom", fill="x")

        # Create the first option row
        self.create_middle_section()
        self.create_bottom_section()

    def relative_to_assets(self, path: str) -> Path:
        ASSETS_PATH = Path(__file__).parent / Path(r"./assets/frame1")
        return ASSETS_PATH / Path(path)

    def create_top_section(self):
        label = tk.Label(
            self.top_frame, 
            text="Wrong Answers", 
            bg="#F5F5F5", 
            fg="#1E1E1E", 
            font=("Inter", 20 * -1)
        )
        label.pack(anchor="nw", padx=10, pady=10)

        description = tk.Label(
            self.top_frame,
            text=(
                "Here you can set either the answer text (t:) to be parsed as a string or the answer "
                "function (f:) in terms of the parameters given in the previous page to calculate "
                "the wrong answer option."
            ),
            bg="#F5F5F5", 
            fg="#757575", 
            font=("Inter", 16 * -1), 
            wraplength=800, 
            justify="left"
        )
        description.pack(anchor="nw", padx=10)

    def create_middle_section(self):
        # Create the first row by default
        self.add_entry_field(1)

    def create_bottom_section(self):
        button_1_img = PhotoImage(file=self.relative_to_assets("button_1.png"))
        button_1 = tk.Button(
            self.bottom_frame,
            image=button_1_img,
            command=self.show_next_entry_field,
            relief="flat",
            bg="#F5F5F5",
            bd=0,
            activebackground="#F5F5F5"
        )
        button_1.image = button_1_img 
        button_1.pack(pady=5)

        number_label_info = tk.Label(
            self.bottom_frame,
            text=(
                "Specify how many of the wrong generated answers you want to be displayed "
                "to the student (Suggestion: 3)"
            ),
            bg="#F5F5F5",
            fg="#757575",
            font=("Inter", 14 * -1),
            wraplength=800,
            justify="left"
        )
        number_label_info.pack(anchor="w", padx=10, pady=(5, 0))

        number_label = tk.Label(
            self.bottom_frame,
            text="Number:",
            bg="#F5F5F5",
            fg="#1E1E1E",
            font=("Inter", 16 * -1)
        )
        number_label.pack(side="left", padx=(10, 0))

        self.answer_number_entry = tk.Entry(
            self.bottom_frame,
            bd=0,
            bg="#FFFFFF",
            fg="#000716",
            highlightthickness=0
        )
        self.answer_number_entry.pack(side="left", padx=(10, 0), pady=10, fill="x", expand=True)

        placeholders = {
            self.answer_number_entry: "Enter a value here..."
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

        button_2_img = PhotoImage(file=self.relative_to_assets("button_2.png"))
        button_2 = tk.Button(
            self.bottom_frame,
            image=button_2_img,
            command=self.process_entries_and_continue,
            relief="flat",
            bg="#F5F5F5",
            bd=0,
            activebackground="#F5F5F5"
        )
        button_2.image = button_2_img 
        button_2.pack(side="right", padx=5, pady=10)

    def update_scroll_region(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def add_entry_field(self, index):
        """
        Creates one "row" containing:
          - A label "Option {index}:"
          - An Entry
          - A trash-bin button if index > 1
        All inside row_frame, placed at (row=index) in inner_frame.
        """
        row_frame = tk.Frame(self.inner_frame, bg="#F5F5F5")
        row_frame.grid(row=index, column=0, sticky="w", pady=2)

        label = tk.Label(
            row_frame, 
            text=f"Option {index}:", 
            bg="#F5F5F5", 
            font=("Inter", 12)
        )
        label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        entry = tk.Entry(
            row_frame, 
            width=50, 
            bd=0, 
            bg="#FFFFFF", 
            fg="#000716", 
            highlightthickness=0
        )
        entry.grid(row=0, column=1, padx=5)

        # Placeholder handling for the entry
        new_placeholders = {entry: "Enter the string or function here..."}
        def on_focus_in(event):
            w = event.widget
            placeholder = new_placeholders.get(w)
            if placeholder and w.get() == placeholder:
                w.delete(0, "end")
                w.config(fg="#000716")

        def on_focus_out(event):
            w = event.widget
            placeholder = new_placeholders.get(w)
            if placeholder and w.get() == "":
                w.insert(0, placeholder)
                w.config(fg="#C0C0C0")

        entry.insert(0, new_placeholders[entry])
        entry.config(fg="#C0C0C0")
        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

        # Only show a trash bin for options after the first one
        if index > 1:
            trash_bin_path = self.relative_to_assets("trash_bin.png")
            trash_bin_image = Image.open(trash_bin_path)
            desired_width, desired_height = 20, 20
            trash_bin_image = trash_bin_image.resize((desired_width, desired_height), Image.Resampling.LANCZOS)
            trash_bin_photo = ImageTk.PhotoImage(trash_bin_image)

            # A small frame to hold the trash bin button
            trash_button_frame = tk.Frame(row_frame, width=desired_width + 10, height=desired_height + 10, bg="#F5F5F5")
            trash_button_frame.grid_propagate(False)
            trash_button_frame.grid(row=0, column=2, padx=5, pady=2)

            # Create the trash bin button
            trash_button = tk.Button(
                trash_button_frame,
                image=trash_bin_photo,
                borderwidth=0,
                highlightthickness=0,
                relief="flat",
                command=lambda: self.delete_option(option_frame)
            )
            trash_button.image = trash_bin_photo  # Keep a reference
            trash_button.pack(expand=True)

        # Store references in a dictionary
        option_frame = {
            'row_frame': row_frame,
            'label': label,
            'entry': entry
        }
        self.entries.append(option_frame)

    def show_next_entry_field(self):
        index = self.visible_options + 1
        self.add_entry_field(index)
        self.visible_options += 1
        self.update_scroll_region()

    def collect_wrong_answers(self):
        self.controller.shared_data["wrong_answers"] = self.wrong_answers
        self.controller.shared_data["answer_number"] = self.answer_number

    def process_entries_and_continue(self):
        self.wrong_answers.clear()

        # Access each entry from the dictionaries in self.entries
        for option_frame in self.entries:
            text = option_frame['entry'].get().strip()

            # If it's a "t:" or "f:" type
            if text.startswith("t:"):
                self.wrong_answers.append(text[2:].strip())
            elif text.startswith("f:"):
                latex_str = text[2:].strip()
                try:
                    sympy_expr = parse_latex(latex_str)
                    self.wrong_answers.append(sympy_expr)
                except Exception as e:
                    print(f"Error parsing LaTeX: {e}")
                    self.wrong_answers.append(None)
            else:
                # If there's no prefix, treat it as plain text or ignore
                self.wrong_answers.append(text)

        # Get the number of answers to show
        try:
            self.answer_number = int(self.answer_number_entry.get().strip())
        except ValueError:
            self.answer_number = 0  

        self.collect_wrong_answers()
        self.controller.show_frame("RandomizerPage")

    def delete_option(self, option_frame):
        """
        Destroys the entire row (label, entry, trash button) for the given option_frame,
        then reassigns row indices to the remaining rows.
        """
        # Do not allow deletion of the first row if that is your requirement
        if self.entries and self.entries[0] == option_frame:
            return

        # Remove the row_frame from the UI
        row_frame = option_frame.get('row_frame')
        if row_frame:
            row_frame.destroy()

        # Remove this option from the entries list
        if option_frame in self.entries:
            self.entries.remove(option_frame)
            self.visible_options -= 1

        # Reconfigure row numbers for remaining options
        for new_index, frame_dict in enumerate(self.entries, start=1):
            frame_dict['row_frame'].grid_configure(row=new_index)

        self.update_scroll_region()
