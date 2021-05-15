import time
import tkinter as tk
import matplotlib.pyplot as plt
import threading
import imageio
import audioplayer
import speech_recognition as sr
import random
from PIL import Image, ImageTk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter.scrolledtext import ScrolledText
from multiprocessing import Process, Array
from constant import *
from scipy.io import wavfile
from os import listdir
from dtw import runDTW


class Page4(tk.Frame):
    isInitialized = False

    def __init__(self, parent, customers, couriers, controller, name):
        tk.Frame.__init__(self, parent, bg=lightBlue)
        print(f"{name} Frame initialized")

        self.customers = customers
        self.couriers = couriers
        self.controller = controller
        self.name = name

        self.textBox = ScrolledText
        self.showVideo()
        self.showAudioGraph()

    def showVideo(self):
        frame = tk.Frame(self, bg=lightBlue)
        frame.grid(row=0, column=0, sticky="new", pady=7, padx=10)

        video = tk.Label(frame, anchor="center", borderwidth=2, relief="groove")
        video.grid(row=0, column=0, sticky="nsew", rowspan=2)

        controller = tk.Button(frame)
        controller.place(x=5, y=175)

        TkVideo("voice/video.mp4", "voice/voice.wav", controller, video, size=(300, 200))

        tk.Label(frame, text="Extracted Word Using Google Speech Recognition:",
                 anchor="w", font=textFontU, background=lightBlue).grid(row=0, column=1, padx=10, sticky="nw")

        self.runRecognition()

        self.textBox = ScrolledText(frame, width=63, height=10, wrap=tk.WORD, background=blue, font=textFontN)
        self.textBox.grid(row=1, column=1, pady=7, padx=10)
        self.textBox.insert(tk.INSERT, "Analyzing")

    def runRecognition(self):
        recognitionThread = threading.Thread(target=self.__recognition)
        recognitionThread.daemon = 1
        recognitionThread.start()

    def __recognition(self):
        recognizer = sr.Recognizer()
        audioFile = sr.AudioFile("voice/voice.wav")

        with audioFile as source:
            audio = recognizer.record(source)

        text = recognizer.recognize_google(audio, language="ms-MY")
        self.textBox.delete("1.0", "end")
        self.textBox.insert(tk.INSERT, text)

    def showAudioGraph(self):
        canvas = tk.Canvas(self, width=780, height=400)
        scrollable_frame = tk.Frame(canvas)
        vsb = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)

        vsb.grid(row=1, column=0, sticky="ens")
        canvas.grid(row=1, column=0, sticky="wns")
        canvas.create_window((5, 5), window=scrollable_frame, anchor="nw")

        plt.style.use('seaborn-whitegrid')
        for i, testWord in enumerate(listdir("test/")):
            color = "#" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)])
            AudioContent(scrollable_frame, testWord, row=i // 2, column=i % 2, color=color)

        scrollable_frame.bind("<Configure>", lambda event, canvas=canvas: self.__onFrameConfigure(canvas))

    def __onFrameConfigure(self, canvas):
        canvas.configure(scrollregion=canvas.bbox("all"))


class AudioContent:
    def __init__(self, master, name, row, column, color):
        self.name = name
        self.color = color
        self.path = f"test/{name}"
        self.audioPlayer = audioplayer.AudioPlayer(self.path)
        fs, self.data = wavfile.read(self.path)

        self.isAnalyzing = False

        self.frame = tk.Frame(master, bg=blue)
        self.frame.grid(row=row, column=column, ipady=10)

        self.status = tk.Label
        self.result = tk.Label
        self.distance = tk.Label

        self.plotGraph()
        self.showDTW()

    def plotGraph(self):
        top = tk.Frame(self.frame)
        top.grid(row=0, column=0)

        fig = plt.Figure(figsize=(5, 2), dpi=80, facecolor='w', edgecolor='k')
        ax = fig.add_subplot(111)
        ax.set_title(f"Waveform of {self.name.capitalize()}")
        ax.title.set_fontsize(10)

        # change the style of the axis spines
        ax.spines['top'].set_color('none')
        ax.spines['right'].set_color('none')

        # Turn off tick labels
        ax.set_yticklabels([])
        ax.set_xticklabels([])
        ax.plot(self.data, color=self.color)

        waveform = FigureCanvasTkAgg(fig, top)
        waveform.get_tk_widget().grid(row=0, column=0)

    def showDTW(self):
        btm = tk.Frame(self.frame, bg=blue)
        btm.grid(row=1, column=0)

        play = getIconImage("play")
        button = tk.Button(btm, image=play, command=self.audioPlayer.play, height=22, **buttonConfig3)
        button.image = play
        button.grid(row=0, column=0, pady=10)

        tk.Button(btm, text="Run DTW", command=self.startDTW,
                  **buttonConfig3).grid(row=0, column=1, sticky="w", pady=10)

        self.status = tk.Label(btm, text="Not Yet Analyze", width=15, anchor="center", font=textFontB, background=blue)
        self.status.grid(row=0, column=2, sticky="w", pady=10)

        self.result = tk.Label(btm, text="UNKNOWN", width=15, anchor="center", font=textFontB, background=blue)
        self.result.grid(row=0, column=3, sticky="w", pady=10)

        tk.Label(btm, text="DTW Distance : ", font=textFontB, background=blue).grid(row=1, column=2)
        self.distance = tk.Label(btm, text="NULL", font=textFontB, background=blue)
        self.distance.grid(row=1, column=3)

    def startDTW(self):
        if not self.isAnalyzing:
            self.isAnalyzing = True
            self.status.config(text="Analyzing", foreground="black")

            rtn = Array('d', 3)
            process = Process(target=runDTW, args=(self.name, rtn, "split", 60))
            thread = threading.Thread(target=self.__updateLabels, args=(process, rtn))
            thread.setDaemon(True)

            process.start()
            thread.start()

    def __DTW(self):
        pass
        # self.isFound, self.dist, self.chunkth = runDTW(self.name, limit=60)

    def __updateLabels(self, process, rtn):
        process.join()
        isFound = True if int(rtn[0]) == 1 else False
        dist = rtn[1]
        chunkth = None if int(rtn[2]) == -1 else int(rtn[2])

        self.distance['text'] = "{:7.3f}".format(dist)
        if isFound:
            self.result.config(text="FOUND", foreground="green")
            print(f"{self.name} is found at {chunkth}.wav with average distance of {dist}")
        else:
            self.result.config(text="NOT FOUND", foreground="red")
            print(f"{self.name} is not found as average distance is {dist}")

        self.isAnalyzing = False
        self.status.config(text="Finish Analyzed", foreground="black")
        process.terminate()


class TkVideo:
    def __init__(self, videoPath, audioPath, controller, label, loop=0, size=(640, 360)):
        self.path = videoPath
        self.audioPath = audioPath
        self.controller = controller
        self.label = label
        self.loop = loop
        self.size = size

        self.isRunning = False
        self.isStarted = False

        self.startIcon = getIconImage("start")
        self.pauseIcon = getIconImage("pause")

        self.__configureController()

        self.frame_data = imageio.get_reader(videoPath)
        self.__setFirstFrame()

        self.audioPlayer = audioplayer.AudioPlayer(audioPath)

    def __load(self):
        if self.loop == 1:
            while True:
                self.__playVideo(frame_data)
        else:
            self.__playVideo()
        self.isStarted = False
        self.isRunning = False
        self.__configureController()

    def play(self):
        if not self.isStarted:
            self.audioPlayer.play()
            thread = threading.Thread(target=self.__load)
            thread.daemon = 1
            thread.start()
            self.isStarted = True

        self.audioPlayer.resume()
        self.isRunning = True
        self.__configureController()

    def pause(self):
        self.audioPlayer.pause()
        self.isRunning = False
        self.__configureController()

    def __playVideo(self):
        for image in self.frame_data.iter_data():
            while not self.isRunning:
                pass
            frame_image = ImageTk.PhotoImage(Image.fromarray(image).resize(self.size))
            self.label.config(image=frame_image)
            self.label.image = frame_image
            time.sleep(0.02)

    def __setFirstFrame(self):
        firstFrame = self.frame_data.get_data(0)

        frame_image = ImageTk.PhotoImage(Image.fromarray(firstFrame).resize(self.size))
        self.label.config(image=frame_image)
        self.label.image = frame_image

    def __configureController(self):
        if self.isRunning:
            self.controller['image'] = self.pauseIcon
            self.controller['command'] = self.pause
        else:
            self.controller['image'] = self.startIcon
            self.controller['command'] = self.play
