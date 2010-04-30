from cocosCairo.cocosCairo import *

class HelloWorldScene(Scene, GestureListener):
	def setup(self):
		# get the application's size
		size = self.director.size
		position = Point(size.width/2, size.height/2)	# make a point at the center of the screen

		# make a new label
		label = Label("Hello world!", position)
		label.fontSize = 72

		# make the label's position relative to the label's center
		label.anchorPoint = Point(0.5, 0.5)

		# attach the label to the Scene to make it visible in the app
		self.addChild(label)

if __name__ == "__main__":
	director = Director()
	director.showingFPS = True
	scene = HelloWorldScene()
	director.runWithScene(scene)
