from cocosCairo.cocosCairo import *

class HelloWorldScene(Scene, GestureListener):
	def setup(self):
		# get the application's size
		size = self.getDirector().getSize()
		width = size.width	# get the size's width and height
		height = size.height
		position = Point(width/2, height/2)	# make a point at the center of the screen

		# make a new label
		label = Label("Hello world!", position)
		label.opacity = 0.5
		label.setFontSize(72)

		# make the label's position relative to the label's center
		anchorPoint = Point(0.5, 0.5)
		label.setAnchorPoint(anchorPoint)

		# attach the label to the Scene to make it visible in the app
		self.addChild(label)

if __name__ == "__main__":
	director = Director()
	director.setShowingFPS(True)
	scene = HelloWorldScene()
	director.runWithScene(scene)
