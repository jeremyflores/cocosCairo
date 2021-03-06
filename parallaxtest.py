from cocosCairo.cocosCairo import *
import math

class ParallaxScene(Scene):
	def setup(self):
		self._parallax = ParallaxNode()
		self._parallax.size = Size(2000,2000)
		sprite = SVGSprite("images/system_block.svg", PointZero())
		sprite.size = Size(1000,1000)
		self._parallax.addChild(sprite, 1)
		self.addChild(self._parallax)
		sprite2 = Sprite("images/pulse.png")
		sprite2.position = Point(800,300)
		self._parallax.addChild(sprite2, 2, ratio=Point(0.5, 0.2), offset=Point(400,300))

	def onEnter(self):
		Scene.onEnter(self)
		action = MoveBy(5.0, Point(200, -900))
		self._parallax.runAction(action)


if __name__ == "__main__":
	director = Director()
	director.showingFPS = True
	director.runWithScene(ParallaxScene())
