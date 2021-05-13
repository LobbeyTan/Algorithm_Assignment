import concurrent.futures
import re
import nltk
import string
import plotly.express as px
from newspaper import Article, ArticleException
from nltk.corpus import stopwords
from algorithm import KMPSearch, match
from constant import courierDict
from request_with_cache import get
import random

APIKey = "AIzaSyBchEciYYbd2nMgbGseIZGjtWZvj3e0riM"

baseURL = "https://customsearch.googleapis.com/customsearch/v1"

searchEngineID = "1d322aba9f2149b89"


class SentimentAnalysis:
    def __init__(self, url="https://www.google.com/"):
        self.url = url
        self.name = list(filter(None, re.split("/+", self.url)))[-1]

        self.article = self.__getArticle()
        self.wordList = self.__preprocessing()

        dictionary = self.__wordListToFreqDict(self.wordList)
        self.sortedDict = self.__sortFreqDict(dictionary)

        self.neg_output = []
        self.pos_output = []
        self.neu_output = []

        self.negativity = 0
        self.positivity = 0

        self.sentimentDescription = "Current Page could not be analyzed"
        self.relatedCourier = -1

        self.analyzeSentiment()
        print(self.relatedCourier)

    def __getArticle(self):
        article = Article(self.url)
        try:
            article.download()
            article.parse()
        except ArticleException:
            pass
        return article

    def __preprocessing(self):
        # Get content of news article
        str1 = self.article.text

        # Convert to lowercase
        str1 = str1.lower()

        # Remove punctuations
        transtable = str.maketrans('', '', string.punctuation)
        str1 = str1.translate(transtable)

        # Convert string to list of words
        wordList = str1.split()

        # Remove digits
        wordList = [x for x in wordList if not any(c.isdigit() for c in x)]

        # Remove stopwords
        filteredWordList = self.__removeStopwords(wordList, stopwords.words('english'))
        return filteredWordList

    # Remove stopwords in the wordlist
    def __removeStopwords(self, wordList, stopwords):
        for x in stopwords:
            txt = x
            for y in wordList:
                pat = y
                if KMPSearch(pat, txt):  # Filter out stopwords using KMP algorithm
                    if len(pat) == len(txt):  # To make sure the words removed are in the same length
                        wordList.remove(y)
        return wordList

    # Convert list of words to a dictionary of word-frequency pairs
    def __wordListToFreqDict(self, wordList):
        freqDict = {}
        for w in wordList:
            freqDict[w] = freqDict.get(w, 0) + 1

        return freqDict

    # Sort a dictionary of word-frequency pairs in order of descending frequency
    def __sortFreqDict(self, freqDict):
        sortedList = sorted(freqDict.items(), key=lambda item: item[1])
        sortedList.reverse()
        sortedDict = {k: v for k, v in sortedList}
        return sortedDict

    def plotWordFrequency(self):
        # Get values for y-axis (word frequency)
        word = list(self.sortedDict.keys())
        # Get values for x-axis (list of words)
        freq = list(self.sortedDict.values())

        # Plot histogram of word frequency
        fig = px.bar(x=word, y=freq, labels=dict(x="Word", y="Frequency"),
                     title=f"Word Frequency in ({self.name}) Page")
        fig.write_html("sentiment/figures/wordFreq_graph.html")

    def plotSentimentGraph(self, model=""):
        if model == "positive":
            output = self.pos_output
        elif model == "negative":
            output = self.neg_output
        elif model == "neutral":
            output = self.neu_output
        else:
            print(f"{model} is invalid, only positive, negative or neutral")
            return None

        freqDict = self.__wordListToFreqDict(output)
        sortedDict = self.__sortFreqDict(freqDict)

        fig = px.bar(x=list(sortedDict.keys()), y=list(sortedDict.values()),
                     labels=dict(x="Word", y="Frequency"),
                     title=f"{model.capitalize()} Word Frequency in ({self.name}) Page")
        fig.write_html(f"sentiment/figures/{model}_graph.html")

    def analyzeSentiment(self):
        with open("sentiment/negative.txt", mode='r', encoding='utf-8') as negFile:
            neg = negFile.read().lower()
            nltk_neg = [x.strip() for x in neg.split(',')]

        with open("sentiment/positive.txt") as posFile:
            pos = posFile.read().lower()
            nltk_pos = [x.strip() for x in pos.split(',')]

        for word in self.wordList:
            if self.__inList(nltk_neg, word):
                self.neg_output.append(word)
            elif self.__inList(nltk_pos, word):
                self.pos_output.append(word)
            else:
                self.neu_output.append(word)

        if len(self.wordList) == 0:
            return

        self.negativity = len(self.neg_output) / len(self.wordList)
        self.positivity = len(self.pos_output) / len(self.wordList)

        self.relatedCourier = self.__getRelatedCourier()[0]
        courier = courierDict[self.relatedCourier]

        if self.positivity > self.negativity:
            self.sentimentDescription = f"This article related to {courier} is giving more postive sentiments "
        elif self.negativity > self.positivity:
            self.sentimentDescription = f"This article related to {courier} is giving more negative sentiments"
        else:
            self.sentimentDescription = f"This article related to {courier} is giving neutral sentiments"

    def __inList(self, nltkList, key):
        for word in nltkList:
            if match(key, word) == 0 and len(key) == len(word):
                return True
        return False

    def __getRelatedCourier(self):
        relatedCourierScore = {-1: 0}
        for word in self.sortedDict.keys():
            if word in ["citylink", "link", "city"]:
                if word == "citylink":
                    relatedCourierScore[0] = relatedCourierScore.get(0, 0) + self.sortedDict[word] * 2
                else:
                    relatedCourierScore[0] = relatedCourierScore.get(0, 0) + self.sortedDict[word] * 0.5
            elif word in ["pos", "laju"]:
                relatedCourierScore[1] = relatedCourierScore.get(1, 0) + self.sortedDict[word] * 1
            elif word in ["gdex"]:
                relatedCourierScore[2] = relatedCourierScore.get(2, 0) + self.sortedDict[word] * 4
            elif "jt" in word:
                relatedCourierScore[3] = relatedCourierScore.get(3, 0) + self.sortedDict[word] * 4
            elif "dhl" in word:
                relatedCourierScore[4] = relatedCourierScore.get(4, 0) + self.sortedDict[word] * 4

        relatedCourierScore = self.__sortFreqDict(relatedCourierScore)
        return list(relatedCourierScore.keys())


