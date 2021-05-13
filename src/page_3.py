import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
import random
from PIL import Image, ImageTk
from entity import *
from ranking import CourierRecommendation
from constant import getIconImage


class Page3(tk.Frame):
    isInitialized = False

    def __init__(self, parent, customers, couriers, controller, name):
        tk.Frame.__init__(self, parent)
        print(f"{name} Frame initialized")

        self.customers = customers
        self.couriers = couriers
        self.controller = controller
        self.name = name

        self.customerCards = []
        self.sentimentCards = []
        self.sentimentData = {}

        sentimentFrame = tk.Frame(self)
        sentimentFrame.grid(row=0, column=0)

        customerFrame = tk.Frame(self, bg="yellow")
        customerFrame.grid(row=0, column=1)

        for i, courier in enumerate(couriers):
            sen = SentimentCard(sentimentFrame, courier=courier, row=i, column=0, borderwidth=1, background="black")
            self.sentimentData[courier.name] = sen.getResult()
            self.sentimentCards.append(sen)

        for i, customer in enumerate(customers):
            cus = CustomerCard(customerFrame, customer=customer, row=i, column=1)
            self.customerCards.append(cus)

        icon = getIconImage("refresh")
        refresh = tk.Button(self, text=" Refresh", image=icon, compound="left", command=self.refresh)
        refresh.image = icon
        refresh.place(x=710, y=10)

        icon = getIconImage("bar")
        bar = tk.Button(self, text=" Bar Chart", image=icon, compound="left", command=self.barChart)
        bar.image = icon
        bar.place(x=625, y=10)

    def refresh(self):
        self.destroy()
        Page3.isInitialized = False
        self.controller.frames["page_3"] = Page3
        self.controller.show_frame("page_3")

    def barChart(self):
        labels = list(self.sentimentData.keys())
        
        positivity = [value[0] for value in self.sentimentData.values()]
        negativity = [value[1] for value in self.sentimentData.values()]
        width = 0.35

        fig, ax = plt.subplots()

        ax.bar(labels, positivity, width, label="Positivity")
        ax.bar(labels, negativity, width, bottom=positivity, label="Negativity")

        ax.set_ylabel("Results")
        ax.set_xlabel("Couriers")
        ax.set_title("Sentiment Results by Couriers")
        ax.legend()

        plt.show()


class CustomerCard:
    def __init__(self, master, customer, row=0, column=0, cnf={}, **kw):
        self.frame = tk.Frame(master, cnf, **kw)
        self.frame.grid(row=row, column=column, padx=18, pady=10, sticky="ew")
        self.customer = customer

        recommender = CourierRecommendation(customer)
        recommender.analyzeRanking()
        self.ranking = recommender.ranking

        tk.Label(self.frame, text=f"Customer {self.customer.ID}").grid(row=0, column=0, columnspan=3)

        self.showContent()
        self.showRanking()
        self.showRecommended()

    def showContent(self):
        content = tk.Frame(self.frame)
        content.grid(row=1, column=0, padx=5)
        tk.Label(content,
                 text=f"Origin            : {self.customer.origin}").grid(row=1, column=0, sticky="w", columnspan=3)
        tk.Label(content,
                 text=f"Destination   : {self.customer.destination}").grid(row=2, column=0, sticky="w", columnspan=3)

        L1 = tk.Label(content, text=f"Distance Through")
        L1.config(font="Verdana 9 underline")
        L1.grid(row=3, column=0, sticky="w", columnspan=3)

        sortedDist = {k: v for k, v in sorted(self.customer.distanceWithHub.items(), key=lambda item: item[1])}

        for i, data in enumerate(sortedDist.items()):
            courier, distance = data
            tk.Label(content, text=f"Hub {i + 1} : {courier.name} ").grid(row=4 + i, column=0, sticky='w')
            tk.Label(content, text=f"at {courier.location} ").grid(row=4 + i, column=1, sticky='w')
            tk.Label(content, text="= {:>10.3f} km".format(distance)).grid(row=4 + i, column=2, sticky='w')

    def showRanking(self):
        ranking = tk.Frame(self.frame)
        ranking.grid(row=1, column=1, sticky="s", padx="20")

        tk.Label(ranking, text="Courier Ranking", font="Verdana 12 underline").grid(row=0, column=0, columnspan=2)

        for i, data in enumerate(self.ranking.items()):
            courier, score = data
            tk.Label(ranking, text=f"{courier.name} ", anchor="w").grid(row=1 + i, column=0, sticky="nsew")
            tk.Label(ranking, text=": {:-6.3f}".format(score), anchor="e").grid(row=1 + i, column=1, sticky="nsew")

    def showRecommended(self):
        recommendation = tk.Frame(self.frame)
        recommendation.grid(row=1, column=2, padx=10, sticky="ew")

        courier, score = list(self.ranking.items())[0]

        load = Image.open(f"logo/{courier.name}.png")
        load = load.resize((120, 120), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(load)

        logo = tk.Label(recommendation, image=img)
        logo.image = img
        logo.grid(row=0, column=0, columnspan=2, sticky="nsew")

        tk.Label(recommendation, text="RECOMMENDED").grid(row=1, column=0, sticky="s")

        like = getIconImage("like")

        icon = tk.Label(recommendation, image=like)
        icon.image = like
        icon.grid(row=1, column=1)


class SentimentCard:
    def __init__(self, master, courier, row=0, column=0, cnf={}, **kw):
        self.frame = tk.Frame(master, cnf, **kw)
        self.frame.grid(row=row, column=column, padx=2.5, pady=1)
        self.courier = courier

        self.positivity = 0.0
        self.negativity = 0.0

        self.showSentiment()

    def showSentiment(self):
        name = self.courier.name
        load = Image.open(f"logo/{name}.png")
        load = load.resize((75, 75), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(load)

        logo = tk.Label(self.frame, image=img)
        logo.image = img
        logo.grid(row=0, column=0, columnspan=2, sticky="nsew")

        for result in self.courier.sentimentResults:
            self.positivity += result.positivity
            self.negativity += result.negativity

        tk.Label(self.frame, text="Positivity   : ").grid(row=1, column=0)
        tk.Label(self.frame, text="{:4.3f}".format(self.positivity), width=4).grid(row=1, column=1)
        tk.Label(self.frame, text="Negativity : ").grid(row=2, column=0)
        tk.Label(self.frame, text="{:4.3f}".format(self.negativity), width=4).grid(row=2, column=1)
        tk.Label(self.frame, text=f"{len(self.courier.sentimentResults)}",
                 width=3, anchor="center", foreground="#004F00").place(x=75, y=5)

    def getResult(self):
        return [self.positivity, self.negativity]
