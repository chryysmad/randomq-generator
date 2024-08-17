import subprocess

gui_files = ["build/intro.py", "build/parameters.py", "build/correct.py", "build/wrongs.py", "build/randomizer.py"]

def launch_gui(file):
    subprocess.Popen(["python3", file])

for gui in gui_files:
    launch_gui(gui)