class SentimentAnalysisTool:
    def __init__(self, couriers: object = []) -> object:
        self.history = {}
        self.couriers = couriers

    def getSentiment(self, url) -> SentimentAnalysis:
        if url in self.history:
            return self.history[url]
        else:
            result = SentimentAnalysis(url)
            self.history[url] = result

            relatedCourier = result.relatedCourier
            if relatedCourier != -1:
                self.couriers[relatedCourier].appendSentiment(result)

            return result

    def getUrls(self):
        return list(self.history.keys())

    def hasAnalyzed(self, url):
        return url in self.history

    def randomScraping(self):
        queries = [
            ("city-link", "city-link express news"),
            ("pos laju", "pos laju news"),
            ("gdex", "gdex express news"),
            ("j&t", "j&t express news"),
            ("dhl", "dhl express news"),
        ]
        with concurrent.futures.ProcessPoolExecutor(5) as executor:
            executor.map(self.analyzeSentiment, queries)

    def analyzeSentiment(self, q):
        exactTerms, query = q
        items = []

        for i in range(1, 40, 10):
            params = {
                "c2coff": "1",
                "cx": searchEngineID,
                "exactTerms": exactTerms,
                "filter": "1",
                "num": 10,
                "q": query,
                "siteSearch": "www.youtube.com",
                "siteSearchFilter": "e",
                "key": APIKey,
                "start": i,
            }
            data = get(baseURL, params)
            items += data["items"]

        print(query)
        for item in random.sample(items, 5):
            link = item['link']
            print(link)
            self.getSentiment(link)


def downloadResources():
    nltk.download('punkt')
    nltk.download('stopwords')
