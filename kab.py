from cocosCairo.cocosCairo import *

allConsonants = ['B', 'C', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', \
				'Qu', 'R', 'S', 'T', 'V', 'W', 'X', 'Y', 'Z']

allVowels = ['A', 'E', 'I', 'O', 'U']

def loadWordList():
	wordList = []
	f = open("words")
	for line in f:
		line = line.strip().lower()
		wordList.append(line)
	f.close()
	return wordList


class LetterNode(Node):
	def __init__(self, rect=None, letter=""):
		Node.__init__(self, rect)
		self._greyRect = RectangleNode(Rect(PointZero(), rect.size), fillColor=GreyColor())
		self.addChild(self._greyRect)
		self._label = Label(letter)
		self._label.setFontSize(18)
		self._label.setPosition(Point(self.getSize().width/2, self.getSize().height/2))
		self.addChild(self._label)

	def onModelChange(self, model):
		letter = model.getLetter()
		if len(letter) is 1 and ord(letter) >= 97 and ord(letter) <= 122:
			lookupString = letter + ".png"
		# add speciality tiles here
		self._label.setText(model.getLetter())

	def didPress(self):
		action = EaseOut(TintBy(0.1, 0.7, 0.7, 0.1))
		sequence = Sequence(action, action.reverse())
		self._greyRect.runAction(sequence)


class LetterModel(AbstractModel):
	def __init__(self, letter=""):
		AbstractModel.__init__(self)
		self._isInWordBuild = False
		self._letter = letter

	def getLetter(self):
		return self._letter

	def setLetter(self, letter):
		self._letter = letter

class LetterController(AbstractController):
	def __init__(self, letter="", callback=None):
		position = PointZero()
		size = Size(50,75)
		AbstractController.__init__(self, LetterNode(Rect(position,size), letter), LetterModel(letter))
		self._callback = callback
		#self.getNode().setRotation(angle)

	def onMousePress(self, event):
		if self.getNode().getRect().containsPoint(event.point):
			self.getNode().didPress()
			self._callback(self.getModel().getLetter())
			return True
		return False

	def onKeyPress(self, event):
		if event.key.lower() == self.getModel().getLetter().lower()[0]:	# for zero index for 'Qu'
			self.getNode().didPress()
			self._callback(self.getModel().getLetter())
			return True
		return False


import math
import random

class KabScene(Scene):
	def setup(self):
		self._wordList = loadWordList()
		self._letterControllers = []	# of the form [controller, [x_loc,y_loc]]
		self._word = ""
		global allConsonants
		global allVowels
		letters = [random.choice(allConsonants) for i in range(0,8)]
		letters.extend([random.choice(allVowels) for i in range(0,2)])
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
		self._word = self._word.lower()
		if self._word in self._wordList:
			print self._word, "YES"
		else:
			print self._word, "NO"



if __name__ == "__main__":
	director = Director()
	director.setWindow()
	director.runWithScene(KabScene())
