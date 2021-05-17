from src.utils.entity import *
from src.solution.algorithm import timSort
from src.constant import courierDict


class CourierRecommendation:
    def __init__(self, customer):
        self.customer = customer
        self.ranking = {}

    def analyzeRanking(self):
        self.__preprocessing()
        self.__sorting()

    # Calculate the total score of distance and Sentiment score
    def __calculateScore(self, distance, sentimentScore):
        # 0.5 and 100 are weightage of distance and sentimentScore, distance is on minus,
        # So the least distance will have higher total score
        score = (0.5 * - distance) + (100 * sentimentScore) + 100
        return score

    # Function to process total of sentiment score and call calculateScore function
    def __preprocessing(self):
        for courier, distance in self.customer.distanceWithHub.items():
            n = len(courier.sentimentResults)

            # sum up the sentiment Result of positive and negative words
            positivity = sum([result.positivity for result in courier.sentimentResults])
            negativity = sum([result.negativity for result in courier.sentimentResults])

            # calculate total sentiment score = total positivity minus total negativity divided by amount of article
            score = self.__calculateScore(distance, (positivity - negativity) / (1 if n == 0 else n))
            self.customer.scoreWithHub[courier] = score

    # Sort the list of score
    def __sorting(self):
        scoreDict = {v: k for k, v in self.customer.scoreWithHub.items()}
        scores = list(scoreDict.keys())
        # Calling timsort
        timSort(scores)
        # Reverse the list , because it was sorted in ascending order, the recommendation list descending order
        scores.reverse()
        self.ranking = {scoreDict[v]: v for v in scores}

    # Getter for rank
    def getRanking(self):
        return self.ranking
