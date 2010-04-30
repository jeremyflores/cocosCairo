from cocosCairo.cocosCairo import *
import cocosCairo.EaseAction

import math

import inspect

easeClasses = []

class Linear(AbstractEaseAction):
	def update(self, time):
		self._action.update(time)

easeClasses.append(["Linear (default)", Linear])

for name, obj in inspect.getmembers(cocosCairo.EaseAction):
	if inspect.isclass(obj) and \
		(AbstractEaseAction in obj.__bases__ or \
		AbstractEaseRateAction in obj.__bases__ or\
		AbstractEaseBounce in obj.__bases__):
		if name[:8] == "Abstract":	# don't care about the abstract ones
			continue
		easeClasses.append([name,obj])


class GraphNode(Node):
	def __init__(self, rect=None, color=None, axisColor=None, lineThickness=2.0):
		Node.__init__(self, rect)
		if color is None:
			color = WhiteColor()
		if axisColor is None:
			axisColor = Color(0.5, 0.5, 0.5)
		self.color = color
		self._axisColor = axisColor
		self._table = []
		self._pointNodes = []
		self._radius = 2
		self._pointChangeDuration = 0.75
		self._graphName = ""
		self._label = Label()
		self._label.setFontSize(14)
		self._label.setOpacity(0.0)
		self.addChild(self._label)
		self._startingLabelPosition = Point(0,0)
		self._label.position = self._startingLabelPosition
		width = self.size.width
		height = self.size.height
		for i in range(0, int(width/self._radius/2)):
			x = i*4
			y = height
			point = Point(x,y)
			self._pointNodes.append(PointNode(point, Color(1.0, 1.0, 1.0), self._radius))
		for node in self._pointNodes:
			self.addChild(node, 3)
		self._lineThickness = lineThickness

	def getGraphName(self):
		return self._graphName

	def setGraphName(self, name):
		self._graphName = name

	graphName = property(getGraphName, setGraphName)

	def clearTable(self):
		self._table = []

	def getTable(self):
		return self._table

	table = property(getTable)

	def onEnterFromFinishedTransition(self):
		Node.onEnterFromFinishedTransition(self)
		self.updatePointNodes()

	def updatePointNodes(self):
		if len(self._table) > 0:
			for node in self._pointNodes:
				node.stopActionByTag("move")
			self.startFloatUpExitSequence()
			width = self.size.width
			height = self.size.height
			for i in range(0, int(width/self._radius/2)):
				x = i*4
				y = -self._table[i*len(self._table)/width*self._radius*2]*height
				y += height
				action = EaseExponentialInOut(MoveTo(self._pointChangeDuration, Point(x,y)))
				action.tag = "move"
				node = self._pointNodes[i]
				node.runAction(action)

	def didFinishPopulatingTable(self):
		self.updatePointNodes()

	def startFloatUpEnterSequence(self):
		# for the label / graph's title
		self._label.stopAllActions()
		self._label.opacity = 0.0
		self._label.text = self._graphName
		self._label.position = self._startingLabelPosition
		x = self._label.position.x
		y = self._label.position.y
		duration = self._pointChangeDuration
		action1 = FadeIn(duration*3/4)
		action2 = EaseSineOut(MoveBy(duration*3/4, Point(0, -25)))
		spawn = Spawn(action1,action2)
		self._label.runAction(spawn)

	def startFloatUpExitSequence(self):
		# for the label / graph's title
		duration = self._pointChangeDuration
		action1 = FadeOut(duration*1/4)
		action2 = EaseSineIn(MoveBy(duration*1/4, Point(0, -25)))
		spawn = Spawn(action1,action2)
		cbAction = CallbackInstantAction(self.startFloatUpEnterSequence)
		sequence = Sequence(spawn, cbAction)
		self._label.runAction(sequence)


	def draw(self, context):
		# draws the axes and the grid
		width = self.size.width
		height = self.size.height
		color = self._axisColor
		context.set_line_width(self._lineThickness)
		context.set_source_rgba(color.r, color.g, color.b, color.a)
		context.move_to(0, height)
		context.line_to(width, height)
		context.stroke()
		context.move_to(0, 0)
		context.line_to(0, height)
		context.stroke()
		context.set_line_width(2.0)
		context.set_source_rgba(color.r/2., color.g/2., color.b/2., color.a/2)
		for i in range(1, 10):
			context.move_to(0, height*i/10.)
			context.line_to(width, height*i/10.)
			context.stroke()
			context.move_to(width*i/10., 0)
			context.line_to(width*i/10., height)
			context.stroke()


