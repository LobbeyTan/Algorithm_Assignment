from entity import *
from constant import courierDict
from algorithm import timSort


class CourierRecommendation:
    def __init__(self, customer):
        self.customer = customer
        self.ranking = {}

    def analyzeRanking(self):
        self.__preprocessing()
        self.__sorting()

    def __calculateScore(self, distance, sentimentScore):
        score = (0.5 * - distance) + (100 * sentimentScore) + 100
        return score

    def __preprocessing(self):
        for courier, distance in self.customer.distanceWithHub.items():
            n = len(courier.sentimentResults)

            positivity = sum([result.positivity for result in courier.sentimentResults])
            negativity = sum([result.negativity for result in courier.sentimentResults])

            score = self.__calculateScore(distance, (positivity - negativity) / (1 if n == 0 else n))
            self.customer.scoreWithHub[courier] = score

    def __sorting(self):
        scoreDict = {v: k for k, v in self.customer.scoreWithHub.items()}
        scores = list(scoreDict.keys())
        timSort(scores)
        scores.reverse()
        self.ranking = {scoreDict[v]: v for v in scores}

    def getRanking(self):
        return self.ranking
