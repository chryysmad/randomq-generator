import tkinter as tk
from pathlib import Path
from tkinter import PhotoImage
from sympy.parsing.latex import parse_latex 
import backend.util as util
from PIL import Image, ImageTk

class WrongsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#F5F5F5")

        self.option_counter = 1 
        self.entries = []   
        self.wrong_answers = []
        self.answer_number = 0

        # Top section
        self.top_frame = tk.Frame(self, bg="#F5F5F5")
        self.top_frame.pack(side="top", fill="x")
        self.create_top_section()

        # Middle (scrollable) section
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

        # Bottom section
        self.bottom_frame = tk.Frame(self, bg="#F5F5F5")
        self.bottom_frame.pack(side="bottom", fill="x")

        self.add_entry_field()  # always create one row at start
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
                "to the student (Suggestion: 3). The number should be less than or equal "
                "to the number of options provided above."
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

        # create spinbox with a default value of 1
        self.answer_number_spinbox = tk.Spinbox(
            self.bottom_frame,
            from_=1,
            to=(len(self.entries) if self.entries else 1),
            width=5,
            bd=0,
            bg="#FFFFFF",
            fg="#000716",
            font=("Inter", 16 * -1),
            validate="focusout",
            validatecommand=self.validate_spinbox
        )

        self.answer_number_spinbox.delete(0, tk.END)
        self.answer_number_spinbox.insert(0, "1")
        self.answer_number_spinbox.pack(side="left", padx=(10, 0), pady=10)

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

        if hasattr(self, 'answer_number_spinbox'):
            new_max = len(self.entries) if len(self.entries) > 0 else 1
            self.answer_number_spinbox.config(to=new_max)
           
            try:
                current_val = int(self.answer_number_spinbox.get())
            except ValueError:
                current_val = 1
            if current_val > new_max:
                self.answer_number_spinbox.delete(0, tk.END)
                self.answer_number_spinbox.insert(0, str(new_max))

    def validate_spinbox(self):
        try:
            value = int(self.answer_number_spinbox.get())
        except ValueError:
            value = 1
        max_val = len(self.entries) if len(self.entries) > 0 else 1
        if value > max_val:
            self.answer_number_spinbox.delete(0, tk.END)
            self.answer_number_spinbox.insert(0, str(max_val))
        return True

    def add_entry_field(self):
        grid_row = len(self.entries) + 1
        row_frame = tk.Frame(self.inner_frame, bg="#F5F5F5")
        row_frame.grid(row=grid_row, column=0, sticky="w", pady=2)

        label_num = self.option_counter
        self.option_counter += 1

        label = tk.Label(
            row_frame, 
            text=f"Option {label_num}:", 
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

        if len(self.entries) >= 1:
            trash_bin_path = self.relative_to_assets("trash_bin.png")
            trash_bin_image = Image.open(trash_bin_path)
            desired_width, desired_height = 20, 20
            trash_bin_image = trash_bin_image.resize((desired_width, desired_height), Image.Resampling.LANCZOS)
            trash_bin_photo = ImageTk.PhotoImage(trash_bin_image)

            trash_button_frame = tk.Frame(row_frame, width=desired_width + 10, height=desired_height + 10, bg="#F5F5F5")
            trash_button_frame.grid_propagate(False)
            trash_button_frame.grid(row=0, column=2, padx=5, pady=2)

            trash_button = tk.Button(
                trash_button_frame,
                image=trash_bin_photo,
                borderwidth=0,
                highlightthickness=0,
                relief="flat",
                command=lambda: self.delete_option(option_frame)
            )
            trash_button.image = trash_bin_photo
            trash_button.pack(expand=True)

        option_frame = {
            'row_frame': row_frame,
            'label': label,
            'entry': entry,
            'label_num': label_num  
        }
        self.entries.append(option_frame)
        self.update_scroll_region()

    def show_next_entry_field(self):
        self.add_entry_field()
        self.update_scroll_region()

    def collect_wrong_answers(self):
        self.controller.shared_data["wrong_answers"] = self.wrong_answers
        try:
            self.answer_number = int(self.answer_number_spinbox.get())
        except ValueError:
            self.answer_number = 0
        self.controller.shared_data["answer_number"] = self.answer_number

    def process_entries_and_continue(self):
        self.wrong_answers.clear()

        for option_frame in self.entries:
            text = option_frame['entry'].get().strip()
            if text.startswith("t:"):
                self.wrong_answers.append(text[2:].strip())
            elif text.startswith("f:"):
                latex_str = text[2:].strip()
                try:
                    sympy_expr = parse_latex(latex_str)
                    self.wrong_answers.append(sympy_expr)
                except Exception as e:
                    util.logger.error(f"Error parsing LaTeX: {e}")
                    self.wrong_answers.append(None)
            else:
                self.wrong_answers.append(text)

        self.collect_wrong_answers()
        self.controller.show_frame("RandomizerPage")

    def delete_option(self, option_frame):
        row_frame = option_frame.get('row_frame')
        if row_frame:
            row_frame.destroy()

        if option_frame in self.entries:
            self.entries.remove(option_frame)

        for new_index, frame_dict in enumerate(self.entries, start=1):
            frame_dict['row_frame'].grid_configure(row=new_index)

        self.update_scroll_region()