class TableAction(AbstractIntervalAction):
	def __init__(self, duration):
		AbstractIntervalAction.__init__(self, duration)

	def start(self, owner):
		self.owner = owner
		self.owner.clearTable()

	def update(self, dt):
		self.owner.table.append(dt)

	def stop(self):
		self.owner.didFinishPopulatingTable()
		AbstractIntervalAction.stop(self)


class TrackedAction(AbstractIntervalAction):
	def __init__(self, duration, callback):
		AbstractIntervalAction.__init__(self, duration)
		self._callback = callback

	def update(self, dt):
		self._callback(dt)

class GraphScene(Scene,GestureListener):
	def setup(self):
		self._graphNode = GraphNode(MakeRect(self.getSize().width/2,self.getSize().height/2, 400, 200), axisColor=Color(0.3, 0.3, 0.7))
		self._graphNode.anchorPoint = Point(0.5,0.5)
		self.addChild(self._graphNode)
		self._currentIndex = 0
		self._leftArrow = SVGSprite("images/left_button.svg")
		self._leftArrow.rotation = math.pi
		self._leftArrow.anchorPoint = Point(0.5,0.5)
		self._leftArrow.position = Point(self.size.width/2+125, self.size.height/2+160)
		self.addChild(self._leftArrow)
		self._rightArrow = SVGSprite("images/right_button.svg")
		self._rightArrow.anchorPoint = Point(0.5,0.5)
		self._rightArrow.position = Point(self.size.width/2+175, self.size.height/2+160)
		self.addChild(self._rightArrow)
		self._ball = Sprite("images/goal.png")
		self._ball.anchorPoint = Point(0.5,1.0)
		self._ballStartingPosition = Point(100, 575)
		self._ball.position = self._ballStartingPosition
		self.addChild(self._ball)

	def setCurrentIndex(self, index):
		self._currentIndex = (index % len(easeClasses))
		for pointNode in self._graphNode._pointNodes:
			pointNode.color = WhiteColor()
		self._ball.stopAllActions()
		self._ball.position = self._ballStartingPosition
		easeList = easeClasses[self._currentIndex]
		easeName = easeList[0]
		EaseClass = easeList[1]
		self._graphNode.graphName = easeName
		action = EaseClass(TableAction(1.0))
		action.start(self._graphNode)
		for i in range(0,1000):
			action.step(0.001)
		action.stop()
		duration = 2.0
		action = EaseClass(MoveTo(duration, Point(700, 575)))
		trackedAction = TrackedAction(duration, self._onUpdate)
		spawn = Spawn(action, trackedAction)
		cbAction = CallbackInstantAction(lambda:self._ball.setPosition(self._ballStartingPosition))
		sequence = Sequence(spawn, DelayTime(duration/4.), cbAction)
		self._ball.runAction(RepeatForever(sequence))

	def _onUpdate(self, percentComplete):
		pointNodes = self._graphNode._pointNodes
		for pointNode in pointNodes:
			pointNode.color = WhiteColor()
			pointNode.scale = 1.0
		index = int(len(pointNodes)*percentComplete)-1
		pointNode = pointNodes[index]
		pointNode.color = YellowColor()
		pointNode.scale = 2.0

	def onMousePress(self, event):
		if self._leftArrow.rect.containsPoint(event.point):
			self.setCurrentIndex(self._currentIndex-1)
		elif self._rightArrow.rect.containsPoint(event.point):
			self.setCurrentIndex(self._currentIndex+1)

	def onKeyPress(self, event):
		if event.key == "Left":
			self.setCurrentIndex(self._currentIndex-1)
		elif event.key == "Right":
			self.setCurrentIndex(self._currentIndex+1)

	def onEnter(self):
		Scene.onEnter(self)
		self.director.gestureDispatch.addListener(self)
		self.setCurrentIndex(0)

	def onExit(self):
		self.director.gestureDispatch.removeListener(self)


if __name__ == "__main__":
	director = Director()
	director.showingFPS = True
	director.runWithScene(GraphScene())
