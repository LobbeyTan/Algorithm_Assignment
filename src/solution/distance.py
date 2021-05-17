import gmplot
from src.utils.request_with_cache import get
from src.solution.algorithm import cocktailSort
from src.constant import html

APIKey = 'AIzaSyB7nJMebT6DAXDxqcZRO6rCovT7imtmyXE'


# Get the distance from origin to destination
def __getDistance(origins, destinations):
    baseUrl = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": "|".join(f"{x},{y}" for x, y in origins),
        "destinations": "|".join(f"{x},{y}" for x, y in destinations),
        "key": APIKey
    }

    data = get(baseUrl, params)
    distance = data['rows'][0]['elements'][0]['distance']['value']
    return distance


def plotMap(couriers, customers):
    # Initialize gmplot
    gmaps = [gmplot.GoogleMapPlotter(*customer.originCoords, zoom=11,
                                     apikey=APIKey, title=f"Customer {customer.ID}") for customer in customers]

    # mark courier company on map
    for gmap in gmaps:
        for courier in couriers:
            gmap.marker(*courier.coordinate, title=courier.name, label='H',
                        info_window='Delivery Hub: {} ({}  {})'.format(courier.location, *courier.coordinate))

    # Calculate the best route based on shortest distance for all courier company
    for customer, gmap in zip(customers, gmaps):

        # Get distance from origin to destination without going through the hub
        customer.distance = __getDistance([customer.originCoords], [customer.desCoords]) / 1000

        for courier in couriers:
            # Get distance from origin to destination go through hub
            distance1 = __getDistance([customer.originCoords], [courier.coordinate])
            distance2 = __getDistance([courier.coordinate], [customer.desCoords])
            totalDistance = (distance1 + distance2) / 1000
            customer.distanceThrough(courier, totalDistance)

        sortedCouriers = cocktailSort(customer.distanceWithHub)

        customer.minimumDistance = sortedCouriers[0][1]
        customer.minDistanceHub = sortedCouriers[0][0].name

        sortedCouriers.reverse()
        for i, courierWithDist in enumerate(sortedCouriers):
            colour, zIndex = ('red', 2) if i == len(sortedCouriers) - 1 else ('blue', 0)

            gmap.directions(customer.originCoords, customer.desCoords, color=colour, zIndex=zIndex,
                            waypoints=[courierWithDist[0].coordinate])

        # Plot direction for shortest route in map for each customer
        gmap.directions(customer.originCoords, customer.desCoords, color='black', zIndex=1)

        # Draw the map to an HTML file:
        gmap.draw(f"{html}/customer{customer.ID}.html")
