import concurrent.futures
import re
import nltk
import string
import plotly.express as px
import random
from newspaper import Article, ArticleException
from nltk.corpus import stopwords
from src.utils.request_with_cache import get
from src.solution.algorithm import KMPSearch, match
from src.constant import courierDict, sentiment

APIKey = "AIzaSyBchEciYYbd2nMgbGseIZGjtWZvj3e0riM"

baseURL = "https://customsearch.googleapis.com/customsearch/v1"

searchEngineID = "1d322aba9f2149b89"


class SentimentAnalysis:
    def __init__(self, url="https://www.google.com/"):
        self.article = self.__getArticle(url)

        self.name = self.article.title

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

    def __getArticle(self, url):
        # Get the article
        article = Article(url)
        try:
            article.download()

            # Parse the article
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

        # Make empty graph if the article cannot be analyzed or no wordList
        if len(word) == 0:
            word = None
        if len(freq) == 0:
            freq = None

        # Plot histogram of word frequency
        fig = px.bar(x=word, y=freq, labels=dict(x="Word", y="Frequency"),
                     title=f"Word Frequency in ({self.name}) Page")
        fig.write_html(f"{sentiment}/figures/wordFreq_graph.html")

    # Plot the sentiment analysis graph based on type of model
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

        # Convert the type of word analysis into sorted frequency dictionary
        freqDict = self.__wordListToFreqDict(output)
        sortedDict = self.__sortFreqDict(freqDict)

        x = list(sortedDict.keys())
        y = list(sortedDict.values())

        if len(x) == 0:
            x = None
        if len(y) == 0:
            y = None

        # Plot the bar chart
        fig = px.bar(x=x, y=y, labels=dict(x="Word", y="Frequency"),
                     title=f"{model.capitalize()} Word Frequency in ({self.name}) Page")

        # Export the bar chart into html file
        fig.write_html(f"{sentiment}/figures/{model}_graph.html")

    # Analyze the sentiment
    def analyzeSentiment(self):
        # Open negative word list file
        with open(f"{sentiment}/negative.txt", mode='r', encoding='utf-8') as negFile:
            neg = negFile.read().lower()
            nltk_neg = [x.strip() for x in neg.split(',')]

        # Open positive word list file
        with open(f"{sentiment}/positive.txt") as posFile:
            pos = posFile.read().lower()
            nltk_pos = [x.strip() for x in pos.split(',')]

        # Identify and seperate the wordList into categories [positive, negative, neutral]
        for word in self.wordList:
            if self.__inList(nltk_neg, word):
                self.neg_output.append(word)
            elif self.__inList(nltk_pos, word):
                self.pos_output.append(word)
            else:
                self.neu_output.append(word)

        if len(self.wordList) == 0:
            return

        # Calculate the positivity and negativity
        self.negativity = len(self.neg_output) / len(self.wordList)
        self.positivity = len(self.pos_output) / len(self.wordList)

        # Identify the related courier of the article
        self.relatedCourier = self.__getRelatedCourier()[0]
        courier = courierDict[self.relatedCourier]

        # Make conclusion on the analysis
        if self.positivity > self.negativity:
            self.sentimentDescription = f"This article related to {courier} is giving more postive sentiments "
        elif self.negativity > self.positivity:
            self.sentimentDescription = f"This article related to {courier} is giving more negative sentiments"
        else:
            self.sentimentDescription = f"This article related to {courier} is giving neutral sentiments"

    def __inList(self, nltkList, key):
        # Using Z algorithm to identify matched word
        for word in nltkList:
            if match(key, word) == 0 and len(key) == len(word):
                return True
        return False

    # Obtain the courier which the article refer to
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

    def __getstate__(self):
        attributes = self.__dict__
        attributes.pop("article")

        return attributes


# A driver class use to call and analyze sentiment
class SentimentAnalysisTool:
    def __init__(self, couriers: object = []) -> object:
        self.history = {}
        self.couriers = couriers

    # Get the sentiment of a article with the url as a parameter
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

    # Get the list of analyzed urls
    def getUrls(self):
        return list(self.history.keys())

    # Check whether an url has been analyzed
    def hasAnalyzed(self, url):
        return url in self.history

    # Randomly analyzed the sentiment of random articles
    def randomSentiment(self, q, n=5):
        exactTerms, query = q
        items = []

        # Retrieve 40 articles through Google Custom Search API
        for i in range(1, 40, 10):
            # Parameters to be included
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

        # Randomly get n links from the result obtained
        urls = [item['link'] for item in random.sample(items, n)]

        # Use multiprocessor to speed up analysis
        with concurrent.futures.ProcessPoolExecutor(max_workers=n) as executor:
            results = executor.map(randomSentiment, urls)

        for url, result in results:
            self.history[url] = result

            relatedCourier = result.relatedCourier
            if relatedCourier != -1:
                self.couriers[relatedCourier].appendSentiment(result)


def randomSentiment(url):
    print(url)
    return url, SentimentAnalysis(url)


# Download nltk resources
def downloadResources():
    nltk.download('punkt')
    nltk.download('stopwords')
