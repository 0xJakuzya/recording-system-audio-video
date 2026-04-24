import tkinter as tk

from src import RecorderApp
from src.ui.user_info import ask_user_info


def main():
    user_info = ask_user_info()
    if user_info is None:
        return
    root = tk.Tk()
    RecorderApp(root, user_info=user_info)
    root.mainloop()

if __name__ == "__main__":
    main()
