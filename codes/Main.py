import tkinter as tk
from tkinter import *
from tkinter import messagebox
import time, os, sys, cv2
from colorama import Fore, Style
import colorama, numpy as np
from generic import JsonParser as jp
from PIL.ImageTk import PhotoImage
import random

class Minesweeper:

    EMPTY = 0
    BOMB = -1
    FLAG = -2

    def __init__(self):

        colorama.init()
        self.initializePaths()
        self.config = jp.parseFile(filePath=os.path.join(self.resourcesDirectoryPath, 'config.json'))

        self.initializeParams()
        self.setupBombs()
        self.setupNoOfBombs()

        self.seconds = 0
        self.startTime = time.time()
        self.minutes = 0

        self.initializeGUI()

    def initializePaths(self):
        self.projectDirectoryPath = os.path.abspath(os.path.join('..'))
        self.codesDirectoryPath = os.path.join(self.projectDirectoryPath, 'codes')
        self.genericDirectoryPath = os.path.join(self.projectDirectoryPath, 'generic')
        self.logsDirectoryPath = os.path.join(self.projectDirectoryPath, 'logs')
        self.resourcesDirectoryPath = os.path.join(self.projectDirectoryPath, 'resources')
        self.iconsDirectoryPath = os.path.join(self.resourcesDirectoryPath, 'icons')
        self.imagesDirectoryPath = os.path.join(self.resourcesDirectoryPath, 'images')

    def initializeParams(self):

        self.gridSize = self.config['gamePlay']['gridSize']
        self.noOfBombs = self.config['gamePlay']['noOfBombs']
        if self.noOfBombs > self.gridSize ** 2:
            self.displayError('Number of Bombs > Total Grid Size!')
            sys.exit(1)
        self.surroundingDistance = self.config['gamePlay']['surroundingDistance']

        self.noOfBombsLeft = self.noOfBombs
        self.noOfTilesLeft = self.gridSize ** 2 - self.noOfBombs

    def setupBombs(self):
        self.grid = np.zeros(shape=(self.gridSize, self.gridSize), dtype=np.int8)
        for i in range(0, self.noOfBombs):
            x = random.randint(0, self.gridSize - 1)
            y = random.randint(0, self.gridSize - 1)
            while self.grid[x, y] != Minesweeper.EMPTY:
                x = random.randint(0, self.gridSize - 1)
                y = random.randint(0, self.gridSize - 1)
            self.grid[x, y] = Minesweeper.BOMB

    def setupNoOfBombs(self):
        tempGrid = np.copy(-1*self.grid).astype(dtype=np.uint8)
        kernel = np.ones(shape=(2*self.surroundingDistance+1, 2*self.surroundingDistance+1))
        kernel[1:2*self.surroundingDistance, 1:2*self.surroundingDistance] = 0
        self.grid = self.grid + np.multiply((self.grid + 1), cv2.filter2D(src=tempGrid, ddepth=-1, kernel=kernel, borderType=cv2.BORDER_CONSTANT))

    def initializeGUI(self):

        self.root = tk.Tk()
        self.root.config(self.config["rootConfig"])
        self.root.title(self.config['title'])
        self.root.iconbitmap(os.path.join(self.iconsDirectoryPath, self.config['fileNames']['icons']['rootIcon']))
        self.addFrames()

        self.root.resizable(width=False, height=False)
        self.centraizeWindow(self.root)
        self.root.mainloop()

    def addFrames(self):
        self.addInfoFrame()
        self.addGridFrame()

    def addInfoFrame(self):
        self.infoFrame = tk.Frame(master=self.root)
        self.infoFrame.pack(side=tk.TOP)
        self.infoFrame.config(self.config['infoFrameConfig'])

        self.genericLabelConfig = self.config['genericLabelConfig']

        self.leftLabel = tk.Label(master=self.infoFrame)
        self.leftLabelConfig = self.genericLabelConfig
        self.leftLabelText = StringVar()
        self.leftLabelText.set('Number of Bombs Left: ')
        self.leftLabelConfig['textvariable'] = self.leftLabelText
        self.leftLabel.config(self.leftLabelConfig)
        self.leftLabel.pack(side=tk.LEFT, ipadx=10, ipady=10)

        self.rightLabel = tk.Label(master=self.infoFrame)
        self.rightLabelConfig = self.genericLabelConfig
        self.rightLabelText = StringVar()
        self.rightLabelText.set(self.noOfBombsLeft)
        self.rightLabelConfig['textvariable'] = self.rightLabelText
        self.rightLabel.config(self.rightLabelConfig)
        self.rightLabel.pack(side=tk.RIGHT, ipadx=10, ipady=10)

    def addGridFrame(self):
        self.gridFrame = tk.Frame(self.root)
        self.gridFrame.config(self.config['gridFrameConfig'])
        self.gridFrame.pack(side=tk.TOP, padx=10, pady=10)
        self.setupButtons()

    def setupButtons(self):
        self.buttonGrid = [[None for _ in range(self.gridSize)] for _ in range(self.gridSize)]
        for i in range(0, self.gridSize):
            for j in range(0, self.gridSize):
                self.buttonGrid[i][j] = self.makeButton((i, j))
                self.buttonGrid[i][j].grid(row=i, column=j)

    def makeButton(self, pos):
        button = tk.Button(self.gridFrame)
        image = PhotoImage(file=os.path.join(self.imagesDirectoryPath, self.config['fileNames']['images']['unexplored']))
        buttonConfig = self.config['genericButtonConfig']
        buttonConfig['bg'] = self.config['buttonColors']['unexplored']
        buttonConfig['image'] = image
        button.config(buttonConfig)
        button.bind('<Button-1>', lambda event, position=pos: self.leftClick(pos))
        button.bind('<Button-3>', lambda event, position=pos: self.rightClick(pos))
        button.image = image
        return button

    # def displayResult(self, type=False):
    #
    #     self.seconds = int(time.time() - self.startTime) - self.minutes * 60
    #     if self.seconds >= 60:
    #         self.minutes = self.seconds / 60
    #         self.seconds = self.seconds % 60
    #
    #     for i in range(self.gridSize):
    #         for j in range(self.gridSize):
    #             buttonConfig = self.genericButtonConfig
    #             if self.grid[i][j] == -1:
    #                 image = PhotoImage(file=self.config['imageFilePaths']['unexploredBomb'])
    #                 buttonConfig['image'] = image
    #                 buttonConfig['text'] = ' '
    #                 buttonConfig['relief'] = tk.SUNKEN
    #                 buttonConfig['cursor'] = 'target'
    #                 buttonConfig['state'] = tk.DISABLED
    #                 buttonConfig['font'] = (self.config['fonts'][self.fontOption], self.config['fontSizes']['button'])
    #                 self.buttonGrid[i][j].config(buttonConfig)
    #                 self.buttonGrid[i][j].image = image
    #
    #     if not type:
    #         messagebox.showinfo(title='Congratulations', message='Got through it well!\nYou Won!')
    #     else:
    #         messagebox.showwarning(title='Oops!', message='Bad stepping huh?\nYou Lost')
    #
    #     self.root.destroy()
    #
    #     # resultScreen = tk.Tk()
    #     # self.centerWindow(resultScreen)
    #     # resultScreen.geometry('{}x{}'.format(300, 400))
    #     # resultScreen.iconbitmap(self.config['imageFilePaths']['icon'])
    #     #
    #     # resultScreen.title('Game Over!')
    #     #
    #     # resultMessage = tk.Label(resultScreen)
    #     # resultMessageConfig = self.config['resultMessageConfig']
    #     # if not type:
    #     #     resultMessageConfig['text'] = 'You Lost!'
    #     #     resultMessageConfig['fg'] = '#000000'
    #     #     print('You Lost!')
    #     # else:
    #     #     resultMessageConfig['text'] = 'You Won!'
    #     #     print('You Won!')
    #     #     resultMessageConfig['fg'] = self.config['buttonColors']['unexplored']
    #     # resultMessageConfig['font'] = (self.config['fonts'][self.fontOption], self.config['fontSizes']['resultLabel'])
    #     # resultMessage.config(resultMessageConfig)
    #     # print('Total Time of the play : ' + str(self.minutes) + ' Minutes & ' + str(self.seconds) + ' Seconds')
    #     #
    #     # resultButton = tk.Button(resultScreen, command=lambda : exit(1))
    #     # resultButtonConfig = self.config['resultButtonConfig']
    #     # resultButtonConfig['font'] = (self.config['fonts'][self.fontOption], self.config['fontSizes']['resultButton'])
    #     # resultButton.config(resultButtonConfig)
    #     # resultMessage.pack()
    #     # resultButton.pack()
    #     # resultScreen.mainloop()

    def rightClick(self, pos):
        x = pos[0]
        y = pos[1]

        buttonConfig = self.config['genericButtonConfig']
        if self.buttonGrid[x][y]['relief'] == tk.RAISED:
            image = PhotoImage(file=os.path.join(self.imagesDirectoryPath, self.config['fileNames']['images']['flag']))
            buttonConfig['image'] = image
            buttonConfig['bg'] = self.config['buttonColors']['explored']
            buttonConfig['relief'] = tk.SUNKEN
            buttonConfig['state'] = tk.NORMAL
            self.buttonGrid[x][y].image = image
            self.noOfBombsLeft -= 1
            self.rightLabelText.set(max(0, self.noOfBombsLeft))
        else:
            image = PhotoImage(file=os.path.join(self.imagesDirectoryPath, self.config['fileNames']['images']['unexplored']))
            buttonConfig['image'] = image
            buttonConfig['bg'] = self.config['buttonColors']['unexplored']
            buttonConfig['relief'] = tk.RAISED
            buttonConfig['state'] = tk.NORMAL
            self.buttonGrid[x][y].image = image
            self.noOfBombsLeft += 1
            self.rightLabelText.set(max(0, self.noOfBombsLeft))
        self.buttonGrid[x][y].config(buttonConfig)

    def leftClick(self, pos):
        x = pos[0]
        y = pos[1]

        buttonConfig = self.config['genericButtonConfig']

        if self.grid[x][y] == -1:
            image = PhotoImage(file=os.path.join(self.imagesDirectoryPath, self.config['fileNames']['images']['exploredBomb']))
            buttonConfig['image'] = image
            buttonConfig['bg'] = self.config['buttonColors']['explored']
            buttonConfig['relief'] = tk.SUNKEN
            buttonConfig['state'] = DISABLED
            self.buttonGrid[x][y].image = image
            self.buttonGrid[x][y].config(buttonConfig)
            self.displayResult(type=False)

        elif self.grid[x][y] > 0 and self.buttonGrid[x][y]['relief'] == tk.RAISED:
            image = PhotoImage(file=os.path.join(self.imagesDirectoryPath, self.config['fileNames']['images']['explored']))
            buttonConfig['image'] = image
            buttonConfig['text'] = self.grid[x][y]
            buttonConfig['bg'] = self.config['buttonColors']['explored']
            buttonConfig['relief'] = tk.SUNKEN
            buttonConfig['state'] = ACTIVE
            self.buttonGrid[x][y].image = image
            self.buttonGrid[x][y].config(buttonConfig)
            self.noOfTilesLeft -= 1
            if self.noOfTilesLeft == 0:
                self.displayResult(type=True)

        elif self.grid[x][y] == 0 and self.buttonGrid[x][y]['relief'] == tk.RAISED:
            image = PhotoImage(file=os.path.join(self.imagesDirectoryPath, self.config['fileNames']['images']['explored']))
            buttonConfig['image'] = image
            buttonConfig['bg'] = self.config['buttonColors']['explored']
            buttonConfig['relief'] = tk.SUNKEN
            buttonConfig['state'] = DISABLED
            self.buttonGrid[x][y].image = image
            self.buttonGrid[x][y].config(buttonConfig)
            if x - 1 > -1:
                if self.grid[x - 1][y] >= 0 and self.buttonGrid[x - 1][y]['relief'] == tk.RAISED:
                    self.leftClick((x - 1, y))
            if y + 1 < self.gridSize:
                if self.grid[x][y + 1] >= 0 and self.buttonGrid[x][y + 1]['relief'] == tk.RAISED:
                    self.leftClick((x, y + 1))
            if x + 1 < self.ggridSize:
                if self.grid[x + 1][y] >= 0 and self.buttonGrid[x + 1][y]['relief'] == tk.RAISED:
                    self.leftClick((x + 1, y))
            if y - 1 > -1:
                if self.grid[x][y - 1] >= 0 and self.buttonGrid[x][y - 1]['relief'] == tk.RAISED:
                    self.leftClick((x, y - 1))
            self.noOfTilesLeft -= 1
            if self.noOfTilesLeft == 0:
                self.displayResult(type=True)

    def displayResult(self, type=False):

        self.seconds = int(time.time() - self.startTime) - self.minutes * 60
        if self.seconds >= 60:
            self.minutes = self.seconds / 60
            self.seconds = self.seconds % 60

        for i in range(self.gridSize):
            for j in range(self.gridSize):
                buttonConfig = self.config['genericButtonConfig']
                if self.grid[i][j] == -1:
                    image = PhotoImage(file=os.path.join(self.imagesDirectoryPath, self.config['fileNames']['images']['bomb']))
                    buttonConfig['image'] = image
                    buttonConfig['relief'] = tk.SUNKEN
                    buttonConfig['state'] = tk.DISABLED
                    self.buttonGrid[i][j].config(buttonConfig)
                    self.buttonGrid[i][j].image = image

        if not type:
            messagebox.showinfo(title='Congratulations', message='Got through it well!\nYou Won!')
        else:
            messagebox.showwarning(title='Oops!', message='Bad stepping huh?\nYou Lost')

        self.root.destroy()

    def centraizeWindow(self, win):
        win.update_idletasks()
        width = win.winfo_width()
        height = win.winfo_height()
        x = (win.winfo_screenwidth() // 2) - (width // 2)
        y = (win.winfo_screenheight() // 2) - (height // 2)
        win.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def displayError(self, message):
        print(Fore.RED+'Error: '+Style.RESET_ALL+str(message))

minesweeper = Minesweeper()