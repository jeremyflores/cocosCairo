from cocosCairo.cocosCairo import *

class MainScene(Scene):
	def setup(self):
		self.backgroundColor = GrayColor()
		rect1 = MakeRect(self.size.width/2, self.size.height/2, 50, 50)
		self.rectNode1 = RectangleNode(rect1, Color(0.2, 0.2, 0.2))
		self.rectNode1.anchorPoint = Point(0.5, 0.5)
		self.addChild(self.rectNode1)

		rect2 = MakeRect(0, self.size.height/2, 50, 50)
		self.rectNode2 = RectangleNode(rect2, WhiteColor())
		self.rectNode2.setScale(2.0)
		self.rectNode2.anchorPoint = Point(0.5, 0.5)
		self.addChild(self.rectNode2)

	def onEnter(self):
		Scene.onEnter(self)

		scale1 = EaseSineInOut(ScaleBy(1.0, 0.01))
		sequence1 = Sequence(scale1, scale1.reverse())
		repeat1 = RepeatForever(sequence1)
		self.rectNode1.runAction(repeat1)

		scale2 = EaseSineInOut(ScaleBy(1.0, 0.01))
		move1 = EaseSineInOut(MoveBy(2.0, Point(self.size.width, 0)))
		scaleSequence = Sequence(scale2, scale2.reverse(), scale2, scale2.reverse())
		moveSequence = Sequence(move1, move1.reverse()) 
		spawn1 = Spawn(scaleSequence, moveSequence)
		repeat2 = RepeatForever(spawn1)
		self.rectNode2.runAction(repeat2)


if __name__ == "__main__":
	director = Director()
	scene = MainScene()
	director.runWithScene(scene)
