import tkinter as tk
from tkinter import *
from generic.JsonConfigParser import ConfigParser
from PIL import ImageTk
import random

class Minesweeper:

    def __init__(self) -> None:

        self.configParser = ConfigParser()
        self.config = self.configParser.parse(configFilePath="D:\\Codes\\Python\\Minesweeper\\resources\\config.json")

        self.root = tk.Tk()
        self.root.title(self.config["title"])
        self.root.iconbitmap(self.config["imageFilePaths"]["icon"])

        self.gridSize = self.config["gridSize"]
        self.noOfBombs = self.config["noOfBombs"]
        self.noOfBombsLeft = self.noOfBombs
        self.noOfTilesLeft = self.gridSize ** 2 - self.noOfBombs
        self.surroundingDistance = self.config["surroundingDistance"]

        self.fontOption = 5

        self.genericLabelConfig = self.config["genericLabelConfig"]
        self.genericLabelConfig["font"] = (self.config["fonts"][self.fontOption], self.config["fontSizes"]["label"])

        self.leftLabel = tk.Label(self.root)
        self.leftLabelConfig = self.genericLabelConfig
        self.leftLabelConfig["text"] = "Number of Bombs Left: "
        self.leftLabel.config(self.leftLabelConfig)
        self.leftLabel.grid(row=0, column=0, padx=5, pady=5, sticky=E)

        self.rightLabel = tk.Label(self.root)
        self.rightLabelConfig = self.genericLabelConfig
        self.rightLabelConfig["text"] = str(self.noOfBombs)
        self.rightLabelText = StringVar()
        self.rightLabelText.set(self.noOfBombsLeft)
        self.rightLabelConfig["textvariable"] = self.rightLabelText
        self.rightLabel.config(self.rightLabelConfig)
        self.rightLabel.grid(row=0, column=1, padx=5, pady=5, sticky=W)

        self.frame = tk.Frame(self.root)
        self.frameConfig = self.config["frameConfig"]
        self.frame.config(self.frameConfig)
        self.frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        self.setupButtons()

        self.bombGrid = [[0] * self.gridSize for _ in range(0, self.gridSize)]
        self.setupBombs()
        self.setupNeighbours()
        for i in range(self.gridSize):
            print(self.bombGrid[i])

    def setupButtons(self):
        self.buttonGrid = [[None] * self.gridSize for _ in range(0, self.gridSize)]
        self.genericButtonConfig = self.config["genericButtonConfig"]
        for i in range(0, self.gridSize):
            for j in range(0, self.gridSize):
                self.buttonGrid[i][j] = self.makeButton(i, j)
                self.buttonGrid[i][j].grid(row=i + 1, column=j)

    def displayResult(self, type = False):

        for i in range(self.gridSize):
            for j in range(self.gridSize):
                buttonConfig = self.genericButtonConfig
                if self.bombGrid[i][j] == -1:
                    image = ImageTk.PhotoImage(file=self.config["imageFilePaths"]["unexploredBomb"])
                    buttonConfig["image"] = image
                    buttonConfig["text"] = " "
                    buttonConfig["relief"] = tk.SUNKEN
                    buttonConfig["cursor"] = "target"
                    buttonConfig["state"] = tk.DISABLED
                    buttonConfig["font"] = (self.config["fonts"][self.fontOption], self.config["fontSizes"]["button"])
                    self.buttonGrid[i][j].config(buttonConfig)
                    self.buttonGrid[i][j].image = image

        resultScreen = tk.Tk()
        self.centerWindow(resultScreen)
        resultScreen.geometry('{}x{}'.format(300, 400))
        # resultScreen.resizable(width=False, height=False)
        resultScreen.iconbitmap(self.config["imageFilePaths"]["icon"])

        resultScreen.title("Game Over!")

        resultMessage = tk.Label(resultScreen)
        resultMessageConfig = self.config["resultMessageConfig"]
        if not type:
            resultMessageConfig["text"] = "You Lost!"
            resultMessageConfig["fg"] = "#000000"
        else:
            resultMessageConfig["text"] = "You Won!"
            resultMessageConfig["fg"] = self.config["colors"]["unexplored"]
        resultMessageConfig["font"] = (self.config["fonts"][self.fontOption], self.config["fontSizes"]["resultLabel"])
        resultMessage.config(resultMessageConfig)

        resultButton = tk.Button(resultScreen, command=lambda : exit(1))
        resultButtonConfig = self.config["resultButtonConfig"]
        resultButtonConfig["font"] = (self.config["fonts"][self.fontOption], self.config["fontSizes"]["resultButton"])
        resultButton.config(resultButtonConfig)
        resultMessage.pack()
        resultButton.pack()
        resultScreen.mainloop()

    def rightClick(self, event, arg):
        x = arg[0]
        y = arg[1]
        buttonConfig = self.genericButtonConfig
        if self.buttonGrid[x][y]["relief"] == tk.RAISED:
            image = ImageTk.PhotoImage(file=self.config["imageFilePaths"]["unexploredFlag"])
            buttonConfig["image"] = image
            buttonConfig["text"] = " "
            buttonConfig["bg"] = self.config["colors"]["flag"]
            buttonConfig["relief"] = tk.SUNKEN
            buttonConfig["cursor"] = "target"
            buttonConfig["state"] = tk.NORMAL
            buttonConfig["font"] = (self.config["fonts"][self.fontOption], self.config["fontSizes"]["button"])
            self.buttonGrid[x][y].image = image
            self.noOfBombsLeft -= 1
            self.rightLabelText.set(self.noOfBombsLeft)
        else:
            image = ImageTk.PhotoImage(file=self.config["imageFilePaths"]["unexplored"])
            buttonConfig["image"] = image
            buttonConfig["text"] = " "
            buttonConfig["bg"] = self.config["colors"]["unexplored"]
            buttonConfig["relief"] = tk.RAISED
            buttonConfig["cursor"] = "circle"
            buttonConfig["state"] = tk.NORMAL
            buttonConfig["font"] = (self.config["fonts"][self.fontOption], self.config["fontSizes"]["button"])
            self.buttonGrid[x][y].image = image
            self.noOfBombsLeft += 1
            self.rightLabelText.set(self.noOfBombsLeft)
        self.buttonGrid[x][y].config(buttonConfig)

    def leftClick(self, x, y):
        buttonConfig = self.genericButtonConfig

        if self.bombGrid[x][y] == -1:
            image = ImageTk.PhotoImage(file=self.config["imageFilePaths"]["exploredBomb"])
            buttonConfig["image"] = image
            buttonConfig["text"] = " "
            buttonConfig["bg"] = self.config["colors"]["explored"]
            buttonConfig["relief"] = tk.SUNKEN
            buttonConfig["cursor"] = "x_cursor"
            buttonConfig["font"] = (self.config["fonts"][self.fontOption], self.config["fontSizes"]["button"])
            buttonConfig["state"] = DISABLED
            self.buttonGrid[x][y].image = image
            self.buttonGrid[x][y].config(buttonConfig)
            self.displayResult(type=False)

        elif self.bombGrid[x][y] > 0 and self.buttonGrid[x][y]["relief"] == tk.RAISED:
            image = ImageTk.PhotoImage(file=self.config["imageFilePaths"]["explored"])
            buttonConfig["image"] = image
            buttonConfig["text"] = self.bombGrid[x][y]
            buttonConfig["bg"] = self.config["colors"]["explored"]
            buttonConfig["relief"] = tk.SUNKEN
            buttonConfig["cursor"] = "x_cursor"
            buttonConfig["font"] = (self.config["fonts"][self.fontOption], self.config["fontSizes"]["button"])
            buttonConfig["state"] = ACTIVE
            self.buttonGrid[x][y].image = image
            self.buttonGrid[x][y].config(buttonConfig)
            self.noOfTilesLeft -= 1
            if self.noOfTilesLeft == 0:
                self.displayResult(type=True)

        elif self.bombGrid[x][y] == 0 and self.buttonGrid[x][y]["relief"] == tk.RAISED:
            image = ImageTk.PhotoImage(file=self.config["imageFilePaths"]["explored"])
            buttonConfig["image"] = image
            buttonConfig["text"] = " "
            buttonConfig["bg"] = self.config["colors"]["explored"]
            buttonConfig["relief"] = tk.SUNKEN
            buttonConfig["cursor"] = "x_cursor"
            buttonConfig["font"] = (self.config["fonts"][self.fontOption], self.config["fontSizes"]["button"])
            buttonConfig["state"] = DISABLED
            self.buttonGrid[x][y].image = image
            self.buttonGrid[x][y].config(buttonConfig)
            if x-1 > -1:
                if self.bombGrid[x-1][y] >= 0 and self.buttonGrid[x-1][y]["relief"] == tk.RAISED:
                    self.leftClick(x - 1, y)
            if y+1 < self.gridSize:
                if self.bombGrid[x][y+1] >= 0 and self.buttonGrid[x][y+1]["relief"] == tk.RAISED:
                    self.leftClick(x, y + 1)
            if x+1 < self.gridSize:
                if self.bombGrid[x+1][y] >= 0 and self.buttonGrid[x+1][y]["relief"] == tk.RAISED:
                    self.leftClick(x + 1, y)
            if y-1 > -1:
                if self.bombGrid[x][y-1] >= 0 and self.buttonGrid[x][y-1]["relief"] == tk.RAISED:
                    self.leftClick(x, y - 1)
            self.noOfTilesLeft -= 1
            if self.noOfTilesLeft == 0:
                self.displayResult(type=True)

    def makeButton(self, i, j):
        button = tk.Button(self.frame, command= lambda: self.leftClick(i, j))
        image = ImageTk.PhotoImage(file = self.config["imageFilePaths"]["unexplored"])
        buttonConfig = self.genericButtonConfig
        buttonConfig["bg"] = self.config["colors"]["unexplored"]
        buttonConfig["image"] = image
        buttonConfig["cursor"] = "circle"
        button.config(buttonConfig)
        data = (i, j)
        button.bind("<Button-3>", lambda event, arg=data: self.rightClick(event, arg))
        button.image = image
        return button

    def getRandomCell(self):
        x = random.randint(0, self.gridSize - 1)
        y = random.randint(0, self.gridSize - 1)
        return (x, y)

    def getSurroundingCells(self, x, y):
        surroundingCells = []

        i = x - self.surroundingDistance
        j = y - self.surroundingDistance

        for j in range(y - self.surroundingDistance, y + self.surroundingDistance):
            if i > -1 and i < self.gridSize and j > -1 and j < self.gridSize:
                surroundingCells.append((i, j))
        j += 1

        for i in range(x - self.surroundingDistance, x + self.surroundingDistance):
            if i > -1 and i < self.gridSize and j > -1 and j < self.gridSize:
                surroundingCells.append((i, j))
        i += 1

        for j in range(y + self.surroundingDistance, y - self.surroundingDistance, -1):
            if i > -1 and i < self.gridSize and j > -1 and j < self.gridSize:
                surroundingCells.append((i, j))
        j -= 1

        for i in range(x + self.surroundingDistance, x - self.surroundingDistance, -1):
            if i > -1 and i < self.gridSize and j > -1 and j < self.gridSize:
                surroundingCells.append((i, j))
        i -= 1

        return surroundingCells

    def setupBombs(self):
        for i in range(0, self.noOfBombs):
            while True:
                (x, y) = self.getRandomCell()
                if self.bombGrid[x][y] == 0:
                    self.bombGrid[x][y] = -1
                    break

    def setupNeighbours(self):
        for i in range(self.gridSize):
            for j in range(self.gridSize):
                if self.bombGrid[i][j] == 0:
                    surroundingCells = self.getSurroundingCells(i, j)
                    for surroundingCell in surroundingCells:
                        if self.bombGrid[surroundingCell[0]][surroundingCell[1]] == -1:
                            self.bombGrid[i][j] += 1

    def centerWindow(self, win):
        win.update_idletasks()
        width = win.winfo_width()
        height = win.winfo_height()
        x = (win.winfo_screenwidth() // 2) - (width // 2)
        y = (win.winfo_screenheight() // 2) - (height // 2)
        win.geometry('{}x{}+{}+{}'.format(width, height, x, y))

minesweeper = Minesweeper()
minesweeper.root.resizable(width=False, height=False)
minesweeper.centerWindow(minesweeper.root)
minesweeper.root.mainloop()