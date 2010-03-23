from cocosCairo.cocosCairo import *
from SystemBlock import *

import math

class ActionScene(Scene):
	def __init__(self):
		Scene.__init__(self)
		self._connectionNodes = {}
		self._cbRate = 1.0	# between 0.14 and 1.0
		self._count = 0

	def addConnectionNode(self, node, data=None):
		self._connectionNodes[node] = data
		self.addChild(node, 2)

	def removeConnectionNode(self, node):
		if node in self._connectionNodes:
			del self._connectionNodes[node]
			self.removeChild(node)

	def fireConnectionNodes(self, dt=0.0):
		for node in self._connectionNodes:
			nodeCallback = self._connectionNodes[node]
			node.sendPulse(duration=self._cbRate*3/4, callback=nodeCallback)
		self.setIntervalForScheduledCallback(self.fireConnectionNodes, self._cbRate)

	def setup(self):
		actionManagerNode = SystemBlockNode()
		actionManagerNode.setAnchorPoint(Point(0.5,0.5))
		x = self.getSize().width/2
		y = self.getSize().height/2
		actionManagerNode.setPosition(Point(x,y))
		actionManagerNode.setSize(Size(200,150))
		title = '<span foreground="#FFFFFF">ActionManager</span>'
		bullet = '<span foreground="#FFFFFF" size="xx-large">&#183; </span>'
		body = 	bullet + \
				'<span foreground="#FFFFFF" size="small">Updates each running <span face="monospace">Action</span></span>' + \
				'\n' + bullet + \
				'<span foreground="#FFFFFF" size="small">Ticked by the <span face="monospace">Scheduler</span></span>'
		actionManagerModel = SystemBlockModel(title, body)
		actionManagerController = SystemBlockController(actionManagerNode, actionManagerModel)
		self.addController(actionManagerController)
		width = actionManagerNode.getRect().size.width
		height = actionManagerNode.getRect().size.height
		oldX = x
		oldY = y

		self.scheduleCallback(self.fireConnectionNodes, self._cbRate)

		# set up the middle-right node
		x = oldX+width/2+100
		y = oldY
		actionOwner = Sprite("images/goal.png", Point(50,50))
		actionOwner.setAnchorPoint(Point(0.5,1.0))
		actionOwner.setScale(0.75)
		action = MoveBy(1.0, Point(0,54))
		action = RepeatForever(Sequence(EaseBounceOut(action), action.reverse()))
		node = IntervalActionNode(actionOwner, action, Point(x,y))
		node.setAnchorPoint(Point(0.0, 0.5))
		self.addChild(node, 0)
		connectionNode = ConnectionNode(Point(x-100,y), Point(x,y), Color(0.1, 0.1, 0.5))
		self.addConnectionNode(connectionNode, data=node.update)

		# set up the middle-left node
		x = oldX-width-100
		actionOwner = Sprite("images/goal.png", Point(50,50))
		actionOwner.setAnchorPoint(Point(0.5,0.5))
		action = EaseSineInOut(ScaleBy(1.0, 0.5))
		action = RepeatForever(Sequence(action, action.reverse()))
		node = IntervalActionNode(actionOwner, action, Point(x,y))
		node.setAnchorPoint(Point(0.0, 0.5))
		self.addChild(node, 0)
		connectionNode = ConnectionNode(Point(x+200,y), Point(x+100,y), Color(0.1, 0.1, 0.5))
		self.addConnectionNode(connectionNode, data=node.update)

		# set up the middle-top node
		x = oldX
		y = oldY-height/2-50
		actionOwner = Sprite("images/goal.png", Point(50,50))
		actionOwner.setAnchorPoint(Point(0.5,0.5))
		action = EaseSineInOut(TintBy(1.0, 1.0, 1.0, 1.0, 1.0))
		action = RepeatForever(Sequence(action, action.reverse()))
		node = IntervalActionNode(actionOwner, action, Point(x,y))
		node.setAnchorPoint(Point(0.5, 1.0))
		self.addChild(node, 0)
		connectionNode = ConnectionNode(Point(x, y+50), Point(x,y), Color(0.1, 0.1, 0.5))
		self.addConnectionNode(connectionNode, data=node.update)

		# set up the middle-bottom node
		y = oldY+height/2+50
		actionOwner = Sprite("images/goal.png", Point(50,50))
		actionOwner.setAnchorPoint(Point(0.5,0.5))
		action = FadeOut(1.0)
		action = RepeatForever(Sequence(action, action.reverse()))
		node = IntervalActionNode(actionOwner, action, Point(x, y))
		node.setAnchorPoint(Point(0.5, 0.0))
		self.addChild(node, 0)
		connectionNode = ConnectionNode(Point(x, y-50), Point(x,y), Color(0.1, 0.1, 0.5))
		self.addConnectionNode(connectionNode, data=node.update)

	def onExit(self):
		Scene.onExit(self)
		self.unscheduleCallback(self._fire)


