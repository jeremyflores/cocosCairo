from cocosCairo.cocosCairo import *

class PathScene(Scene):
	def setup(self):
		self._path = Path(Point(50,50), Point(100,100), Point(300,300), Point(600,10), Point(600,400), Point(200, 400))
		#self._path = RelativePath(Point(50,50), Point(10,0), Point(50,100), Point(-25, -100))
		pathNode = PathNode(self._path)
		self.addChild(pathNode)
		self._sprite = Sprite("images/pulse.png")
		self._sprite.setAnchorPoint(Point(0.5,0.5))
		self._sprite.setScale(0.25)
		self._sprite.setPosition(Point(100,100))
		self.addChild(self._sprite)

	def onEnter(self):
		Scene.onEnter(self)
		action = EaseSineInOut(MoveAlongPath(5.0, self._path))
		self._sprite.runAction(action)

if __name__ == "__main__":
	director = Director()
	director.setWindow()
	director.runWithScene(PathScene())
