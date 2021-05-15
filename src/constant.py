from PIL import Image, ImageTk
from tkinter.font import Font


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

activeColor = "#38559B"
darkBlue = "#5680E9"
lightBlue = "#84CEEB"
cyanBlue = "#5AB9EA"
blue = "#D6EEF3"
lightPurple = "#C1C8E4"
darkPurple = "#8860D0"
purple = "#E0C8E4"
white = "#FFFFFF"
black = "#000000"

buttonFontB = ("Georgia", 9, "bold")
buttonFontN = ("Georgia", 10)

subFontN = ("Arial", 11)
subFontB = ("Arial", 11, "bold")
textFontN = ("Arial", 9)
textFontB = ("Arial", 9, "bold")
textFontU = ("Arial", 10, "bold", "underline")

buttonConfig1 = {"background": darkBlue, "activebackground": activeColor, "foreground": white, "font": buttonFontB}
buttonConfig2 = {"background": darkPurple, "activebackground": activeColor, "foreground": white, "font": buttonFontB}
buttonConfig3 = {"background": lightPurple, "activebackground": darkPurple, "foreground": black, "font": buttonFontN}
dropDownConfig = {"background": lightPurple, "activebackground": lightPurple, "foreground": black}