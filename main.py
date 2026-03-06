import tkinter as tk
from utils import load_json
from gui_engine import AssessmentApp

CONFIG_FILE = "config.json"


def main():

    config = load_json(CONFIG_FILE)

    root = tk.Tk()

    app = AssessmentApp(root, config)

    root.mainloop()


if __name__ == "__main__":
    main()
