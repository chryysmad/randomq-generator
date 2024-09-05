import tkinter as tk
from pathlib import Path
from tkinter import PhotoImage, Text
import sympy as sp
from sympy.parsing.latex import parse_latex

class ParametersPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#F5F5F5")

        OUTPUT_PATH = Path(__file__).parent
        self.ASSETS_PATH = OUTPUT_PATH / Path(r"/home/chrysmad/randomq-generator/build/assets/frame3")

        self.param_count = 1
        self.placeholders = {}

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

        self.canvas = tk.Canvas(self.scrollable_frame, bg="#F5F5F5", bd=0, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.scrollable_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.inner_frame = tk.Frame(self.canvas, bg="#F5F5F5")
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        self.inner_frame.bind("<Configure>", self.update_scroll_region)

        self.create_middle_section()

        # Bottom section: "+" button and "Next" button 
        self.bottom_frame = tk.Frame(self, bg="#F5F5F5")
        self.bottom_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)

        self.create_bottom_section()

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Storing the latex question and the parameters
        self.latex_question = None
        self.parameters_data = []

    def relative_to_assets(self, path: str) -> Path:
        return self.ASSETS_PATH / Path(path)

    def convert_latex_to_sympy(self):
        latex_input = self.entry_1.get("1.0", "end-1c")
        try:
            self.latex_question = parse_latex(latex_input) 
            print(f"SymPy Expression: {self.latex_question}")
        except Exception as e:
            print(f"Error parsing LaTeX: {e}")

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
        label = tk.Label(self.inner_frame, text=f"Param {self.param_count}:", bg="#F5F5F5", font=("Inter", 16 * -1))
        label.grid(row=self.param_count, column=0, padx=10, pady=5, sticky="w")

        self.entry_2 = tk.Entry(self.inner_frame, width=6, bd=0, bg="#FFFFFF", fg="#000716", highlightthickness=0)
        self.entry_2.grid(row=self.param_count, column=1, padx=5)

        tk.Label(self.inner_frame, text="from", bg="#F5F5F5", font=("Inter", 16 * -1)).grid(row=self.param_count, column=2, padx=5)

        self.entry_3 = tk.Entry(self.inner_frame, width=10, bd=0, bg="#FFFFFF", fg="#000716", highlightthickness=0)
        self.entry_3.grid(row=self.param_count, column=3, padx=5)

        tk.Label(self.inner_frame, text="to", bg="#F5F5F5", font=("Inter", 16 * -1)).grid(row=self.param_count, column=4, padx=5)

        self.entry_4 = tk.Entry(self.inner_frame, width=10, bd=0, bg="#FFFFFF", fg="#000716", highlightthickness=0)
        self.entry_4.grid(row=self.param_count, column=5, padx=5)

        tk.Label(self.inner_frame, text="excluding", bg="#F5F5F5", font=("Inter", 16 * -1)).grid(row=self.param_count, column=6, padx=5)

        self.entry_5 = tk.Entry(self.inner_frame, width=15, bd=0, bg="#FFFFFF", fg="#000716", highlightthickness=0)
        self.entry_5.grid(row=self.param_count, column=7, padx=5)

        tk.Label(self.inner_frame, text="with", bg="#F5F5F5", font=("Inter", 16 * -1)).grid(row=self.param_count, column=8, padx=5)

        self.entry_6 = tk.Entry(self.inner_frame, width=15, bd=0, bg="#FFFFFF", fg="#000716", highlightthickness=0)
        self.entry_6.grid(row=self.param_count, column=9, padx=5)

        new_placeholders = {
            self.entry_2: "Name...",
            self.entry_3: "Range...",
            self.entry_4: "Range...",
            self.entry_5: "Value...",
            self.entry_6: "Step..."
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
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def add_parameter(self):
        self.create_middle_section()

    def on_next(self):
        self.convert_latex_to_sympy()
        print("SymPy Expression:", self.latex_question)
        self.controller.save_latex_question(self.latex_question)

        param_data = {
            "name": self.entry_2.get(),
            "range_from": self.entry_3.get(),
            "range_to": self.entry_4.get(),
            "excluding": self.entry_5.get(),
            "step": self.entry_6.get(),
        }
        self.parameters_data.append(param_data)
        print(f"Added parameter: {param_data}")

        print("Parameters Data:", self.parameters_data)
        self.controller.save_parameters(self.parameters_data)
        
        self.controller.show_frame("CorrectPage")
