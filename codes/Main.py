import tkinter as tk
from tkinter import *
from tkinter import messagebox
import time, os, sys
from colorama import Fore, Style
import colorama, numpy as np
from generic import JsonParser as jp
from PIL import ImageTk
import random

class Minesweeper:

    EMPTY = 0
    BOMB = 1
    FLAG = 2

    def initializePaths(self):
        self.projectDirectoryPath = os.path.abspath(os.path.join('..'))
        self.codesDirectoryPath = os.path.join(self.projectDirectoryPath, 'codes')
        self.genericDirectoryPath = os.path.join(self.projectDirectoryPath, 'generic')
        self.logsDirectoryPath = os.path.join(self.projectDirectoryPath, 'logs')
        self.resourcesDirectoryPath = os.path.join(self.projectDirectoryPath, 'resources')
        self.iconsDirectoryPath = os.path.join(self.resourcesDirectoryPath, 'icons')
        self.imagesDirectoryPath = os.path.join(self.resourcesDirectoryPath, 'images')

    def initializeParams(self):
        if len(sys.argv) < 2:
            self.liveLogging = False
        elif len(sys.argv) > 2:
            self.liveLogging = False
        else:
            try:
                file = open(sys.argv[1], 'wb')
                file.closed
                self.liveLogging = True
            except:
                self.displayError(message='Cannot open the log file!')
                self.liveLogging = False

        self.gridSize = self.config['gamePlay']['gridSize']
        self.noOfBombs = self.config['gamePlay']['noOfBombs']
        if self.noOfBombs > self.gridSize ** 2:
            self.displayError('Number of Bombs > Total Grid Size!')
            sys.exit(1)
        self.surroundingDistance = self.config['gamePlay']['surroundingDistance']

        self.noOfBombsLeft = self.noOfBombs
        self.noOfTilesLeft = self.gridSize ** 2 - self.noOfBombs

    def initializeGUI(self):

        self.root = tk.Tk()
        self.root.title(self.config['title'])
        self.root.iconbitmap(self.config['imageFilePaths']['icon'])
        self.addFrames()

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
        self.leftLabelConfig['text'] = 'Number of Bombs Left: '
        self.leftLabelText = StringVar()
        self.leftLabelText.set(self.noOfBombsLeft)
        self.leftLabelConfig['textvariable'] = self.leftLabelText
        self.leftLabel.config(self.leftLabelConfig)
        self.leftLabel.pack(side=tk.LEFT, ipadx=10, ipady=10)

        self.rightLabel = tk.Label(master=self.infoFrame)
        self.rightLabelConfig = self.genericLabelConfig
        self.rightLabelConfig['text'] = str(self.noOfBombs)
        self.rightLabelText = StringVar()
        self.rightLabelText.set(self.noOfBombsLeft)
        self.rightLabelConfig['textvariable'] = self.rightLabelText
        self.rightLabel.config(self.rightLabelConfig)
        self.leftLabel.pack(side=tk.LEFT, ipadx=10, ipady=10)

    def addGridFrame(self):
        self.gridFrame = tk.Frame(self.root)
        self.gridFrame.config(self.config['frameConfig'])
        self.gridFrame.pack(side=tk.TOP, padx=10, pady=10)

        self.setupButtons()

    def __init__(self):

        colorama.init()
        self.initializePaths()
        self.config = jp.parseFile(filePath=os.path.join(self.resourcesDirectoryPath, 'config.json'))

        self.initializeParams()
        self.setupBombs()
        self.setupNeighbours()
        self.initializeGUI()

        self.root.resizable(width=False, height=False)
        self.centraizeWindow(self.root)
        self.root.mainloop()

        self.seconds = 0
        self.minutes = 0
        self.startTime = time.time()

    def getRandomCell(self, type):
        x = random.randint(0, self.gridSize - 1)
        y = random.randint(0, self.gridSize - 1)
        while self.grid[x, y] != type:
            pass
        return (x, y)

    def setupBombs(self):
        self.grid = np.zeros(shape=(self.gridSize, self.gridSize))
        for i in range(0, self.noOfBombs):
            pos = self.getRandomCell(Minesweeper.EMPTY)
            self.grid[pos[0], pos[1]] = Minesweeper.BOMB

    def setupButtons(self):
        self.buttonGrid = [[None] * self.grid for _ in range(0, self.gridSize)]
        for i in range(0, self.grid):
            for j in range(0, self.grid):
                self.buttonGrid[i][j] = self.makeButton((i, j))
                self.buttonGrid[i][j].grid(row=i + 1, column=j)

    def displayResult(self, type=False):

        if self.config['liveLogging']:
            print('Game Over!')

        self.seconds = int(time.time() - self.startTime) - self.minutes * 60
        if self.seconds >= 60:
            self.minutes = self.seconds / 60
            self.seconds = self.seconds % 60

        for i in range(self.grid):
            for j in range(self.grid):
                buttonConfig = self.genericButtonConfig
                if self.grid[i][j] == -1:
                    image = ImageTk.PhotoImage(file=self.config['imageFilePaths']['unexploredBomb'])
                    buttonConfig['image'] = image
                    buttonConfig['text'] = ' '
                    buttonConfig['relief'] = tk.SUNKEN
                    buttonConfig['cursor'] = 'target'
                    buttonConfig['state'] = tk.DISABLED
                    buttonConfig['font'] = (self.config['fonts'][self.fontOption], self.config['fontSizes']['button'])
                    self.buttonGrid[i][j].config(buttonConfig)
                    self.buttonGrid[i][j].image = image

        if not type:
            messagebox.showinfo(title='Congratulations', message='Got through it well!\nYou Won!')
        else:
            messagebox.showwarning(title='Oops!', message='Bad stepping huh?\nYou Lost')

        self.root.destroy()

        # resultScreen = tk.Tk()
        # self.centerWindow(resultScreen)
        # resultScreen.geometry('{}x{}'.format(300, 400))
        # resultScreen.iconbitmap(self.config['imageFilePaths']['icon'])
        #
        # resultScreen.title('Game Over!')
        #
        # resultMessage = tk.Label(resultScreen)
        # resultMessageConfig = self.config['resultMessageConfig']
        # if not type:
        #     resultMessageConfig['text'] = 'You Lost!'
        #     resultMessageConfig['fg'] = '#000000'
        #     print('You Lost!')
        # else:
        #     resultMessageConfig['text'] = 'You Won!'
        #     print('You Won!')
        #     resultMessageConfig['fg'] = self.config['colors']['unexplored']
        # resultMessageConfig['font'] = (self.config['fonts'][self.fontOption], self.config['fontSizes']['resultLabel'])
        # resultMessage.config(resultMessageConfig)
        # print('Total Time of the play : ' + str(self.minutes) + ' Minutes & ' + str(self.seconds) + ' Seconds')
        #
        # resultButton = tk.Button(resultScreen, command=lambda : exit(1))
        # resultButtonConfig = self.config['resultButtonConfig']
        # resultButtonConfig['font'] = (self.config['fonts'][self.fontOption], self.config['fontSizes']['resultButton'])
        # resultButton.config(resultButtonConfig)
        # resultMessage.pack()
        # resultButton.pack()
        # resultScreen.mainloop()

    def rightClick(self, event, arg):
        x = arg[0]
        y = arg[1]
        if self.config['liveLogging']:
            print('Right click at: (' + str(x+1) + ',' + str(y+1) + ')')
        buttonConfig = self.genericButtonConfig
        if self.buttonGrid[x][y]['relief'] == tk.RAISED:
            image = ImageTk.PhotoImage(file=self.config['imageFilePaths']['unexploredFlag'])
            buttonConfig['image'] = image
            buttonConfig['text'] = ' '
            buttonConfig['bg'] = self.config['colors']['flag']
            buttonConfig['relief'] = tk.SUNKEN
            buttonConfig['cursor'] = 'target'
            buttonConfig['state'] = tk.NORMAL
            buttonConfig['font'] = (self.config['fonts'][self.fontOption], self.config['fontSizes']['button'])
            self.buttonGrid[x][y].image = image
            self.noOfBombsLeft -= 1
            self.rightLabelText.set(self.noOfBombsLeft)
        else:
            image = ImageTk.PhotoImage(file=self.config['imageFilePaths']['unexplored'])
            buttonConfig['image'] = image
            buttonConfig['text'] = ' '
            buttonConfig['bg'] = self.config['colors']['unexplored']
            buttonConfig['relief'] = tk.RAISED
            buttonConfig['cursor'] = 'circle'
            buttonConfig['state'] = tk.NORMAL
            buttonConfig['font'] = (self.config['fonts'][self.fontOption], self.config['fontSizes']['button'])
            self.buttonGrid[x][y].image = image
            self.noOfBombsLeft += 1
            self.rightLabelText.set(self.noOfBombsLeft)
        self.buttonGrid[x][y].config(buttonConfig)

    def leftClick(self, x, y):
        if self.config['liveLogging']:
            print('Left click at: (' + str(x+1) + ',' + str(y+1) + ')')
        buttonConfig = self.genericButtonConfig

        if self.grid[x][y] == -1:
            image = ImageTk.PhotoImage(file=self.config['imageFilePaths']['exploredBomb'])
            buttonConfig['image'] = image
            buttonConfig['text'] = ' '
            buttonConfig['bg'] = self.config['colors']['explored']
            buttonConfig['relief'] = tk.SUNKEN
            buttonConfig['cursor'] = 'x_cursor'
            buttonConfig['font'] = (self.config['fonts'][self.fontOption], self.config['fontSizes']['button'])
            buttonConfig['state'] = DISABLED
            self.buttonGrid[x][y].image = image
            self.buttonGrid[x][y].config(buttonConfig)
            self.displayResult(type=False)

        elif self.grid[x][y] > 0 and self.buttonGrid[x][y]['relief'] == tk.RAISED:
            image = ImageTk.PhotoImage(file=self.config['imageFilePaths']['explored'])
            buttonConfig['image'] = image
            buttonConfig['text'] = self.grid[x][y]
            buttonConfig['bg'] = self.config['colors']['explored']
            buttonConfig['relief'] = tk.SUNKEN
            buttonConfig['cursor'] = 'x_cursor'
            buttonConfig['font'] = (self.config['fonts'][self.fontOption], self.config['fontSizes']['button'])
            buttonConfig['state'] = ACTIVE
            self.buttonGrid[x][y].image = image
            self.buttonGrid[x][y].config(buttonConfig)
            self.noOfTilesLeft -= 1
            if self.noOfTilesLeft == 0:
                self.displayResult(type=True)

        elif self.grid[x][y] == 0 and self.buttonGrid[x][y]['relief'] == tk.RAISED:
            image = ImageTk.PhotoImage(file=self.config['imageFilePaths']['explored'])
            buttonConfig['image'] = image
            buttonConfig['text'] = ' '
            buttonConfig['bg'] = self.config['colors']['explored']
            buttonConfig['relief'] = tk.SUNKEN
            buttonConfig['cursor'] = 'x_cursor'
            buttonConfig['font'] = (self.config['fonts'][self.fontOption], self.config['fontSizes']['button'])
            buttonConfig['state'] = DISABLED
            self.buttonGrid[x][y].image = image
            self.buttonGrid[x][y].config(buttonConfig)
            if x-1 > -1:
                if self.grid[x - 1][y] >= 0 and self.buttonGrid[x - 1][y]['relief'] == tk.RAISED:
                    self.leftClick(x - 1, y)
            if y+1 < self.grid:
                if self.grid[x][y + 1] >= 0 and self.buttonGrid[x][y + 1]['relief'] == tk.RAISED:
                    self.leftClick(x, y + 1)
            if x+1 < self.grid:
                if self.grid[x + 1][y] >= 0 and self.buttonGrid[x + 1][y]['relief'] == tk.RAISED:
                    self.leftClick(x + 1, y)
            if y-1 > -1:
                if self.grid[x][y - 1] >= 0 and self.buttonGrid[x][y - 1]['relief'] == tk.RAISED:
                    self.leftClick(x, y - 1)
            self.noOfTilesLeft -= 1
            if self.noOfTilesLeft == 0:
                self.displayResult(type=True)

    def makeButton(self, pos):
        button = tk.Button(self.gridFrame)
        if not os.path.isfile(self.config['imageFilePaths']['unexplored']):
            self.displayError('Cannot Find Image File!')
            sys.exit(1)
        image = ImageTk.PhotoImage(file=self.config['imageFilePaths']['unexplored'])
        image = image.subsample(2, 2)
        buttonConfig = self.config['genericButtonConfig']
        buttonConfig['bg'] = self.config['colors']['unexplored']
        buttonConfig['image'] = image
        button.config(buttonConfig)
        button.bind('<Button-1>', self.leftClick(pos))
        button.bind('<Button-3>', self.rightClick(pos))
        button.image = image
        return button

    def getSurroundingCells(self, pos):
        surroundingCells = []

        i = pos(0) - self.surroundingDistance
        j = pos(1) - self.surroundingDistance

        for j in range(pos(1) - self.surroundingDistance, pos(0) + self.surroundingDistance):
            if i > -1 and i < self.grid and j > -1 and j < self.grid:
                surroundingCells.append((i, j))
        j += 1

        for i in range(pos(0) - self.surroundingDistance, pos(0) + self.surroundingDistance):
            if i > -1 and i < self.grid and j > -1 and j < self.grid:
                surroundingCells.append((i, j))
        i += 1

        for j in range(pos(1) + self.surroundingDistance, pos(1) - self.surroundingDistance, -1):
            if i > -1 and i < self.grid and j > -1 and j < self.grid:
                surroundingCells.append((i, j))
        j -= 1

        for i in range(pos(0) + self.surroundingDistance, pos(0) - self.surroundingDistance, -1):
            if i > -1 and i < self.grid and j > -1 and j < self.grid:
                surroundingCells.append((i, j))
        i -= 1

        return surroundingCells

    def setupNeighbours(self):
        for i in range(self.grid):
            for j in range(self.grid):
                if self.grid[i][j] == 0:
                    surroundingCells = self.getSurroundingCells(i, j)
                    for surroundingCell in surroundingCells:
                        if self.grid[surroundingCell[0]][surroundingCell[1]] == -1:
                            self.grid[i][j] += 1

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