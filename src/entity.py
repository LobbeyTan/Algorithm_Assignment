from abc import ABC
from collections import Sequence


class Courier:
    def __init__(self, name, location, coordinate):
        self.name = name
        self.location = location
        self.coordinate = coordinate
        self.sentimentResults = []

    def __str__(self):
        return self.name

    def toString(self):
        return f"{self.name} has a delivery hub located at {self.location} with coordinate {self.coordinate}"

    def appendSentiment(self, sentimentResult):
        self.sentimentResults.append(sentimentResult)


class Customer:
    def __init__(self, ID, origin, destination, originCoords, desCoords):
        self.ID = ID
        self.origin = origin
        self.destination = destination
        self.originCoords = originCoords
        self.desCoords = desCoords
        self.distance = 0
        self.distanceWithHub = {}
        self.scoreWithHub = {}

        self.minimumDistance = 0
        self.minDistanceHub = ""

    def __str__(self):
        return f"Customer {self.ID} delivers parcel " \
               f"from {self.origin} ({self.originCoords}) to {self.destination} ({self.desCoords})"

    def distanceThrough(self, courier, dist):
        self.distanceWithHub[courier] = dist


class Coordinate:
    def __init__(self, lat, long):
        self.lat = lat
        self.long = long

    def __str__(self):
        return f"{self.lat}, {self.long}"

    def __iter__(self):
        yield self.lat
        yield self.long
