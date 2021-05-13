import tkinter as tk
from tkinter import messagebox
from browser import WebBrowser


class Page1(tk.Frame):
    isInitialized = False

    def __init__(self, parent, customers, couriers, controller, name):
        tk.Frame.__init__(self, parent)
        print(f"{name} Frame initialized")

        self.webBrowser = WebBrowser
        self.customers = customers
        self.couriers = couriers
        self.controller = controller
        self.name = name

        self.showMap()
        self.showDistance()

    def closeBrowser(self):
        self.webBrowser.close()

    def loadURL(self, cusID):
        self.webBrowser.loadUrl(f'file:///html/customer{cusID}.html')

    def showMap(self):
        browserFrame = tk.Frame(self, bg='blue', width=800, height=500)
        browserFrame.grid(row=0, column=0)

        initialUrl = 'file:///html/customer1.html'
        browserSetting = {}
        self.webBrowser = WebBrowser(browserFrame, browserSetting, initialUrl, "Customer Route Path")
        self.webBrowser.start()

        frame = tk.Frame(self, bg='black', width=800, height=200)
        frame.grid(row=1, column=0, sticky="w", columnspan=10)

        tk.Button(frame, text='Exit', command=self.closeBrowser).grid(row=1, column=0)
        tk.Button(frame, text='Customer 1', command=lambda: self.loadURL(1)).grid(row=1, column=1)
        tk.Button(frame, text='Customer 2', command=lambda: self.loadURL(2)).grid(row=1, column=2)
        tk.Button(frame, text='Customer 3', command=lambda: self.loadURL(3)).grid(row=1, column=3)
        tk.Button(frame, text='Show something',
                  command=lambda: messagebox.showinfo('TITLE', 'Shown something')).grid(row=1, column=10)

    def showDistance(self):
        frame = tk.Frame(self, bg='white', width=800, height=200)
        frame.grid(row=2, column=0, sticky="w")

        for i, customer in enumerate(self.customers):
            displayDistance = DisplayDistance(frame, customer, i + 2)
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
        tk.Label(self.frame,
                 text=f'Distance of CUSTOMER {self.customer.ID}\'s parcel from {self.customer.origin} '
                      f'to {self.customer.destination} through').grid(row=self.row, column=0, sticky="w")

        choices = list(self.distances.keys())
        choices.insert(0, "None")

        self.hub = tk.StringVar(self.frame, self.customer.minDistanceHub)

        self.dropDownMenu = tk.OptionMenu(self.frame, self.hub, *choices)
        self.dropDownMenu.config(width=20)
        self.dropDownMenu.grid(row=self.row, column=1)

        tk.Label(self.frame, text=f" = ").grid(row=self.row, column=2)

        self.distLabel = tk.Label(self.frame)
        self.distLabel.grid(row=self.row, column=3)
        self.__setDistance(self.customer.minimumDistance)

        tk.Label(self.frame, text=f"km").grid(row=self.row, column=4)

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
                              text=f" {distance} ")
