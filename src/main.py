from entity import *
from distance import plotMap
from application import Application
from multiprocessing import Process
from page_2 import Page2
from page_1 import Page1
from page_3 import Page3
from page_4 import Page4


# Initialize all the Courier Company
def getCouriers():
    couriers = [
        Courier("City-link Express", "Port Klang", Coordinate(lat=3.0319924887507144, long=101.37344116244806)),
        Courier("Pos Laju", "Petaling Jaya", Coordinate(lat=3.112924170027219, long=101.63982650389863)),
        Courier("GDEX", "Batu Caves", Coordinate(lat=3.265154613796736, long=101.68024844550233)),
        Courier("J&T", "Kajang", Coordinate(lat=2.9441205329488325, long=101.7901521759029)),
        Courier("DHL", "Sungai Buloh", Coordinate(lat=3.2127230893650065, long=101.57467295692778))
    ]
    return couriers


# Initialize all the Customer
def getCustomers():
    customers = [
        Customer(1, "Rawang", "Bukit Jelutong",
                 originCoords=Coordinate(lat=3.3615395462207878, long=101.56318183511695),
                 desCoords=Coordinate(lat=3.1000170516638885, long=101.53071480907951)),
        Customer(2, "Subang Jaya", "Puncak Alam",
                 originCoords=Coordinate(lat=3.049398375759954, long=101.58546611160301),
                 desCoords=Coordinate(lat=3.227994355250716, long=101.42730357605375)),
        Customer(3, "Ampang", "Cyberjaya",
                 originCoords=Coordinate(lat=3.141855957281073, long=101.76158583424586),
                 desCoords=Coordinate(lat=2.9188704151716256, long=101.65251821655471))
    ]
    return customers


def main():
    couriers = getCouriers()
    customers = getCustomers()

    plotMap(couriers, customers)

    app = Application({
        "page_1": Page1,
        "page_2": Page2,
        "page_3": Page3,
        "page_4": Page4
    }, customers=customers, couriers=couriers)
    # app.overrideredirect(True)
    app.resizable(False, False)
    app.title('Algorithm Design & Analysis Assignment')
    app.geometry('810x655')
    app.eval('tk::PlaceWindow . center')
    app.mainloop()


if __name__ == '__main__':
    process = Process(target=main)
    process.start()
    process.join()
