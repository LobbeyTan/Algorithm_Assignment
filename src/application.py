import tkinter as tk
from constant import *

class Application(tk.Tk):
    def __init__(self, frames, customers, couriers, *args, **kwargs):
        tk.Tk.__init__(self, *args, *kwargs)

        self.frames = frames
        self.customers = customers
        self.couriers = couriers

        self.currentFrame = None

        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)

        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        topBar = tk.Frame(self.container, height=30)
        topBar.grid(row=0, column=0, sticky="n")

        page1Button = tk.Button(topBar, text="Problem 1", width=24, command=lambda: self.show_frame("page_1"))
        page1Button.config(**buttonConfig1)
        page1Button.grid(row=0, column=0)

        page2Button = tk.Button(topBar, text="Problem 2", width=24, command=lambda: self.show_frame("page_2"))
        page2Button.config(**buttonConfig1)
        page2Button.grid(row=0, column=1)

        page3Button = tk.Button(topBar, text="Problem 3", width=24, command=lambda: self.show_frame("page_3"))
        page3Button.config(**buttonConfig1)
        page3Button.grid(row=0, column=2)

        page4Button = tk.Button(topBar, text="Problem 4", width=24, command=lambda: self.show_frame("page_4"))
        page4Button.config(**buttonConfig1)
        page4Button.grid(row=0, column=3)

        self.init()

    def init(self):
        pageName = "page_1"
        self.show_frame(pageName)

    def show_frame(self, pageName):
        self.currentFrame = self.frames[pageName]
        if not self.currentFrame.isInitialized:
            self.currentFrame.isInitialized = True
            self.currentFrame = self.currentFrame(self.container, self.customers, self.couriers, self, pageName)
            self.frames[pageName] = self.currentFrame

        self.currentFrame.grid(row=1, column=0, sticky="nsew")
        self.currentFrame.tkraise()
