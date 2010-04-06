from cocosCairo.cocosCairo import *

import math

class PulseNode(Sprite):
	def __init__(self, position=None):
		Sprite.__init__(self, "images/pulse.png", position)
		self.setAnchorPoint(Point(0.5, 0.5))
		self.setScale(0.25)

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
		self.setSize(Size(length,1))
		self.setPosition(startPoint)
		self.setRotation(angle)
		self._length = length
		self._lineNode = LineNode(PointZero(), Point(length, 0.0), color)
		self.addChild(self._lineNode, 1)

	def getLineThickness(self):
		return self._lineNode.getThickness()

	def setLineThickness(self, thickness):
		self._lineNode.setThickness(thickness)

	def setColor(self, color):
		self._lineNode.setColor(color)

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
		#moveAction = EaseExponentialInOut(moveAction)
		moveAction = EaseSineInOut(moveAction)
		cbAction = CallbackInstantAction(lambda:self.getParent().removeChild(pulseNode))
		#cbAction = CallbackWithOwner(self._removePulseNode)
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
		self._titleLabel.setWrappingType("word-char")
		self._titleLabel.setFontWeight(1.0)
		self._titleLabel.setAnchorPoint(Point(0.5, 0.0))
		self._titleMargin = 10
		self._bodyLabel = PangoLabel()
		self._bodyLabel.setWrappingType("word-char")
		self._bodyLabel.setAnchorPoint(Point(0.5, 0.0))
		self._bodyMargin = 50
		if rect is None:
			point = PointZero()
			size = self._background.getSize()
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

	def getBodyMargin(self):
		return self._bodyMargin

	def setBodyMargin(self, margin):
		self._bodyMargin = margin
		self.dirty()

	def dirty(self):
		width = self.getSize().width
		x = width/2
		y = self._titleMargin
		self._titleLabel.setPosition(Point(x,y))
		self._titleLabel.setWidth(width)
		y += self._bodyMargin
		self._bodyLabel.setPosition(Point(x,y))
		self._bodyLabel.setWidth(width)

	def getTitleLabel(self):
		return self._titleLabel

	def getBodyLabel(self):
		return self._bodyLabel

	def setSize(self, size):
		Node.setSize(self, size)
		self._background.setSize(size)
		self.dirty()

	def onModelChange(self, model):
		self._titleLabel.setMarkupText(model.getTitleText())
		self._bodyLabel.setMarkupText(model.getBodyText())

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

	def getBodyText(self):
		return self._bodyText

	def setBodyText(self, bodyText):
		self._bodyText = bodyText
