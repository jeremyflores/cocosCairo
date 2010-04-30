from cocosCairo.cocosCairo import * # Convenience module to import all other modules
from splash import *

BACKGROUND_COLOR = Color(0.1, 0.3, 0.7)

MAZE_PATHS = ["maze01.maze", "maze02.maze", "maze03.maze"]	# an ordered list of the maze files
PATH_INDEX = 0	# the index of the next maze file to load

class MazeScene(Scene):
	def __init__(self, modelPath):
		Scene.__init__(self)
		self._modelPath = modelPath

	def setup(self):
		self.setBackgroundColor(BACKGROUND_COLOR)

	def onEnterFromFinishedTransition(self):
		Scene.onEnterFromFinishedTransition(self)

		self._mazePathController = MazePathController(self._modelPath)
		self.addController(self._mazePathController)

		x = self.size.width/2
		y = self.size.height/2
		self._mazePathController.node.position = Point(x,y)

		self._mazePathController.node.opacity = 0.0
		action = EaseSineInOut(FadeIn(1.0))
		cbAction = CallbackInstantAction(self._onFadeInCompletion)
		sequence = Sequence(action, cbAction)
		self._mazePathController.node.runAction(sequence)

	def _onFadeInCompletion(self):
		self._mazePathController.node.showPieces()

class MazePathModel(AbstractModel):
	def __init__(self, filepath):
		AbstractModel.__init__(self)
		self._modelArray = []
		self._playerLocation = [0,0]
		self._goalLocation = [0,0]
		self._moveCount = 0
		f = open(filepath)
		# populate the model array
		for line in f:
			line = line.strip()
			if len(line) < 1 or line[0] is "#" or line[:2] is "//":	# if the line is a comment or empty
				continue	# then move on to the next line
			row = line.split(',')
			row = [int(x[:1]) for x in row if (len(x) > 0 and x != '\n')]	# trim and convert to int
			self._modelArray.append(row)
		# look for special characters
		for i in range(0, len(self._modelArray[0])):
			for j in range(0, len(self._modelArray)):
				if self._modelArray[j][i] is 2:
					self._playerLocation = [i, j]
					self._modelArray[j][i] = 1
				elif self._modelArray[j][i] is 3:
					self._goalLocation = [i, j]
					self._modelArray[j][i] = 1
		f.close()
		self.didChange()

	def getModelArray(self):
		return self._modelArray

	modelArray = property(getModelArray)

	def getPlayerLocation(self):
		return self._playerLocation

	playerLocation = property(getPlayerLocation)

	def getGoalLocation(self):
		return self._goalLocation

	goalLocation = property(getGoalLocation)

	def getMoveCount(self):
		return self._moveCount

	moveCount = property(getMoveCount)

	def movePlayerLocation(self, direction):
		self._moveCount += 1
		row = self._playerLocation[1]
		col = self._playerLocation[0]
		if direction == "left":
			if col-1 < 0 or self._modelArray[row][col-1] != 1:
				return
			else:
				self._playerLocation = [col-1, row]
				self.didChange()
		elif direction == "right":
			if col+1 >= len(self._modelArray[0]) or self._modelArray[row][col+1] != 1:
				return
			else:
				self._playerLocation = [col+1, row]
				self.didChange()
		elif direction == "up":
			if row-1 < 0 or self._modelArray[row-1][col] != 1:
				return
			else:
				self._playerLocation = [col, row-1]
				self.didChange()
		elif direction == "down":
			if row+1 >= len(self._modelArray) or self._modelArray[row+1][col] != 1:
				return
			else:
				self._playerLocation = [col, row+1]
				self.didChange()