class IntervalActionNode(Node):
	def __init__(self, actionOwner, action, position=None, stepSize=0.05):
		Node.__init__(self)
		if position is None:
			position = PointZero()
		self.setPosition(position)
		self.setSize(Size(100,100))
		backgroundNode = SVGSprite("images/system_block.svg")
		self.addChild(backgroundNode, -1)
		self._actionOwner = actionOwner
		self.addChild(self._actionOwner)
		self._action = action
		self._stepSize = stepSize

	def update(self, owner, data):
		self._action.step(self._stepSize)

	def onEnter(self):
		Node.onEnter(self)
		self._action.start(self._actionOwner)



class RedrawScene(Scene):
	def setup(self):
		self._cbRate = 1.0
		self._counter = 0
		self._connectionNodes = {}
		self._displayNode = Node(MakeRect(self.getSize().width/2, self.getSize().height-10, 200, 200))
		rectangleNode = RectangleNode(Rect(PointZero(), self._displayNode.getSize()), strokeColor=WhiteColor(), strokeThickness=2.0)
		self._displayNode.addChild(rectangleNode, -1)
		self._displayNode.setAnchorPoint(Point(0.5, 1.0))
		self.addChild(self._displayNode)
		length = 50

		self.scheduleCallback(self._callback, self._cbRate)

		playButton = PlayButton(Point(self.getSize().width*1/6, self.getSize().height*5/6))
		playButton.setAnchorPoint(Point(0.5,0.5))
		self.addChild(playButton)

		bullet = '<span foreground="#FFFFFF" size="xx-large">&#183; </span>'
		makeTitle = lambda string: '<span foreground="#FFFFFF">' + string + '</span>'
		makeBody = lambda string: bullet + '<span foreground="#FFFFFF" size="small">' + string + '</span>'

		sceneNode = SystemBlockNode()
		sceneNode.setAnchorPoint(Point(0.5,0.0))
		x = self.getSize().width/2
		y = 10
		title = makeTitle('Scene')
		body = 	makeBody('Has <span face="monospace">Node</span> children redrawn according to their z-orders.')
		controller = self.makeController(Point(x,y), title, body, Size(200,100))
		self.addController(controller)

		oldX = x
		oldY = y + sceneNode.getSize().height
		y += controller.getNode().getSize().height + length

		x = self.getSize().width*1/4
		title = makeTitle('Node')
		body = 	makeBody('<span face="monospace">z-order=1</span>')
		controller = self.makeController(Point(x,y), title, body, Size(100, 75))
		self.addController(controller)
		node = RectangleNode(MakeRect(40,70,80,80), Color(0.6, 0.2, 0.2))
		connectionNode = ConnectionNode(Point(oldX,oldY), Point(x,y), Color(0.1,0.1,0.5))
		self.addConnectionNode(connectionNode, 0, node, 1)
		node1 = node

		x = self.getSize().width*2/4
		title = makeTitle('Node')
		body = 	makeBody('<span face="monospace">z-order=2</span>')
		controller = self.makeController(Point(x,y), title, body, Size(100, 75))
		self.addController(controller)
		node = RectangleNode(MakeRect(70,90,40,50), GreenColor())
		connectionNode = ConnectionNode(Point(oldX,oldY), Point(x,y), Color(0.1,0.1,0.5))
		self.addConnectionNode(connectionNode, 3, node, 2)
		node2 = node

		x = self.getSize().width*3/4
		title = makeTitle('Node')
		body = 	makeBody('<span face="monospace">z-order=-1</span>')
		controller = self.makeController(Point(x,y), title, body, Size(100, 75))
		self.addController(controller)
		node = RectangleNode(MakeRect(10,100,150,80), Color(1.0, 0.0, 1.0))
		connectionNode = ConnectionNode(Point(oldX,oldY), Point(x,y), Color(0.1,0.1,0.5))
		self.addConnectionNode(connectionNode, 6, node, -1)
		node3 = node

		oldX = self.getSize().width*1/4
		oldY = y + controller.getNode().getSize().height
		y += controller.getNode().getSize().height + length

		x = self.getSize().width*1/7
		title = makeTitle('Node')
		body = 	makeBody('<span face="monospace">z-order=3</span>')
		controller = self.makeController(Point(x,y), title, body, Size(100, 75))
		self.addController(controller)
		node = RectangleNode(MakeRect(35,20,10,100), Color(0.2, 0.4, 0.6))
		connectionNode = ConnectionNode(Point(oldX,oldY), Point(x,y), Color(0.1,0.1,0.5))
		self.addConnectionNode(connectionNode, 1, node, 3, node1)

		x = self.getSize().width*2/7
		title = makeTitle('Node')
		body = 	makeBody('<span face="monospace">z-order=2</span>')
		controller = self.makeController(Point(x,y), title, body, Size(100, 75))
		self.addController(controller)
		node = RectangleNode(MakeRect(15,50,100,10), Color(0.2, 0.6, 0.9))
		connectionNode = ConnectionNode(Point(oldX,oldY), Point(x,y), Color(0.1,0.1,0.5))
		self.addConnectionNode(connectionNode, 2, node, 2, node1)

		oldX = self.getSize().width*2/4

		x = self.getSize().width*3/7
		title = makeTitle('Node')
		body = 	makeBody('<span face="monospace">z-order=4</span>')
		controller = self.makeController(Point(x,y), title, body, Size(100, 75))
		self.addController(controller)
		node = RectangleNode(MakeRect(-10,20,60,50), Color(1.0, 1.0, 0.2))
		connectionNode = ConnectionNode(Point(oldX,oldY), Point(x,y), Color(0.1,0.1,0.5))
		self.addConnectionNode(connectionNode, 4, node, 4, node2)

		x = self.getSize().width*4/7
		title = makeTitle('Node')
		body = 	makeBody('<span face="monospace">z-order=1</span>')
		controller = self.makeController(Point(x,y), title, body, Size(100, 75))
		self.addController(controller)
		node = RectangleNode(MakeRect(-20,15,45,60), Color(0.3, 0.3, 0.3))
		connectionNode = ConnectionNode(Point(oldX,oldY), Point(x,y), Color(0.1,0.1,0.5))
		self.addConnectionNode(connectionNode, 5, node, 1, node2)

	def addConnectionNode(self, connectionNode, order, node, zOrder, parent=None):
		if parent is not None:
			parent.addChild(node, zOrder)
		else:
			self._displayNode.addChild(node, zOrder)
		node.setVisible(False)
		self._connectionNodes[connectionNode] = (order, node)
		self.addChild(connectionNode)

	def makeController(self, position, title, body, size=None, bodyMargin=20):
		if size is None:
			size = Size(100,100)
		node = SystemBlockNode()
		node.setAnchorPoint(Point(0.5,0.0))
		node.setPosition(position)
		node.setSize(size)
		node.setBodyMargin(bodyMargin)
		model = SystemBlockModel(title, body)
		controller = SystemBlockController(node, model)
		return controller

	def _callback(self, dt):
		if self._counter < 0:
			self._counter += 1
			return
		if self._counter == 0:
			[self._connectionNodes[x][1].setVisible(False) for x in self._connectionNodes]
		node = [self._connectionNodes[x][1] for x in self._connectionNodes if self._connectionNodes[x][0] is self._counter][0]
		connectionNode = [x for x in self._connectionNodes if self._connectionNodes[x][1] is node][0]
		connectionNode.sendPulse(callback=self._onSentPacket, data=node)
		self._counter += 1
		if self._counter >= len(self._connectionNodes):
			self._counter = -1

	def _onSentPacket(self, owner, node):
		node.setVisible(True)


