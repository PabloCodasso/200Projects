import os
import sys
sys.path.append(os.path.abspath(__file__).replace("\kontrforce_GUI\main_window.py", ""))

from tkinter import Label, Tk, Frame
from tkinter.ttk import Progressbar
from multiprocessing import Pipe

from kontrforce_Utils import proceesing, tests, btns_upd, get_folder, thr_pooling
from kontrforce_buttons import ctrl_button


class mainWindow:
    def __init__(self):
        self.prnt_con, self.chld_con = Pipe()
        self.working_dir = None
        self.executor = thr_pooling.Pooler()
    
        self.root_window = Tk()
        self.root_window.title("KontrForse v1.0 by Voevoda")
        self.root_window.geometry('600x400')
        self.root_window.resizable(False, False)
        self.root_window.columnconfigure(0, weight=10)
        self.root_window.columnconfigure(1, weight=1)
        self.root_window.rowconfigure(0, weight=1)
        
        self.button_frame = Frame(self.root_window, bg='grey')
        self.button_frame.grid(column=1, row=0, padx=10, pady=10, sticky='n, e, w')
        self.button_frame.columnconfigure(0, weight=1)

        self.info_frame = Frame(self.root_window, bg='grey')
        self.info_frame.grid(column=0, row=0, padx=10, pady=10, sticky='n, e, s, w')
        self.info_frame.columnconfigure(2, weight=1)


        self.exit_button = ctrl_button(self.button_frame, 'EXIT',
                                       lambda: exit(0), 4)

        self.ans_button = ctrl_button(self.button_frame, 'ANALYSE',
                                        self.analysing, 2)

        self.set_dir_button = ctrl_button(self.button_frame, 'SET DIR',
                                          self.directory_getting,1)

        self.refactor_button = ctrl_button(self.button_frame, 'REFACTOR', 
                                           self.refactoring, 3)

        self.folder_info = Label(master=self.info_frame, text='Working DIR:', bg='grey')
        self.folder_info.grid(column=0, row=0, padx=5, pady=5)

        self.folder_label = Label(master=self.info_frame, text=self.working_dir, width=20, height=1)
        self.folder_label.grid(column=1, row=0, padx=5, pady=5)

        self.prgs = Progressbar(self.info_frame, orient='horizontal', mode='indeterminate', length=70)
        self.prgs.grid(column=2, row=0, padx=5, pady=5, sticky='e')
        
    def analysing(self):
        self.chld_con.send(False)
        self.executor.pooling(btns_upd.btn_upd, 
                                [self.prgs, self.prnt_con, 
                                [self.ans_button, self.set_dir_button, self.refactor_button]])
        proceesing.processStart(tests.testPrcs, (self.chld_con,), 'Analyser process')
    
    def directory_getting(self):
        self.working_dir = get_folder.folder_asking(self.root_window)
        self.folder_label.config(text=self.working_dir)
    
    def refactoring(self):
        print('Its nothing yet...')
        pass

if __name__ == '__main__':
    main_root = mainWindow()
    main_root.root_window.mainloop()
