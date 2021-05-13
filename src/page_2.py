from tkinter.scrolledtext import ScrolledText
from sentiment import SentimentAnalysisTool, SentimentAnalysis
from browser import WebBrowser
from constant import getIconImage
from threading import Thread
import tkinter as tk


class Page2(tk.Frame):
    isInitialized = False

    def __init__(self, parent, customers, couriers, controller, name):
        tk.Frame.__init__(self, parent)
        print(f"{name} Frame initialized")

        self.webBrowser = WebBrowser
        self.customers = customers
        self.couriers = couriers
        self.controller = controller
        self.name = name

        self.wordFreqDisplay = ScrolledText
        self.status = tk.Label
        self.sentimentDescription = tk.Label
        self.hasAnalyzed = False
        self.scrapingText = tk.StringVar(self, " Random Scraping")

        self.tool = SentimentAnalysisTool(self.couriers)

        self.currentResult = SentimentAnalysis()
        self.T1 = Thread
        self.T2 = Thread

        self.showArticle()
        self.showStatistic()

    def showArticle(self):
        browserFrame = tk.Frame(self, bg='blue', width=800, height=500)
        browserFrame.grid(row=0, column=0)

        initialUrl = "https://www.google.com/"
        browserSetting = {}
        self.webBrowser = WebBrowser(browserFrame, browserSetting, initialUrl, "Search For Article")
        self.webBrowser.start()

        frame = tk.Frame(self, bg='white', width=800, height=200)
        frame.grid(row=1, column=0, sticky="w", columnspan=10)

        linkSelected = tk.StringVar(frame, "https://www.google.com/")
        dropDownMenu = tk.OptionMenu(frame, linkSelected, *(self.__getSampleLinks()))
        dropDownMenu.config(width=80, anchor="w")
        dropDownMenu.grid(row=1, column=0, sticky="w")
        linkSelected.trace(mode="w", callback=lambda *args: self.__search(linkSelected.get()))

        tk.Button(frame, text="Analyze Page", command=self.__startSentiment).grid(row=1, column=1)
        tk.Label(frame, text=" STATUS: ").grid(row=1, column=2)

        self.status = tk.Label(frame, text="Not yet analyze", width=17)
        self.status.grid(row=1, column=3)

    def showStatistic(self):
        frame = tk.Frame(self, bg='white')
        frame.grid(row=2, column=0, sticky="w")

        self.wordFreqDisplay = ScrolledText(frame, width=30, height=4, wrap=tk.WORD)
        self.wordFreqDisplay.grid(row=0, column=0, pady=10, padx=10, rowspan=2)
        self.wordFreqDisplay.insert(tk.INSERT, "No Word Frequency Found")

        wordFreqButton = tk.Button(frame, text="Word Frequency", command=lambda: self.__showGraph(0))
        wordFreqButton.config(width=16)
        wordFreqButton.grid(row=0, column=1)

        positveButton = tk.Button(frame, text="Positive Sentiment", command=lambda: self.__showGraph(1))
        positveButton.config(width=16)
        positveButton.grid(row=0, column=2)

        negativeButton = tk.Button(frame, text="Negative Sentiment", command=lambda: self.__showGraph(2))
        negativeButton.config(width=16)
        negativeButton.grid(row=0, column=3)

        neutralButton = tk.Button(frame, text="Neutral Sentiment", command=lambda: self.__showGraph(3))
        neutralButton.config(width=16)
        neutralButton.grid(row=0, column=4)

        self.sentimentDescription = tk.Label(frame, text="No sentiment analysis yet", width=70)
        self.sentimentDescription.config(anchor="w", padx=10, foreground="red", pady=10)
        self.sentimentDescription.grid(row=1, column=1, sticky="se", columnspan=4)

        mining = getIconImage("mining")

        scraping = tk.Button(frame, textvariable=self.scrapingText,
                             image=mining, compound="left", width=130, command=self.__randomScraping)
        scraping.image = mining
        scraping.place(x=653, y=55)

    def __randomScraping(self):
        if self.scrapingText == " Analyzing":
            return

        thread = Thread(target=self.__randomAnalysis)
        thread.isDaemon = True
        thread.start()

    def __randomAnalysis(self):
        self.scrapingText.set(" Analyzing")
        # self.tool.randomScraping()
        queries = [
            ("city-link", "city-link express news"),
            ("pos laju", "pos laju news"),
            ("gdex", "gdex express news"),
            ("j&t", "j&t express news"),
            ("dhl", "dhl express news"),
        ]

        for q in queries:
            self.tool.analyzeSentiment(q)

        self.scrapingText.set(" Random Scraping")

    def __startSentiment(self):
        status = self.status['text']
        if status == "Showing Graph" or status == "Analyzing Page":
            return
        elif status == "Has been analyzed":
            self.currentResult = self.tool.history[self.webBrowser.getUrl()]
            self.__update()
        else:
            self.T1 = Thread(target=self.__getStatus)
            self.T2 = Thread(target=self.__getSentiment)

            self.T1.start()
            self.T2.start()

    def __getStatus(self):
        self.status.config(text="Analyzing Page")
        self.T2.join()
        self.status.config(text="Finished Analyzed")
        self.__update()

    def __update(self):
        self.wordFreqDisplay.delete("1.0", "end")
        self.wordFreqDisplay.insert(tk.INSERT, self.__printFreq())
        self.sentimentDescription['text'] = self.currentResult.sentimentDescription

    def __getSentiment(self):
        url = self.webBrowser.getUrl()
        self.currentResult = self.tool.getSentiment(url)

    def __getSampleLinks(self):
        with open("sentiment/link.txt", mode="r") as file:
            links = [link.strip() for link in file.readlines()]
        return links

    def __search(self, url):
        if url in self.tool.getUrls():
            self.status.config(text="Has been analyzed")
        elif url[:4] == "file":
            self.status.config(text="Showing Graph")
        else:
            self.status.config(text="Not yet analyze")
        self.webBrowser.loadUrl(url)

    def __printFreq(self):
        result = self.currentResult.sortedDict
        output = ""
        if result:
            for word, freq in result.items():
                output += f"{word}, {freq}\n"
        else:
            output = "No Word Frequency Found"
        return output

    def __showGraph(self, mode=0):
        if self.sentimentDescription['text'] == "Current Page could not be analyzed":
            return None

        # 0 = wordFreq, 1 = positive, 2 = negative, 3 = neutral
        if mode == 0:
            fname = "wordFreq"
            self.currentResult.plotWordFrequency()
        elif mode == 1:
            fname = "positive"
            self.currentResult.plotSentimentGraph(model="positive")
        elif mode == 2:
            fname = "negative"
            self.currentResult.plotSentimentGraph(model="negative")
        elif mode == 3:
            fname = "neutral"
            self.currentResult.plotSentimentGraph(model="neutral")
        else:
            print("Invalid mode")
            return None

        self.__search(url=f"file:///sentiment/figures/{fname}_graph.html")