class PlayButton(Node, GestureListener):
	def __init__(self, position):
		scale = 1.5
		Node.__init__(self, MakeRect(position.x, position.y, scale*100, scale*100))
		self._playSprite = SVGSprite("images/play_button.svg")
		self._playSprite.setScale(scale)
		self._pauseSprite = SVGSprite("images/pause_button.svg")
		self._pauseSprite.setScale(scale)
		self._isPlaying = True
		self._isLoaded = False
		self._isEntered = False
		self.addChild(self._pauseSprite)

	def onEnter(self):
		Node.onEnter(self)
		self.getDirector().getGestureDispatch().addListener(self)

	def onExit(self):
		Node.onExit(self)
		self.getDirector().getGestureDispatch().removeListener(self)

	def onMousePress(self, event):
		if self.getRect().containsPoint(event.point):
			self._isLoaded = True
			if self._isPlaying:
				sprite = self._pauseSprite
			else:
				sprite = self._playSprite
			sprite.setStylePropertyValueById("top_stop", "stop-color", "#6699FF")
			return True
		return False

	def onMouseRelease(self, event):
		if self._isLoaded:
			if self._isEntered:
				color = "#3366AA"
			else:
				color = "#003399"
			if self._isPlaying:
				if self._isEntered:
					self._pauseSprite.setStylePropertyValueById("top_stop", "stop-color", "#003399")
					self._playSprite.setStylePropertyValueById("top_stop", "stop-color", color)
					self.removeChild(self._pauseSprite)
					self.addChild(self._playSprite)
					self._isPlaying = not self._isPlaying
					if self._isPlaying:
						self.getDirector().resume()
					else:
						self.getDirector().pause()
				else:
					self._pauseSprite.setStylePropertyValueById("top_stop", "stop-color", color)
			else:
				if self._isEntered:
					self._playSprite.setStylePropertyValueById("top_stop", "stop-color", "#003399")
					self._pauseSprite.setStylePropertyValueById("top_stop", "stop-color", color)
					self.removeChild(self._playSprite)
					self.addChild(self._pauseSprite)
					self._isPlaying = not self._isPlaying
					if self._isPlaying:
						self.getDirector().resume()
					else:
						self.getDirector().pause()
				else:
					self._playSprite.setStylePropertyValueById("top_stop", "stop-color", color)
		self._isLoaded = False

	def onMouseMotion(self, event):
		if self.getRect().containsPoint(event.point):
			if self._isEntered:
				return False
			if self._isLoaded:
				color = "#6699FF"
			else:
				color = "#3366AA"
			if self._isPlaying:
				self._pauseSprite.setStylePropertyValueById("top_stop", "stop-color", color)
			else:
				self._playSprite.setStylePropertyValueById("top_stop", "stop-color", color)
			self._isEntered = True
		elif self._isEntered:
			if self._isPlaying:
				self._pauseSprite.setStylePropertyValueById("top_stop", "stop-color", "#003399")
			else:
				self._playSprite.setStylePropertyValueById("top_stop", "stop-color", "#003399")
			self._isEntered = False


