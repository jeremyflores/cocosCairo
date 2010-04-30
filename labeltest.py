from cocosCairo.cocosCairo import *

class MyScene(Scene):
	def setup(self):
		self._label = Label("Hey there", Point(50,50))
		self._label.fontSize = 24
		self._label.bold = True
		self.addChild(self._label)

	def onEnter(self):
		Scene.onEnter(self)
		self._label.opacity = 0.0
		action = FadeIn(1.0)
		action2 = MoveBy(2.0, Point(250,100))
		self._label.runAction(Sequence(action, action2))

if __name__ == "__main__":
	director = Director()
	director.showingFPS = True
	director.runWithScene(MyScene())
