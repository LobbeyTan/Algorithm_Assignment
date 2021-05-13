from PIL import Image, ImageTk


def getIconImage(name, size=(20, 20)):
    load = Image.open(f"icon/{name}.png")
    load = load.resize(size, Image.ANTIALIAS)
    icon = ImageTk.PhotoImage(load)
    return icon


courierDict = {
    -1: None,
    0: "City-link Express",
    1: "Pos Laju",
    2: "GDEX",
    3: "J&T",
    4: "DHL"
}

