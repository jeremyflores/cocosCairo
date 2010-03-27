from cocosCairo.cocosCairo import *
from Letter import *

allConsonants = ['B', 'C', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', \
				'Qu', 'R', 'S', 'T', 'V', 'W', 'X', 'Y', 'Z']

allVowels = ['A', 'E', 'I', 'O', 'U']

valueDictionary = { \
'A': 1, \
'B': 2, \
'C': 3, \
'D': 1, \
'E': 1, \
'F': 3, \
'G': 2, \
'H': 4, \
'I': 1, \
'J': 6, \
'K': 6, \
'L': 1, \
'M': 1, \
'N': 1, \
'O': 1, \
'P': 2, \
'Qu': 6, \
'R': 1, \
'S': 1, \
'T': 1, \
'U': 1, \
'V': 3, \
'W': 5, \
'X': 8, \
'Y': 1, \
'Z': 7, \
}

def loadWordList():
	wordList = []
	f = open("american-english-large")
	for line in f:
		line = line.strip().lower()
		wordList.append(line)
	f.close()
	return wordList





import math
import random

class PlayerInformation:
	def __init__(self):
		self.totalScore = 0
		self.items = [] 
		self.achievements = []
		self.currentLevel = 1
		self.consonantCount = 6
		self.vowelCount = 1

class LevelInformation:
	def __init__(self):
		self.currentScore = 0
		self.achievements = []
		self.bonusScore = 0
		self.usedWords = []
		self.startingLevel = 1



class GameplayScene(Scene):
	def setup(self):
		self._wordList = loadWordList()
		self._letterControllers = []	# of the form [controller, [x_loc,y_loc]]
		self._word = ""
		self._currentWordScores = []
		global allConsonants
		global allVowels
		letters = []
		for i in range(0,8):
			letter = random.choice(allConsonants)
			while letter in letters:
				letter = random.choice(allConsonants)
			letters.append(letter)
		for i in range(0,2):
			letter = random.choice(allVowels)
			while letter in letters:
				letter = random.choice(allVowels)
			letters.append(letter)
		for letter in letters:
			controller = LetterController(letter, self._onLetterPress)
			self.addLetterController(controller)

	def addLetterController(self, controller):
		angle = random.uniform(-math.pi/12, math.pi/12)
		controller.getNode().setRotation(angle)
		controller.getNode().setAnchorPoint(Point(0.5,0.5))
		width = self.getSize().width
		height = 200
		nodeWidth = controller.getNode().getSize().width
		nodeHeight = controller.getNode().getSize().height
		numX = int(width/nodeWidth)
		numY = int(height/nodeHeight)
		locations = [x[1] for x in self._letterControllers]
		if len(locations) >= numX*numY:	# if the slots are all full
			return
		location = [random.randint(0, numX-1), random.randint(0, numY-1)]
		while location in locations:
			location = [random.randint(0, numX-1), random.randint(0, numY-1)]
		position = Point(location[0]*nodeWidth+nodeWidth/2, location[1]*nodeHeight+nodeHeight/2)
		controller.getNode().setPosition(position)
		if controller not in self._letterControllers:
			self._letterControllers.append([controller, location])
			self.addController(controller)

	def _onLetterPress(self, letter):
		self._word += letter
		self._currentWordScores.append(valueDictionary[letter])
		total = 0
		for score in self._currentWordScores:
			total += score
		self._word = self._word.lower()
		if self._word in self._wordList:
			print self._word, "YES", total
		else:
			print self._word, "NO"



if __name__ == "__main__":
	director = Director()
	director.setWindow()
	director.runWithScene(GameplayScene())
