import tkinter as tk
from datetime import datetime

from config import (
    COLORS,
    FONT_FAMILY,
    FONT_SIZES,
    USER_INFO_TITLE,
    USER_INFO_DOB_LABEL,
    USER_INFO_GENDER_LABEL,
    USER_INFO_SUBMIT,
    USER_INFO_ERROR,
    USER_INFO_DOB_PLACEHOLDER,
    USER_INFO_DOB_FORMAT,
    USER_INFO_GENDERS,
)


class UserInfoDialog:
    def __init__(self, root):
        self.root = root
        self.result = None

        root.title(USER_INFO_TITLE)
        root.configure(bg=COLORS["BG"])
        root.resizable(False, False)

        frame = tk.Frame(root, bg=COLORS["BG"], padx=32, pady=24)
        frame.pack()

        label_font = (FONT_FAMILY, FONT_SIZES["mono_sm"])
        entry_font = (FONT_FAMILY, FONT_SIZES["mono"])

        tk.Label(frame, text=USER_INFO_DOB_LABEL,
                 bg=COLORS["BG"], fg=COLORS["MUTED"], font=label_font
                 ).grid(row=0, column=0, sticky="w", pady=(0, 4))

        self.dob_var = tk.StringVar(value=USER_INFO_DOB_PLACEHOLDER)
        tk.Entry(frame, textvariable=self.dob_var,
                 bg=COLORS["PANEL"], fg=COLORS["TEXT"],
                 insertbackground=COLORS["TEXT"], relief="flat",
                 font=entry_font, width=20
                 ).grid(row=1, column=0, sticky="ew", pady=(0, 16), ipady=6)

        tk.Label(frame, text=USER_INFO_GENDER_LABEL,
                 bg=COLORS["BG"], fg=COLORS["MUTED"], font=label_font
                 ).grid(row=2, column=0, sticky="w", pady=(0, 4))

        self.gender_var = tk.StringVar(value=USER_INFO_GENDERS[0])
        gender_row = tk.Frame(frame, bg=COLORS["BG"])
        gender_row.grid(row=3, column=0, sticky="w", pady=(0, 16))
        for value in USER_INFO_GENDERS:
            tk.Radiobutton(
                gender_row, text=value, value=value, variable=self.gender_var,
                bg=COLORS["BG"], fg=COLORS["TEXT"],
                selectcolor=COLORS["PANEL"], activebackground=COLORS["BG"],
                activeforeground=COLORS["TEXT"], font=label_font,
            ).pack(side="left", padx=(0, 12))

        self.error_label = tk.Label(frame, text="", bg=COLORS["BG"],
                                    fg=COLORS["ACCENT"], font=label_font)
        self.error_label.grid(row=4, column=0, sticky="w", pady=(0, 8))

        tk.Button(frame, text=USER_INFO_SUBMIT,
                  bg=COLORS["ACCENT"], fg="white", activebackground="#c1121f",
                  activeforeground="white", font=entry_font, bd=0,
                  padx=24, pady=10, cursor="hand2", relief="flat",
                  command=self._submit
                  ).grid(row=5, column=0, sticky="ew")

        root.bind("<Return>", lambda e: self._submit())
        root.protocol("WM_DELETE_WINDOW", self._cancel)

    def _submit(self):
        dob_text = self.dob_var.get().strip()
        try:
            dob = datetime.strptime(dob_text, USER_INFO_DOB_FORMAT).date()
        except ValueError:
            self.error_label.config(text=USER_INFO_ERROR)
            return
        self.result = {"dob": dob.isoformat(), "gender": self.gender_var.get()}
        self.root.destroy()

    def _cancel(self):
        self.result = None
        self.root.destroy()


def ask_user_info():
    root = tk.Tk()
    dialog = UserInfoDialog(root)
    root.eval("tk::PlaceWindow . center")
    root.mainloop()
    return dialog.result
