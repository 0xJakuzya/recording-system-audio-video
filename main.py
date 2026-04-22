import tkinter as tk
from recorder import RecorderApp

def main():
    root = tk.Tk()
    app = RecorderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
