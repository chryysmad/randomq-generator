import tkinter as tk
from pathlib import Path
from build.parameters import ParametersPage
from build.intro import IntroPage

class BaseApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("Random Question Generator")
        self.geometry("994x547")
        self.configure(bg="#F5F5F5")

        # make a container that stores all the pages
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (IntroPage, ParametersPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("IntroPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

if __name__ == "__main__":
    app = BaseApp()
    app.resizable(False, False)
    app.mainloop()
