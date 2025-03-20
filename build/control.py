# File: control.py
import tkinter as tk
from pathlib import Path
import backend.util as util

class ControlPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#F5F5F5")

        # Title label
        label_title = tk.Label(
            self,
            text="H5P Control Settings",
            font=("Inter", 24),
            bg="#F5F5F5"
        )
        label_title.grid(row=0, column=0, columnspan=2, padx=20, pady=(20,10), sticky="w")

        # NAME_H5P
        tk.Label(self, text="NAME_H5P:", font=("Inter", 16), bg="#F5F5F5").grid(
            row=1, column=0, padx=20, pady=5, sticky="e"
        )
        self.name_h5p_entry = tk.Entry(self, bd=0, bg="#FFFFFF", fg="#000716", highlightthickness=0)
        self.name_h5p_entry.grid(row=1, column=1, padx=(0,20), pady=5, sticky="w")
        self.name_h5p_entry.insert(0, "example-file.h5p")

        # TITLE
        tk.Label(self, text="TITLE:", font=("Inter", 16), bg="#F5F5F5").grid(
            row=2, column=0, padx=20, pady=5, sticky="e"
        )
        self.title_entry = tk.Entry(self, bd=0, bg="#FFFFFF", fg="#000716", highlightthickness=0, width=40)
        self.title_entry.grid(row=2, column=1, padx=(0,20), pady=5, sticky="w")
        self.title_entry.insert(0, "This is the Title of the Quiz!")

        # AUTHOR
        tk.Label(self, text="AUTHOR:", font=("Inter", 16), bg="#F5F5F5").grid(
            row=3, column=0, padx=20, pady=5, sticky="e"
        )
        self.author_entry = tk.Entry(self, bd=0, bg="#FFFFFF", fg="#000716", highlightthickness=0)
        self.author_entry.grid(row=3, column=1, padx=(0,20), pady=5, sticky="w")
        self.author_entry.insert(0, "chryysmad")

        # INTRODUCTION
        tk.Label(self, text="INTRODUCTION:", font=("Inter", 16), bg="#F5F5F5").grid(
            row=4, column=0, padx=20, pady=5, sticky="e"
        )
        self.intro_entry = tk.Entry(self, bd=0, bg="#FFFFFF", fg="#000716", highlightthickness=0, width=60)
        self.intro_entry.grid(row=4, column=1, padx=(0,20), pady=5, sticky="w")
        self.intro_entry.insert(0, "An H5P Question Set made with txt2h5p-generator...")

        # PASS_PERCENTAGE
        tk.Label(self, text="PASS_PERCENTAGE:", font=("Inter", 16), bg="#F5F5F5").grid(
            row=5, column=0, padx=20, pady=5, sticky="e"
        )
        self.pass_percentage_entry = tk.Entry(self, bd=0, bg="#FFFFFF", fg="#000716", highlightthickness=0)
        self.pass_percentage_entry.grid(row=5, column=1, padx=(0,20), pady=5, sticky="w")
        self.pass_percentage_entry.insert(0, "50")

        # POOL_SIZE
        tk.Label(self, text="POOL_SIZE:", font=("Inter", 16), bg="#F5F5F5").grid(
            row=6, column=0, padx=20, pady=5, sticky="e"
        )
        self.pool_size_entry = tk.Entry(self, bd=0, bg="#FFFFFF", fg="#000716", highlightthickness=0)
        self.pool_size_entry.grid(row=6, column=1, padx=(0,20), pady=5, sticky="w")
        self.pool_size_entry.insert(0, "3")

        # N_QUESTIONS
        tk.Label(self, text="N_QUESTIONS:", font=("Inter", 16), bg="#F5F5F5").grid(
            row=7, column=0, padx=20, pady=5, sticky="e"
        )
        self.n_questions_entry = tk.Entry(self, bd=0, bg="#FFFFFF", fg="#000716", highlightthickness=0)
        self.n_questions_entry.grid(row=7, column=1, padx=(0,20), pady=5, sticky="w")
        self.n_questions_entry.insert(0, "3")

        # Generic action button (will be "Next" or "Back" depending on mode)
        self.action_button = tk.Button(
            self,
            text="Next",  # default text
            font=("Inter", 14, "bold"),
            bg="#2D2D2D",
            fg="white",
            borderwidth=0,
            highlightthickness=0,
            relief="flat"
        )
        self.action_button.grid(row=8, column=0, columnspan=2, pady=20)

        # --- Extra Back Button (always present when NOT in settings mode) ---
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
        self.back_button.grid(row=9, column=0, sticky="w", padx=20, pady=(0,20))
    
    def tkraise(self, aboveThis=None):
        super().tkraise(aboveThis)
        if self.controller.shared_data.get("in_settings_mode", False):
            # When in settings mode, configure the action button as "Back" and hide the extra back button.
            self.action_button.config(text="Back", command=self.on_back)
            self.back_button.grid_remove()
        else:
            # Otherwise, configure the action button as "Next" and show the extra back button.
            self.action_button.config(text="Next", command=self.on_next)
            self.back_button.grid()  # Ensure it is shown

    def on_next(self):
        """
        When the user clicks 'Next':
          - Save control file changes.
          - Set flags indicating that the control page was visited.
          - Move to the ParametersPage.
        """
        self.update_control_file()
        self.controller.shared_data["has_visited_controller"] = True
        self.controller.shared_data["in_settings_mode"] = False
        self.controller.show_frame("ParametersPage")

    def on_back(self):
        """
        When in settings mode, clicking 'Back' saves changes and returns to the IntroPage.
        """
        self.update_control_file()
        self.controller.shared_data["in_settings_mode"] = False
        self.controller.show_frame("IntroPage")

    def go_back(self):
        """
        The extra back button returns to the IntroPage.
        """
        self.controller.show_frame("IntroPage")

    def update_control_file(self):
        """
        Overwrites backend/txt2h5p/control.txt with user-specified fields plus defaults.
        """
        name_h5p = self.name_h5p_entry.get().strip()
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        introduction = self.intro_entry.get().strip()
        pass_percentage = self.pass_percentage_entry.get().strip() or "50"
        pool_size = self.pool_size_entry.get().strip() or "3"
        n_questions = self.n_questions_entry.get().strip() or "3"

        # Hardcoded defaults for the remaining fields.
        LICENSE = "ODC PDDL"
        DISABLE_BACKWARDS_NAVIGATION = "false"
        RANDOM_QUESTIONS = "true"

        control_lines = [
            f"NAME_H5P: {name_h5p}",
            f'TITLE: "{title}"',
            f'AUTHOR: "{author}"',
            f'LICENSE: "{LICENSE}"',
            f'INTRODUCTION: "{introduction}"',
            f"PASS_PERCENTAGE: {pass_percentage}",
            f"DISABLE_BACKWARDS_NAVIGATION: {DISABLE_BACKWARDS_NAVIGATION}",
            f"RANDOM_QUESTIONS: {RANDOM_QUESTIONS}",
            f"POOL_SIZE: {pool_size}",
            f"N_QUESTIONS: {n_questions}",
        ]

        control_txt_path = Path("./backend/txt2h5p/control.txt")
        try:
            with control_txt_path.open("w", encoding="utf-8") as f:
                for line in control_lines:
                    f.write(line + "\n")
            util.logger.info("Updated control.txt with new H5P settings.")
        except Exception as e:
            util.logger.error(f"Failed to update control.txt: {e}")
