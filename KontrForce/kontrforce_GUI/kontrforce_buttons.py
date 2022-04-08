from tkinter import Button
from tkinter import NORMAL, DISABLED

class ctrl_button(Button):
    def __init__(self, btn_parent, btn_text, btn_command, btn_row):
        super().__init__()
        self.new_btn = Button (btn_parent, text=btn_text, command=btn_command)
        self.new_btn.grid(pady=5, padx=5, sticky='w, e', column=0, row=btn_row)
    

    def get_disabled(self):
        self.new_btn.config(state=DISABLED)

    def get_enabled(self):
        self.new_btn.config(state=NORMAL)