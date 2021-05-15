import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
import random
from PIL import Image, ImageTk
from entity import *
from ranking import CourierRecommendation
from constant import *


class Page3(tk.Frame):
    isInitialized = False

    def __init__(self, parent, customers, couriers, controller, name):
        tk.Frame.__init__(self, parent, bg=lightBlue)
        print(f"{name} Frame initialized")

        self.customers = customers
        self.couriers = couriers
        self.controller = controller
        self.name = name

        self.customerCards = []
        self.sentimentCards = []
        self.sentimentData = {}

        sentimentFrame = tk.Frame(self, bg=lightBlue)
        sentimentFrame.grid(row=0, column=0)

        customerFrame = tk.Frame(self, bg=lightBlue)
        customerFrame.grid(row=0, column=1, sticky="ew")

        for i, courier in enumerate(couriers):
            sen = SentimentCard(sentimentFrame, courier=courier, row=i, column=0, bg=black,
                                borderwidth=1, relief="solid")
            self.sentimentData[courier.name] = sen.getResult()
            self.sentimentCards.append(sen)

        for i, customer in enumerate(customers):
            cus = CustomerCard(customerFrame, customer=customer, row=i, column=1, bg=blue,
                               borderwidth=2, relief="groove")
            self.customerCards.append(cus)

        icon = getIconImage("refresh")
        refresh = tk.Button(self, text=" Refresh", image=icon, compound="left", command=self.refresh, **buttonConfig3)
        refresh.image = icon
        refresh.place(x=717, y=15)

        icon = getIconImage("bar")
        bar = tk.Button(self, text=" Bar Chart", image=icon, compound="left", command=self.barChart, **buttonConfig3)
        bar.image = icon
        bar.place(x=625, y=15)

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
        self.frame.grid(row=row, column=column, padx=10, pady=0 if row == 1 else 5, sticky="ew")
        self.customer = customer

        recommender = CourierRecommendation(customer)
        recommender.analyzeRanking()
        self.ranking = recommender.ranking

        tk.Label(self.frame, text=f"Customer {self.customer.ID}",
                 background=blue, font=subFontB).grid(row=0, column=0, columnspan=3)

        self.showContent()
        self.showRanking()
        self.showRecommended()

    def showContent(self):
        content = tk.Frame(self.frame, bg=blue)
        content.grid(row=1, column=0, padx=5)
        tk.Label(content, background=blue, font=textFontN,
                 text=f"Origin            : {self.customer.origin}").grid(row=1, column=0, sticky="w", columnspan=3)
        tk.Label(content, background=blue, font=textFontN,
                 text=f"Destination   : {self.customer.destination}").grid(row=2, column=0, sticky="w", columnspan=3)

        tk.Label(content, text=f"Distance Through",
                 background=blue, font=textFontU).grid(row=3, column=0, sticky="w", columnspan=3)

        sortedDist = {k: v for k, v in sorted(self.customer.distanceWithHub.items(), key=lambda item: item[1])}

        for i, data in enumerate(sortedDist.items()):
            courier, distance = data
            tk.Label(content, text=f"Hub {i + 1} : {courier.name} ",
                     background=blue, font=textFontN).grid(row=4 + i, column=0, sticky='w')
            tk.Label(content, text=f"at {courier.location} ",
                     background=blue, font=textFontN).grid(row=4 + i, column=1, sticky='w')
            tk.Label(content, text="= {:>10.3f} km".format(distance),
                     background=blue, font=textFontB).grid(row=4 + i, column=2, sticky='w')

    def showRanking(self):
        ranking = tk.Frame(self.frame, bg=blue)
        ranking.grid(row=1, column=1, sticky="s", padx="20")

        tk.Label(ranking, text="Courier Ranking", font=textFontU, background=blue).grid(row=0, column=0, columnspan=2)

        for i, data in enumerate(self.ranking.items()):
            courier, score = data
            tk.Label(ranking, text=f"{courier.name} ", anchor="w",
                     font=textFontN, background=blue).grid(row=1 + i, column=0, sticky="nsew")
            tk.Label(ranking, text=": {:-6.3f}".format(score), anchor="e",
                     font=textFontB, background=blue).grid(row=1 + i, column=1, sticky="nsew")

    def showRecommended(self):
        recommendation = tk.Frame(self.frame, bg=blue)
        recommendation.grid(row=1, column=2, padx=10, sticky="ew")

        courier, score = list(self.ranking.items())[0]

        load = Image.open(f"logo/{courier.name}.png")
        load = load.resize((120, 120), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(load)

        logo = tk.Label(recommendation, image=img, background=blue, borderwidth=2, relief="ridge")
        logo.image = img
        logo.grid(row=0, column=0, columnspan=2, sticky="nsew")

        tk.Label(recommendation, text="RECOMMENDED", font=textFontB, background=blue).grid(row=1, column=0, sticky="s")

        like = getIconImage("like")

        icon = tk.Label(recommendation, image=like, background=blue)
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

        logo = tk.Label(self.frame, image=img, background=lightPurple)
        logo.image = img
        logo.grid(row=0, column=0, columnspan=2, sticky="nsew")

        for result in self.courier.sentimentResults:
            self.positivity += result.positivity
            self.negativity += result.negativity

        tk.Label(self.frame, text="Positivity   : ", background=purple).grid(row=1, column=0)
        tk.Label(self.frame, text="{:4.3f}".format(self.positivity), width=4, background=purple).grid(row=1, column=1)
        tk.Label(self.frame, text="Negativity : ", background=purple).grid(row=2, column=0)
        tk.Label(self.frame, text="{:4.3f}".format(self.negativity), width=4, background=purple).grid(row=2, column=1)
        tk.Label(self.frame, text=f"{len(self.courier.sentimentResults)}",
                 width=3, anchor="center", font=buttonFontB, background=lightPurple).place(x=72, y=3)

    def getResult(self):
        return [self.positivity, self.negativity]
