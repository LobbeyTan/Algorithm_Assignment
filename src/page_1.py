import sys
import tkinter as tk
from tkinter import messagebox
from browser import WebBrowser
from constant import *


class Page1(tk.Frame):
    isInitialized = False

    def __init__(self, parent, customers, couriers, controller, name):
        tk.Frame.__init__(self, parent, bg=lightBlue)
        print(f"{name} Frame initialized")

        self.webBrowser = WebBrowser
        self.customers = customers
        self.couriers = couriers
        self.controller = controller
        self.name = name

        self.showMap()
        self.showDistance()

    def loadURL(self, cusID):
        self.webBrowser.loadUrl(f'file:///html/customer{cusID}.html')

    def showMap(self):
        browserFrame = tk.Frame(self, bg='blue', width=810, height=500)
        browserFrame.grid(row=0, column=0, columnspan=2)

        initialUrl = 'file:///html/customer1.html'
        browserSetting = {}
        self.webBrowser = WebBrowser(browserFrame, browserSetting, initialUrl, "Customer Route Path")
        self.webBrowser.start()

        frame1 = tk.Frame(self)
        frame1.grid(row=1, column=0, sticky="w")

        tk.Button(frame1, text='Customer 1', command=lambda: self.loadURL(1),
                  width=15, **buttonConfig1).grid(row=0, column=0)
        tk.Button(frame1, text='Customer 2', command=lambda: self.loadURL(2),
                  width=15, **buttonConfig1).grid(row=0, column=1)
        tk.Button(frame1, text='Customer 3', command=lambda: self.loadURL(3),
                  width=15, **buttonConfig1).grid(row=0, column=2)

        infoIcon = getIconImage("info", size=(18, 18))
        infoButton = tk.Button(frame1, image=infoIcon, text=" INFO", compound="left", width=70, **buttonConfig1)
        infoButton.image = infoIcon
        infoButton.config(command=lambda: messagebox.showinfo(
            'Path Color', "Black: Route without hub\nBlue : Route pass through hub\nRed  : Shortest route with hub"))

        infoButton.grid(row=0, column=3)

        frame2 = tk.Frame(self)
        frame2.grid(row=1, column=1, sticky='e')

        exitIcon = getIconImage("exit")
        exitButton = tk.Button(frame2, image=exitIcon, command=lambda: sys.exit(0), text="EXIT ", compound="right")
        exitButton.image = exitIcon
        exitButton.config(width=70, **buttonConfig1)
        exitButton.grid(row=0, column=0)

    def showDistance(self):
        frame = tk.Frame(self, bg=lightBlue)
        frame.grid(row=2, column=0, sticky="w", columnspan=2)

        for i, customer in enumerate(self.customers):
            displayDistance = DisplayDistance(frame, customer, i)
            displayDistance.createInstance()


class DisplayDistance:
    def __init__(self, frame, customer, row):
        self.frame = frame
        self.customer = customer
        self.row = row
        self.distances = {courier.name: distance for courier, distance in customer.distanceWithHub.items()}
        self.dropDownMenu = None
        self.hub = None
        self.distLabel = None

    def createInstance(self):
        desc = tk.Label(self.frame, font=subFontN, background=lightBlue)
        desc['text'] = f'Distance of customer {self.customer.ID}\'s parcel from {self.customer.origin} ' \
                       f'to {self.customer.destination} through '
        desc.grid(row=self.row, column=0, sticky="w")

        choices = list(self.distances.keys())
        choices.insert(0, "None")

        self.hub = tk.StringVar(self.frame, self.customer.minDistanceHub)

        self.dropDownMenu = tk.OptionMenu(self.frame, self.hub, *choices)
        self.dropDownMenu.config(width=15, font=subFontN, **dropDownConfig)
        self.dropDownMenu.grid(row=self.row, column=1)

        tk.Label(self.frame, text=f" = ", font=subFontN, background=lightBlue).grid(row=self.row, column=2)

        self.distLabel = tk.Label(self.frame, font=subFontB, background=lightBlue, width=10)
        self.distLabel.grid(row=self.row, column=3)
        self.__setDistance(self.customer.minimumDistance)

        tk.Label(self.frame, text=f"km", font=subFontN, background=lightBlue).grid(row=self.row, column=4)

        self.hub.trace("w", self.__changeDistance)

    # noinspection PyUnusedLocal
    def __changeDistance(self, *args):
        try:
            update = self.distances[self.hub.get()]

            self.__setDistance(update)
        except KeyError:
            self.__setDistance(self.customer.distance)

    def __setDistance(self, distance):
        self.distLabel.config(foreground='red' if distance == self.customer.minimumDistance else 'blue',
                              text=f" {distance}")
