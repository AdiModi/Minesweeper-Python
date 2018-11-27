import argparse
import os
import random
import time
import tkinter as tk
from tkinter import *
from tkinter import messagebox

import colorama
import cv2
import numpy as np
from PIL.ImageTk import PhotoImage
from colorama import Fore, Style


class Minesweeper:
    class CELL_STATES:
        UNOPENED = 1
        FLAGGED = 2
        OPENED = 3

    def __init__(self, gridSize, noOfBombs):

        colorama.init()
        self.result = None
        self.initializePaths()

        self.setupHyperParams(gridSize, noOfBombs)
        self.setupGrids()

        self.setupGUI()

    def initializePaths(self):
        self.projectDirectoryPath = os.path.abspath(os.path.join('..'))
        self.codesDirectoryPath = os.path.join(self.projectDirectoryPath, 'codes')
        self.genericDirectoryPath = os.path.join(self.projectDirectoryPath, 'generic')
        self.logsDirectoryPath = os.path.join(self.projectDirectoryPath, 'logs')
        self.resourcesDirectoryPath = os.path.join(self.projectDirectoryPath, 'resources')
        self.iconsDirectoryPath = os.path.join(self.resourcesDirectoryPath, 'icons')
        self.imagesDirectoryPath = os.path.join(self.resourcesDirectoryPath, 'images')

    def setupHyperParams(self, gridSize, noOfBombs):

        self.gridSize = gridSize
        self.noOfBombs = noOfBombs
        if self.noOfBombs > self.gridSize ** 2:
            displayError('Number of Bombs > Total Grid Size!')
            sys.exit(1)

        self.noOfBombsLeft = self.noOfBombs
        self.noOfUnopenedTiles = self.gridSize ** 2 - self.noOfBombs

    def setupGrids(self):
        self.bombGrid = np.zeros(shape=(self.gridSize, self.gridSize), dtype=np.uint8)
        self.cellStateGrid = np.full(shape=(self.gridSize, self.gridSize), fill_value=Minesweeper.CELL_STATES.UNOPENED,
                                     dtype=np.uint8)
        self.convolvedMatrix = np.zeros(shape=(self.gridSize, self.gridSize), dtype=np.uint8)

        for i in range(0, self.noOfBombs):
            x = random.randint(0, self.gridSize - 1)
            y = random.randint(0, self.gridSize - 1)
            while self.bombGrid[x, y] != 0:
                x = random.randint(0, self.gridSize - 1)
                y = random.randint(0, self.gridSize - 1)
            self.bombGrid[x, y] = 1

        kernel = np.ones(shape=(3, 3))
        self.convolvedMatrix = cv2.filter2D(src=self.bombGrid, ddepth=-1, kernel=kernel, borderType=cv2.BORDER_CONSTANT)

    def setupGUI(self):

        self.root = tk.Tk()
        self.root.config({'bg': '#353535'})
        self.root.title('Minesweeper')
        self.root.iconbitmap(os.path.join(self.iconsDirectoryPath, 'rootIcon.ico'))
        self.addFrames()

        self.root.resizable(width=False, height=False)
        self.centraizeWindow(self.root)
        self.startTime = time.time()
        self.root.mainloop()

    def addFrames(self):
        self.addInfoFrame()
        self.addGridFrame()

    def addInfoFrame(self):
        self.infoFrame = tk.Frame(master=self.root)
        self.infoFrame.pack(side=tk.TOP)
        self.infoFrame.config({'bd': 10, 'bg': '#353535'})

        self.genericLabelConfig = {'bd': 7, 'padx': 10, 'pady': 10, 'bg': '#D9D9D9', 'justify': 'left',
                                   'font': ['Montserrat', 15, 'bold'], 'relief': 'raised'}

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
        if self.noOfBombsLeft < 10:
            self.rightLabelText.set('0' + str(self.noOfBombsLeft))
        else:
            self.rightLabelText.set(self.noOfBombsLeft)
        self.rightLabelConfig['textvariable'] = self.rightLabelText
        self.rightLabel.config(self.rightLabelConfig)
        self.rightLabel.pack(side=tk.RIGHT, ipadx=10, ipady=10)

    def addGridFrame(self):
        self.gridFrame = tk.Frame(self.root)
        self.gridFrame.config({'bd': 10, 'padx': 5, 'pady': 5, 'relief': 'ridge', 'bg': '#D9D9D9'})
        self.gridFrame.pack(side=tk.TOP, padx=10, pady=10)
        self.setupButtons()

    def setupButtons(self):
        self.buttonGrid = [[None for _ in range(self.gridSize)] for _ in range(self.gridSize)]
        for i in range(0, self.gridSize):
            for j in range(0, self.gridSize):
                self.buttonGrid[i][j] = self.makeButton((i, j))
                self.buttonGrid[i][j].grid(row=i, column=j)

    def makeButton(self, pos):
        button = tk.Button(self.gridFrame, cursor='plus')
        image = PhotoImage(file=os.path.join(self.imagesDirectoryPath, 'unexplored.png'))
        buttonConfig = {'bd': 7, 'width': 15, 'height': 15, 'text': ' ', 'relief': 'raised',
                        'font': ['Montserrat', 11, 'bold'], 'compound': 'center'}
        buttonConfig['bg'] = '#224908'
        buttonConfig['image'] = image
        button.config(buttonConfig)
        button.bind('<Button-1>', lambda event, position=pos: self.leftClick(pos))
        button.bind('<Button-3>', lambda event, position=pos: self.rightClick(pos))
        button.image = image
        return button

    def rightClick(self, pos):
        x = pos[0]
        y = pos[1]

        buttonConfig = {'bd': 7, 'width': 15, 'height': 15, 'text': ' ', 'relief': 'raised',
                        'font': ['Montserrat', 11, 'bold'], 'compound': 'center'}
        if self.cellStateGrid[x, y] == Minesweeper.CELL_STATES.UNOPENED:
            if self.noOfBombsLeft == 0:
                return
            self.cellStateGrid[x, y] = Minesweeper.CELL_STATES.FLAGGED
            self.noOfBombsLeft -= 1

            image = PhotoImage(file=os.path.join(self.imagesDirectoryPath, 'flag.png'))
            buttonConfig['image'] = image
            buttonConfig['bg'] = '#BEA57D'
            self.buttonGrid[x][y].image = image
            if self.noOfBombsLeft < 10:
                self.rightLabelText.set('0' + str(self.noOfBombsLeft))
            else:
                self.rightLabelText.set(self.noOfBombsLeft)
            self.buttonGrid[x][y].config(buttonConfig)

        elif self.cellStateGrid[x, y] == Minesweeper.CELL_STATES.FLAGGED:
            self.cellStateGrid[x, y] = Minesweeper.CELL_STATES.UNOPENED
            self.noOfBombsLeft += 1

            image = PhotoImage(file=os.path.join(self.imagesDirectoryPath, 'unexplored.png'))
            buttonConfig['image'] = image
            buttonConfig['bg'] = '#224908'
            self.buttonGrid[x][y].image = image
            if self.noOfBombsLeft < 10:
                self.rightLabelText.set('0' + str(self.noOfBombsLeft))
            else:
                self.rightLabelText.set(self.noOfBombsLeft)
            self.buttonGrid[x][y].config(buttonConfig)

    def leftClick(self, pos):
        x = pos[0]
        y = pos[1]

        buttonConfig = {'bd': 7, 'width': 15, 'height': 15, 'text': ' ', 'relief': 'raised',
                        'font': ['Montserrat', 11, 'bold'], 'compound': 'center'}

        if self.cellStateGrid[x, y] == Minesweeper.CELL_STATES.OPENED:
            return

        self.cellStateGrid[x, y] = Minesweeper.CELL_STATES.OPENED
        self.noOfUnopenedTiles -= 1
        if self.bombGrid[x, y] == 1:
            image = PhotoImage(file=os.path.join(self.imagesDirectoryPath, 'exploredBomb.png'))
            buttonConfig['image'] = image
            buttonConfig['bg'] = '#BEA57D'
            self.buttonGrid[x][y].image = image
            self.buttonGrid[x][y].config(buttonConfig)
            self.revealAllBombs()
            messagebox.showerror(title='You Lost', message='Better Luck Next Time')
            sys.exit(0)
        elif self.convolvedMatrix[x, y] != 0:
            image = PhotoImage(file=os.path.join(self.imagesDirectoryPath, 'explored.png'))
            buttonConfig['image'] = image
            self.buttonGrid[x][y].config(buttonConfig)
            buttonConfig['bg'] = '#BEA57D'
            self.buttonGrid[x][y].image = image
            buttonConfig['text'] = self.convolvedMatrix[x, y]
            self.buttonGrid[x][y].config(buttonConfig)
        elif self.convolvedMatrix[x, y] == 0:
            image = PhotoImage(file=os.path.join(self.imagesDirectoryPath, 'explored.png'))
            buttonConfig['image'] = image
            buttonConfig['state'] = tk.DISABLED
            buttonConfig['relief'] = tk.FLAT
            buttonConfig['bg'] = '#BEA57D'
            self.buttonGrid[x][y].image = image
            self.buttonGrid[x][y].config(buttonConfig)
            if x - 1 > -1:
                if self.bombGrid[x - 1, y] != 1 and self.cellStateGrid[x - 1, y] != Minesweeper.CELL_STATES.OPENED:
                    self.leftClick((x - 1, y))
            if y + 1 < self.gridSize:
                if self.bombGrid[x, y + 1] != 1 and self.cellStateGrid[x, y + 1] != Minesweeper.CELL_STATES.OPENED:
                    self.leftClick((x, y + 1))
            if x + 1 < self.gridSize:
                if self.bombGrid[x + 1, y] != 1 and self.cellStateGrid[x + 1, y] != Minesweeper.CELL_STATES.OPENED:
                    self.leftClick((x + 1, y))
            if y - 1 > -1:
                if self.bombGrid[x, y - 1] != 1 and self.cellStateGrid[x, y - 1] != Minesweeper.CELL_STATES.OPENED:
                    self.leftClick((x, y - 1))

        if self.noOfUnopenedTiles == 0:
            self.endTime = time.time()
            self.seconds = (self.endTime - self.startTime) % 60
            self.minutes = (self.endTime - self.startTime) / 60
            messagebox.showinfo(title='You Won', message='Keep up the streak. Time taken to solve is: {} minutes and {} seconds'.format(int(self.minutes), int(self.seconds)))
            sys.exit(0)

    def revealAllBombs(self):
        for i in range(0, self.gridSize):
            for j in range(0, self.gridSize):
                if self.bombGrid[i, j] == 1:
                    buttonConfig = {'bd': 7, 'width': 15, 'height': 15, 'font': ['Montserrat', 11, 'bold']}
                    image = PhotoImage(file=os.path.join(self.imagesDirectoryPath, 'exploredBomb.png'))
                    buttonConfig['image'] = image
                    buttonConfig['bg'] = '#BEA57D'
                    self.buttonGrid[i][j].image = image
                    self.buttonGrid[i][j].config(buttonConfig)

    def centraizeWindow(self, win):
        win.update_idletasks()
        width = win.winfo_width()
        height = win.winfo_height()
        x = (win.winfo_screenwidth() // 2) - (width // 2)
        y = (win.winfo_screenheight() // 2) - (height // 2)
        win.geometry('{}x{}+{}+{}'.format(width, height, x, y))


def printError(message):
    print(Fore.RED + 'Error: ' + Fore.LIGHTRED_EX + str(message) + Style.RESET_ALL)


parser = argparse.ArgumentParser(description='Play Light Minesweeper Anytime')
parser.add_argument('difficulty', default='medium', help='The options are: easy, medium, hard')
args = parser.parse_args()

if not args.difficulty:
    minesweeper = Minesweeper(16, 40)
else:
    difficulty = str(args.difficulty).lower()
    if difficulty == 'easy':
        minesweeper = Minesweeper(9, 10)
    # elif difficulty == 'medium':
    #     minesweeper = Minesweeper(16, 40)
    elif difficulty == 'hard':
        minesweeper = Minesweeper(24, 100)
    else:
        printError(message='Invalid Difficulty Level Option')
