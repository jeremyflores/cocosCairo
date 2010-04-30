from cocosCairo.cocosCairo import *

import math

class PulseNode(Sprite):
	def __init__(self, position=None):
		Sprite.__init__(self, "images/pulse.png", position)
		self.anchorPoint = Point(0.5, 0.5)
		self.scale = 0.25

	def onEnter(self):
		Sprite.onEnter(self)
		action = TintBy(0.5, 1.0, 1.0, 1.0, 1.0)
		action = EaseSineInOut(action)
		sequence = Sequence(action, action.reverse())
		repeatForever = RepeatForever(sequence)
		self.runAction(repeatForever)

class ConnectionNode(Node):
	def __init__(self, startPoint, endPoint, color=None):
		Node.__init__(self)
		if color is None:
			color = WhiteColor()
		length = pointDistance(startPoint, endPoint)
		self._startPoint = startPoint
		self._endPoint = endPoint
		angle = math.atan2((endPoint.y-startPoint.y),(endPoint.x-startPoint.x))
		self.size = Size(length,1)
		self.position = startPoint
		self.rotation = angle
		self._length = length
		self._lineNode = LineNode(PointZero(), Point(length, 0.0), color)
		self.addChild(self._lineNode, 1)

	def getLineThickness(self):
		return self._lineNode.thickness

	def setLineThickness(self, thickness):
		self._lineNode.thickness = thickness

	lineThickness = property(getLineThickness, setLineThickness)

	def getColor(self):
		return self._lineNode.color

	def setColor(self, color):
		self._lineNode.color = color

	color = property(getColor, setColor)

	def setColors(self, r, g, b, a=1.0):
		self._lineNode.setColors(r, g, b, a)

	def sendPulse(self, fromBeginning=True, duration=0.75, callback=None, data=None):
		if fromBeginning:
			startPoint = self._startPoint
			movePoint = self._endPoint
		else:
			startPoint = self._endPoint
			movePoint = self._startPoint
		pulseNode = PulseNode(startPoint)
		pulseNode.setRotation(self.getRotation())
		pulseNode.setOpacity(0.0)
		self.getParent().addChild(pulseNode, 2)	# parent the pulse node to the parent in case there are nearby ConnectionNodes: otherwise, the z-ordering will cause one of the pulse nodes to render beneath the other ConnectionNode's line node
		fadeInAction = FadeIn(duration/3)
		moveAction = MoveTo(duration/3, movePoint)
		moveAction = EaseSineInOut(moveAction)
		cbAction = CallbackInstantAction(lambda:self.parent.removeChild(pulseNode))
		if callback is not None:
			cbAction2 = CallbackWithOwnerAndData(callback, data)
			sequence = Sequence(fadeInAction, moveAction, fadeInAction.reverse(), cbAction, cbAction2)
		else:
			sequence = Sequence(fadeInAction, moveAction, fadeInAction.reverse(), cbAction)
		pulseNode.runAction(sequence)

	def _removePulseNode(self, node):
		self.getParent().removeChild(node)

class SystemBlockNode(Node):
	def __init__(self, rect=None):
		self._background = SVGSprite("images/system_block.svg")
		self._titleLabel = PangoLabel()
		self._titleLabel.wrappingType = "word-char"
		self._titleLabel.fontWeight = 1.0
		self._titleLabel.anchorPoint = Point(0.5, 0.0)
		self._titleMargin = 10
		self._bodyLabel = PangoLabel()
		self._bodyLabel.wrappingType = "word-char"
		self._bodyLabel.anchorPoint = Point(0.5, 0.0)
		self._bodyMargin = 50
		if rect is None:
			point = PointZero()
			size = self._background.size
			rect = Rect(point, size)
		Node.__init__(self, rect)
		self.addChild(self._background, 1)
		self.addChild(self._titleLabel, 2)
		self.addChild(self._bodyLabel, 2)

	def getTitleMargin(self):
		return self._titleMargin

	def setTitleMargin(self, margin):
		self._titleMargin = margin
		self.dirty()

	titleMargin = property(getTitleMargin, setTitleMargin)

	def getBodyMargin(self):
		return self._bodyMargin

	def setBodyMargin(self, margin):
		self._bodyMargin = margin
		self.dirty()

	bodyMargin = property(getBodyMargin, setBodyMargin)

	def dirty(self):
		width = self.size.width
		x = width/2
		y = self._titleMargin
		self._titleLabel.position = Point(x,y)
		self._titleLabel.width = width
		y += self._bodyMargin
		self._bodyLabel.position = Point(x,y)
		self._bodyLabel.width = width

	def getTitleLabel(self):
		return self._titleLabel

	titleLabel = property(getTitleLabel)

	def getBodyLabel(self):
		return self._bodyLabel

	bodyLabel = property(getBodyLabel)

	def setSize(self, size):
		Node.setSize(self, size)
		self._background.size = size
		self.dirty()

	size = property(Node.getSize, setSize)

	def onModelChange(self, model):
		self._titleLabel.markupText = model.titleText
		self._bodyLabel.markupText = model.bodyText

class SystemBlockController(AbstractController):
	def __init__(self, node=None, model=None):
		if node is None:
			node = SystemBlockNode()
		if model is None:
			model = SystemBlockModel()
		AbstractController.__init__(self, node, model)

class SystemBlockModel(AbstractModel):
	def __init__(self, titleText='', bodyText=''):
		AbstractModel.__init__(self)
		self._titleText = titleText
		self._bodyText = bodyText

	def getTitleText(self):
		return self._titleText

	def setTitleText(self, titleText):
		self._titleText = titleText
		self.didChange()

	titleText = property(getTitleText, setTitleText)

	def getBodyText(self):
		return self._bodyText

	def setBodyText(self, bodyText):
		self._bodyText = bodyText

	bodyText = property(getBodyText, setBodyText)