class MazePathNode(Node):
	def __init__(self, rect=None):
		Node.__init__(self, rect)
		self._hasRenderedTiles = False
		self._hasFinishedActions = False
		self._player = None
		self._goal = None
		self._tileSize = 50
		self.anchorPoint = Point(0.5, 0.5)

	def setOpacity(self, opacity):
		Node.setOpacity(self, opacity)
		for child in self.children:
			child.opacity = opacity

	def onModelChange(self, model):
		if not model:
			return
		# render the tiles
		if not self._hasRenderedTiles:
			self._hasRenderedTiles = True
			modelArray = model.modelArray
			width = self._tileSize * len(modelArray[0])
			height = self._tileSize * len(modelArray)
			self.size = Size(width, height)
			for i in range(0, len(modelArray[0])):
				for j in range(0, len(modelArray)):
					x = i*self._tileSize
					y = j*self._tileSize
					w = self._tileSize
					h = self._tileSize
					rect = MakeRect(x, y, w, h)
					if modelArray[j][i] is 0:	# 'matrix' lookup is [row,col], but that's equivalent to (y,x) instead of (x,y), so switch the i,j indices
						continue
					else:
						color = WhiteColor()
					rectangle = RectangleNode(rect, color)
					self.addChild(rectangle, 1)

		# set up the player's sprite
		x = model.playerLocation[0] * self._tileSize
		y = model.playerLocation[1] * self._tileSize
		if not self._player:
			self._player = Sprite("images/character.png", Point(x,y))
			self.addChild(self._player,3)
			self._player.scale = 0.01
			self._player.anchorPoint = Point(0.5,0.5)
			size = self._player.size.width
			self._player.position = pointAdd(self._player.position, Point(size/2, size/2))
		else:
			self._hasFinishedActions = False
			action = EaseSineInOut(MoveTo(0.05, Point(x,y)))
			cbAction = CallbackInstantAction(self.onPlayerMotionCompletion)
			sequence = Sequence(action, cbAction)
			self._player.runAction(sequence)

		# set up the goal sprite
		x = model.goalLocation[0] * self._tileSize
		y = model.goalLocation[1] * self._tileSize
		if not self._goal:
			self._goal = Sprite("images/goal.png", Point(x,y))
			self.addChild(self._goal,2)
			self._goal.scale = 0.01
			self._goal.anchorPoint = Point(0.5,0.5)
			size = self._goal.size.width
			self._goal.position = pointAdd(self._goal.getPosition(), Point(size/2, size/2))
		else:
			self._goal.position = Point(x,y)

	def showPieces(self):
		if self._goal:
			action = EaseBounceOut(ScaleTo(0.75, 1.0))
			sequence = Sequence(action, CallbackInstantAction(self.onGoalScaleCompletion))
			self._goal.runAction(sequence)

	def onGoalScaleCompletion(self):
		self._goal.anchorPoint = PointZero()
		size = self._goal.size.width
		self._goal.position = pointSub(self._goal.position, Point(size/2, size/2))
		if self._player:
			action = EaseBounceOut(ScaleTo(0.75, 1.0))
			sequence = Sequence(action, CallbackInstantAction(self.onPlayerScaleCompletion))
			self._player.runAction(sequence)

	def onPlayerScaleCompletion(self):
		self._player.anchorPoint = PointZero()
		size = self._player.size.width
		self._player.position = pointSub(self._player.getPosition(), Point(size/2, size/2))
		self._hasFinishedActions = True

	def onPlayerMotionCompletion(self):
		self._hasFinishedActions = True

	def reset(self):
		self._hasRenderedTiles = False
		self._hasFinishedActions = False
		self.removeAllChildren()
		self._player = None
		self._goal = None

	def hasFinishedActions(self):
		return self._hasFinishedActions


class MazePathController(AbstractController):
	def __init__(self, modelPath):
		AbstractController.__init__(self, MazePathNode(RectZero()), MazePathModel(modelPath))

	def onKeyPress(self, event):
		if not self.getNode().hasFinishedActions():
			return

		key = event.key
		if key == "Left":
			self.model.movePlayerLocation("left")
		elif key == "Right":
			self.model.movePlayerLocation("right")
		elif key == "Up":
			self.model.movePlayerLocation("up")
		elif key == "Down":
			self.model.movePlayerLocation("down")

		if self.model.playerLocation == self.model.goalLocation:
			winScene = WinScene(self.model.moveCount)
			transition = MoveInTopTransition(.5, winScene)
			self.director.replaceScene(transition)
		return True


class WinScene(Scene, GestureListener):
	def __init__(self, moveCount):
		Scene.__init__(self)
		self._currentCount = 0
		self._moveCount = moveCount

	def setup(self):
		self.backgroundColor = WhiteColor()
		size = self.size
		winLabel = Label("You win!", Point(size.width/2, 50), BlackColor())
		winLabel.fontSize = 72
		winLabel.anchorPoint = Point(0.5, 0.5)
		self.addChild(winLabel)
		self._moveCountLabel = Label("00", Point(size.width/2, 300), BlackColor())
		self._moveCountLabel.anchorPoint = Point(0.5, 0.5)
		self._moveCountLabel.fontSize = 72
		self.addChild(self._moveCountLabel)
		movesLabel = Label("moves", Point(size.width/2, 400), BlackColor())
		movesLabel.anchorPoint = Point(0.5, 0.5)
		movesLabel.fontSize = 72
		self.addChild(movesLabel)

	def onEnter(self):
		Scene.onEnter(self)
		self.director.gestureDispatch.addListener(self)

	def onEnterFromFinishedTransition(self):
		Scene.onEnterFromFinishedTransition(self)
		self.scheduleCallback(self._updateCount, 0.001/self._moveCount)

	def onExit(self):
		Scene.onExit(self)
		self.director.gestureDispatch.removeListener(self)

	def _updateCount(self, dt):
		self._currentCount += 1
		if self._currentCount < 10:
			countString = "0"+str(self._currentCount)
		else:
			countString = str(self._currentCount)
		self._moveCountLabel.text = countString
		if self._currentCount >= self._moveCount:
			self.unscheduleCallback(self._updateCount)

	def onKeyPress(self, event):
		self._onEvent()
		return True

	def onMousePress(self, event):
		self._onEvent()
		return True

	def _onEvent(self):
		global PATH_INDEX
		global MAZE_PATHS
		if PATH_INDEX < len(MAZE_PATHS):
			path = MAZE_PATHS[PATH_INDEX]
			PATH_INDEX += 1
			transition = RotoZoomTransition(1.0, MazeScene(path))
			self.director.replaceScene(transition)
		else:
			PATH_INDEX = 0 # for right now, just loop through the mazes
			self._onEvent()


if __name__ == "__main__":
	director = Director()
	director.setShowingFPS(True)
	path = MAZE_PATHS[PATH_INDEX]
	PATH_INDEX += 1
	transition = RotoZoomTransition(1.5, MazeScene(path))
	director.runWithScene(SplashScene(transition))
	#director.runWithScene(MazeScene(path))	# Use this to skip the splash scene.