class cocosCairoScene(Scene,GestureListener):
	def setup(self):
		self._connectionNodes = []
		self._counter = 0

		makeTitle = lambda string: '<span foreground="#FFFFFF">' + string + '</span>'

		x = self.getSize().width/2
		y = 10
		title = makeTitle('PyGTK')
		controller = self.makeController(Point(x,y), title, "", Size(100, 50))
		self.addController(controller)
		oldX = x
		oldY = y + 50

		x = self.getSize().width/2
		y = 160
		title = makeTitle('Director')
		controller = self.makeController(Point(x,y), title, "", Size(100, 50))
		self.addController(controller)
		connectionNode = ConnectionNode(Point(oldX,oldY), Point(x,y), Color(0.1,0.1,0.5))
		self._connectionNodes.append(connectionNode)

		oldX = x+50
		oldY = 160+25

		x = self.getSize().width*5/6
		title = makeTitle('Scheduler')
		controller = self.makeController(Point(x,y), title, "", Size(100, 50))
		self.addController(controller)
		connectionNode = ConnectionNode(Point(oldX,oldY), Point(x-50,y+25), Color(0.1,0.1,0.5))
		self._connectionNodes.append(connectionNode)

		oldX = x
		oldY = oldY+25

		x = self.getSize().width*5/6
		y = 310+25
		title = makeTitle('ActionManager')
		controller = self.makeController(Point(x,y), title, "", Size(150, 50))
		self.addController(controller)
		connectionNode = ConnectionNode(Point(oldX,oldY), Point(x,y), Color(0.1,0.1,0.5))
		self._connectionNodes.append(connectionNode)

		oldX = x
		oldY = y+50

		x = self.getSize().width*5/6
		y = 460+25
		title = makeTitle('Action')
		controller = self.makeController(Point(x,y), title, "", Size(100, 50))
		self.addController(controller)
		connectionNode = ConnectionNode(Point(oldX,oldY), Point(x,y), Color(0.1,0.1,0.5))
		self._connectionNodes.append(connectionNode)

		oldX = x-50
		oldY = y+25
		x = self.getSize().width/2
		y = 460+25
		title = makeTitle('Node')
		controller = self.makeController(Point(x,y), title, "", Size(100, 50))
		self.addController(controller)
		connectionNode = ConnectionNode(Point(oldX,oldY), Point(x+50,y+25), Color(0.1,0.1,0.5))
		self._connectionNodes.append(connectionNode)

		oldX = self.getSize().width/2
		oldY = 160+50
		x = self.getSize().width/2
		y = 310+25
		title = makeTitle('Scene')
		controller = self.makeController(Point(x,y), title, "", Size(100, 50))
		self.addController(controller)
		connectionNode = ConnectionNode(Point(oldX,oldY), Point(x,y), Color(0.1,0.1,0.5))
		self._connectionNodes.append(connectionNode)

		connectionNode = ConnectionNode(Point(x,y+50), Point(x,460+25), Color(0.1,0.1,0.5))
		self._connectionNodes.append(connectionNode)

		[self.addChild(connectionNode) for connectionNode in self._connectionNodes]

		oldX = self.getSize().width/2-50
		oldY = 10+25
		x = self.getSize().width*1/6
		y = 10
		title = makeTitle('GestureDispatch')
		controller = self.makeController(Point(x,y), title, "", Size(160, 50))
		self.addController(controller)
		self._conn1 = ConnectionNode(Point(oldX,oldY), Point(x+80,y+25), Color(0.1,0.1,0.5))
		self.addChild(self._conn1)

		oldX = x
		oldY = y+50
		x = oldX
		y = 160
		title = makeTitle('GestureListener')
		controller = self.makeController(Point(x,y), title, "", Size(160, 50))
		self.addController(controller)
		self._conn2 = ConnectionNode(Point(oldX,oldY), Point(x,y), Color(0.1,0.1,0.5))
		self.addChild(self._conn2)


	def makeController(self, position, title, body, size=None, bodyMargin=20):
		if size is None:
			size = Size(100,100)
		node = SystemBlockNode()
		node.setAnchorPoint(Point(0.5,0.0))
		node.setPosition(position)
		node.setSize(size)
		node.setBodyMargin(bodyMargin)
		model = SystemBlockModel(title, body)
		controller = SystemBlockController(node, model)
		return controller

	def callback(self, owner, data):
		if self._counter == 0:
			path = "images/new_frame.svg"
			point = Point(self.getSize().width/2-50, 100)
		elif self._counter == 1:
			path = "images/tick.svg"
			point = Point(self.getSize().width/2, 150)
		elif self._counter == 2:
			path = "images/tick.svg"
			point = Point(self.getSize().width*3/4, 250)
		elif self._counter == 3:
			path = "images/tick.svg"
			point = Point(self.getSize().width*3/4, 420)
		elif self._counter == 4:
			path = "images/update.svg"
			point = Point(self.getSize().width/2, 450)
		elif self._counter == 5:
			path = "images/redraw.svg"
			point = Point(self.getSize().width/2-50, 250)
		elif self._counter == 6:
			path = "images/redraw.svg"
			point = Point(self.getSize().width/2-50, 420)
		self.startFloatUpSequence(SVGSprite(path, point))
		self._connectionNodes[self._counter].sendPulse(duration=1.0, callback=self.callback)
		self._counter += 1
		if self._counter >= len(self._connectionNodes):
			self._counter = 0

	def startFloatUpSequence(self, node):
		self.addChild(node)
		node.setOpacity(0.0)
		duration = 1.0
		action1 = FadeIn(duration*3/4)
		action1a = EaseSineOut(MoveBy(duration*3/4, Point(0, -25)))
		action2 = FadeOut(duration*1/4)
		action2a = EaseSineIn(MoveBy(duration*1/4, Point(0, -25)))
		action3 = CallbackInstantAction(lambda:self.removeChild(node))
		sequence = Sequence(Spawn(action1,action1a), Spawn(action2,action2a), action3)
		node.runAction(sequence)

	def onEnter(self):
		Scene.onEnter(self)
		self.callback(None,None)
		self.getDirector().getGestureDispatch().addListener(self)

	def onExit(self):
		Scene.onExit(self)
		self.getDirector().getGestureDispatch().removeListener(self)

	def _mousePressCallback(self, owner, data):
		self._conn2.sendPulse(duration=1.0)
		self.startFloatUpSequence(SVGSprite("images/mouse_press.svg", Point(self.getSize().width/4-100, 100)))

	def onMousePress(self, event):
		self._conn1.sendPulse(duration=1.0, callback=self._mousePressCallback)
		self.startFloatUpSequence(SVGSprite("images/mouse_press.svg", Point(self.getSize().width/4-25, 50)))
		return True

	def _keyPressCallback(self, owner, data):
		self._conn2.sendPulse(duration=1.0)
		self.startFloatUpSequence(SVGSprite("images/key_press.svg", Point(self.getSize().width/4-100, 100)))

	def onKeyPress(self, event):
		self._conn1.sendPulse(duration=1.0, callback=self._keyPressCallback)
		self.startFloatUpSequence(SVGSprite("images/key_press.svg", Point(self.getSize().width/4-25, 50)))
		return True


if __name__ == "__main__":
	director = Director()
	director.setWindow()
	#director.runWithScene(ActionScene())
	#director.runWithScene(RedrawScene())
	director.runWithScene(cocosCairoScene())
