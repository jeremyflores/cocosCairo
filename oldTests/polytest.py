from cocosCairo.cocosCairo import *

import random

class MyScene(Scene, GestureListener):
	def setup(self):
		points = []
		for i in range(0,50):
			point = Point(random.randint(0,800), random.randint(0,600))
			points.append(point)
		for point in points:
			node = PointNode(point, WhiteColor())
			self.addChild(node, 3)
		self._polygon = MakePolygon(*points)
		#self._polygon = Polygon(Point(50,50), Point(20,100), Point(70,460), Point(80, 470), Point(90, 500), Point(240,540), Point(360,440))
		x = 150
		y = 150
		w = 50
		h = 50
		#self._polygon = Polygon(Point(x,y), Point(x+w,y), Point(x+w,y+h), Point(x,y+h))
		self._polygonNode = PolygonNode(self._polygon, GreenColor(), RedColor(), 2)
		self.addChild(self._polygonNode)
		self._isEntered = False

	def onEnter(self):
		Scene.onEnter(self)
		self.getDirector().getGestureDispatch().addListener(self)

	def onExit(self):
		Scene.onExit(self)
		self.getDirector().getGestureDispatch().removeListener(self)

	def onMouseMotion(self, event):
		point = event.point
		if self._polygon.containsPoint(point):
			if not self._isEntered:
				self._isEntered = True
				self._polygonNode.setFillColor(WhiteColor())
		else:
			if self._isEntered:
				self._isEntered = False
				self._polygonNode.setFillColor(GreenColor())

if __name__ == "__main__":
	director = Director()
	director.setWindow()
	director.runWithScene(MyScene())
