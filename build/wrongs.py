import tkinter as tk
from pathlib import Path
from tkinter import PhotoImage
from sympy.parsing.latex import parse_latex 
import backend.util as util
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

        self.create_middle_section()
        self.create_bottom_section()

    def relative_to_assets(self, path: str) -> Path:
        ASSETS_PATH = Path(__file__).parent / Path(r"./assets/frame1")
        return ASSETS_PATH / Path(path)

    def create_top_section(self):
        label = tk.Label(self.top_frame, text="Wrong Answers", bg="#F5F5F5", fg="#1E1E1E", font=("Inter", 20 * -1))
        label.pack(anchor="nw", padx=10, pady=10)

        description = tk.Label(self.top_frame, text="Here you can set either the answer text (t:) to be parsed as a string or the answer function (f:) in terms of the parameters given in the previous page to calculate the wrong answer option.",
                               bg="#F5F5F5", fg="#757575", font=("Inter", 16 * -1), wraplength=800, justify="left")
        description.pack(anchor="nw", padx=10)

    def create_middle_section(self):
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

        number_label_info = tk.Label(self.bottom_frame, text="Specify how many of the wrong generated answers you want to be displayed to the student (Suggestion: 3)",
                                     bg="#F5F5F5", fg="#757575", font=("Inter", 14 * -1), wraplength=800, justify="left")
        number_label_info.pack(anchor="w", padx=10, pady=(5, 0))

        number_label = tk.Label(self.bottom_frame, text="Number:", bg="#F5F5F5", fg="#1E1E1E", font=("Inter", 16 * -1))
        number_label.pack(side="left", padx=(10, 0))

        self.answer_number_entry = tk.Entry(self.bottom_frame, bd=0, bg="#FFFFFF", fg="#000716", highlightthickness=0)
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
        label = tk.Label(self.inner_frame, text=f"Option {index}:", bg="#F5F5F5", font=("Inter", 12))
        entry = tk.Entry(self.inner_frame, width=50, bd=0, bg="#FFFFFF", fg="#000716", highlightthickness=0)

        new_placeholders = {
            entry: "Enter the string or function here..."
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

        label.grid(row=index, column=0, padx=10, pady=5, sticky="w")
        entry.grid(row=index, column=1, padx=5)

        self.entries.append((label, entry))

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

        for label, entry in self.entries:
            text = entry.get().strip()
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

        try:
            self.answer_number = int(self.answer_number_entry.get().strip())
        except ValueError:
            self.answer_number = 0  

        self.collect_wrong_answers()
        self.controller.show_frame("RandomizerPage")
