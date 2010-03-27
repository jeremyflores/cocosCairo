from cocosCairo.cocosCairo import *

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
