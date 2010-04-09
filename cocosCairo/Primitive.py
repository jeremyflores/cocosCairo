"""
Defines Nodes which display primitive geometric items, such as Polygons or Points, to the screen.
"""

from Geometry import *
from Node import *
from Color import *

import math

# TODO: make more primitive nodes.

class PathNode(Node):
	"""
	Displays interconnected lines as defined by a L{Path}.
	"""
	def __init__(self, path=None, color=None, thickness=2.0):
		"""
		Initialization method.

		@param path: The path to be displayed.
		@type path: L{Path}
		@param color: The color of the line. Default is L{WhiteColor}.
		@type color: L{Color}
		@param thickness: The thickness of the line.
		@type thickness: Non-negative C{float}
		"""
		if path is None:
			path = Path()
		if color is None:
			color = WhiteColor()
		Node.__init__(self)
		self._path = None
		self._isRelative = False
		self._thickness = thickness
		self.setPath(path)
		self.setColor(color)

#{ Accessor methods.
	def getPath(self):
		"""
		Returns the Path to be displayed.

		@return: The Path to be displayed.
		@rtype: L{Path}
		"""
		return self._path

	def setPath(self, path):
		"""
		Sets the Path to be displayed.

		@param path: The Path to be displayed.
		@type path: L{Path}
		"""
		self._isRelative = isinstance(path, RelativePath)
		self._path = path

	path = property(getPath, setPath, doc="The Path to be displayed.")

	def getThickness(self):
		"""
		Returns the thickness of the line. Default is 2.0.

		@return: The thickness.
		@rtype: C{float}
		"""
		return self._thickness

	def setThickness(self, thickness):
		"""
		Sets the thickness of the line.

		@param thickness: The thickness.
		@type thickness: C{float}
		"""
		self._thickness = thickness

	thickness = property(getThickness, setThickness, doc="The thickness of the line.")
#}

	def getOpacity(self):
		"""
		Returns the opacity of the line.

		@return: The opacity.
		@rtype: C{float}
		"""
		return self._color.a

	def setOpacity(self, opacity):
		"""
		Sets the opacity for the line.

		@param opacity: The opacity from C{0.0} to C{1.0}.
		@type opacity: C{float}
		"""
		self._color.a = opacity

	def draw(self, context):
		points = self._path.getPoints()
		if len(points) < 2:
			return
		context.set_line_width(self._thickness)
		context.set_source_rgba(self._color.r, self._color.g, self._color.b, self._color.a)
		point = points[0]
		context.move_to(point.x, point.y)
		if self._isRelative:
			for point in points[1:]:
				context.rel_line_to(point.x, point.y)
		else:
			for point in points[1:]:
				context.line_to(point.x, point.y)
		context.stroke()

class LineNode(Node):
	"""
	Displays a line.
	"""
	def __init__(self, startPoint=None, endPoint=None, color=None, thickness=2.0):
		"""
		Initialization method.

		@param startPoint: The starting point of the line. Default is L{PointZero}.
		@type startPoint: L{Point}
		@param endPoint: The ending point of the line. Default is L{PointZero}.
		@type endPoint: L{Point}
		@param color: The color of the line. Default is L{WhiteColor}.
		@type color: L{Color}
		@param thickness: The thickness of the line.
		@type thickness: Non-negative C{float}
		"""
		if startPoint is None:
			startPoint = Point(0,0)
		if endPoint is None:
			endPoint = Point(0,0)
		if color is None:
			color = WhiteColor()
		Node.__init__(self)
		self._startPoint = startPoint
		self._endPoint = endPoint
		self._thickness = thickness
		self.setColor(color)

#{ Accessor methods.
	def getStartPoint(self):
		"""
		Returns the starting point of the LineNode.

		@return: The starting point.
		@rtype: L{Point}
		"""
		return self._startPoint.copy()

	def setStartPoint(self, startPoint):
		"""
		Sets the starting point of the LineNode.

		@param startPoint: The starting point.
		@type startPoint: L{Point}
		"""
		self._startPoint = startPoint.copy()
		self._updateRect()

	startPoint = property(getStartPoint, setStartPoint, doc="The starting point of the LineNode.")

	def getEndPoint(self):
		"""
		Returns the end point of the LineNode.

		@return: The end point.
		@rtype: L{Point}
		"""
		return self._endPoint.copy()

	def setEndPoint(self, endPoint):
		"""
		Sets the end point of the LineNode.

		@param endPoint: The end point.
		@type endPoint: L{Point}
		"""
		self._endPoint = endPoint.copy()
		self._updateRect()

	endPoint = property(getEndPoint, setEndPoint, doc="The ending point of the LineNode.")

	def getThickness(self):
		"""
		Returns the thickness of the line. Default is 2.0.

		@return: The thickness.
		@rtype: C{float}
		"""
		return self._thickness

	def setThickness(self, thickness):
		"""
		Sets the thickness of the line.

		@param thickness: The thickness.
		@type thickness: C{float}
		"""
		self._thickness = thickness

	thickness = property(getThickness, setThickness, doc="The thickness of the line.")
#}


#{ Private methods.
	def _updateRect(self):
		if self._endPoint.x < self._startPoint.x or self._endPoint.y < self._startPoint.y:
			startPoint = self._endPoint
			endPoint = self._startPoint
		else:
			startPoint = self._startPoint
			endPoint = self._endPoint
		x = startPoint.x
		y = startPoint.y
		w = startPoint.x + endPoint.x
		h = startPoint.y + endPoint.y
		self.setRect(MakeRect(x,y,w,h))
#}
	def getOpacity(self):
		"""
		Returns the opacity of the line.

		@return: The opacity.
		@rtype: C{float}
		"""
		return self._color.a

	def setOpacity(self, opacity):
		"""
		Sets the opacity for the line.

		@param opacity: The opacity from C{0.0} to C{1.0}.
		@type opacity: C{float}
		"""
		self._color.a = opacity

	def draw(self, context):
		context.set_line_width(self._thickness)
		context.set_source_rgba(self._color.r, self._color.g, self._color.b, self._color.a)
		context.move_to(self._startPoint.x, self._startPoint.y)
		context.line_to(self._endPoint.x, self._endPoint.y)
		context.stroke()

class AbstractFillableNode(Node):
	"""
	A L{Node} which can be filled with a color and have a colored outline.
	"""
	def __init__(self, fillColor=None, strokeColor=None, strokeThickness=0.0):
		"""
		Initialization method.
		
		@param fillColor: The color which will fill the polygon. Default is L{WhiteColor}.
		@type fillColor: L{Color}
		@param strokeColor: The color which will outline the polygon. Default is L{ClearColor}.
		@type strokeColor: L{Color}
		@param strokeThickness: The thickness of the line.
		@type strokeThickness: Non-negative C{float}
		"""
		Node.__init__(self)
		if fillColor is None:
			fillColor = WhiteColor()
		if strokeColor is None:
			strokeColor = ClearColor()
		self._fillColor = fillColor
		self._strokeColor = strokeColor
		self._strokeThickness = strokeThickness

	def getOpacity(self):
		"""
		Returns the opacity for the fill color.

		@return: The opacity.
		@rtype: C{float}
		"""
		return self._fillColor.a

	def setOpacity(self, opacity):
		"""
		Sets the opacity for the fill color.

		@param opacity: The opacity from C{0.0} to C{1.0}.
		@type opacity: C{float}
		"""
		self._fillColor.a = opacity

	def getColor(self):
		return self.getFillColor()

	def setColor(self, color):
		self.setFillColor(color)

#{ Accessor methods.
	def getFillColor(self):
		"""
		Returns the color which will fill the Node. Default is L{WhiteColor()}.

		@return: Fill color.
		@rtype: L{Color}
		"""
		return self._fillColor.copy()

	def setFillColor(self, fillColor):
		"""
		Sets the color which will fill the Node.

		@param fillColor: Fill color.
		@rtype: L{Color}
		"""
		self._fillColor = fillColor.copy()

	fillColor = property(getFillColor, setFillColor, doc="The color which will fill the Node.")

	def getStrokeColor(self):
		"""
		Returns the Color which will outline the Node. Default is L{ClearColor()}.

		@return: Stroke color.
		@rtype: L{Color}
		"""
		return self._strokeColor.copy()

	def setStrokeColor(self, strokeColor):
		"""
		Sets the Color which will outline the Node.

		@param strokeColor: Stroke color.
		@type strokeColor: L{Color}
		"""
		self._strokeColor = strokeColor.copy()

	strokeColor = property(getStrokeColor, setStrokeColor, doc="The Color which will outline the Node.")

	def getStrokeThickness(self):
		"""
		Returns the thickness of the outline. Default is C{2.0}.

		@return: Stroke thickness.
		@rtype: C{float}
		"""
		return self._strokeThickness

	def setStrokeThickness(self, strokeThickness):
		"""
		Sets the thickness of the outline.

		@param strokeThickness: Stroke thickness.
		@type strokeThickness: C{float}
		"""
		self._strokeThickness = strokeThickness

	strokeThickness = property(getStrokeThickness, setStrokeThickness, doc="The thickness of the outline.")
#}


class PolygonNode(AbstractFillableNode):
	def __init__(self, polygon=None, fillColor=None, strokeColor=None, strokeThickness=0.0):
		"""
		Initialization method.

		@param polygon: The Polygon to display.
		@type polygon: L{Polygon}
		@param fillColor: The color which will fill the polygon. Default is L{WhiteColor}.
		@type fillColor: L{Color}
		@param strokeColor: The color which will outline the polygon. Default is L{ClearColor}.
		@type strokeColor: L{Color}
		@param strokeThickness: The thickness of the line.
		@type strokeThickness: Non-negative C{float}
		"""
		AbstractFillableNode.__init__(self, fillColor, strokeColor, strokeThickness)
		self._polygon = None
		self._minX = 0
		self._minY = 0
		if polygon is not None:
			self.setPolygon(polygon)

#{ Accessor methods.
	def getPolygon(self):
		"""
		Returns the Polygon (or C{None} if it is not yet defined).

		@return: The Polygon.
		@rtype: L{Polygon}
		"""
		return self._polygon

	def setPolygon(self, polygon):
		"""
		Sets the Polygon to be rendered.

		@param polygon: The Polygon to be rendered.
		@type polygon: L{Polygon}
		"""
		allX = [point.x for point in polygon.getPoints()]
		allY = [point.y for point in polygon.getPoints()]
		minX = min(allX)
		maxX = max(allX)
		minY = min(allY)
		maxY = max(allY)
		rect = MakeRect(minX, minY, maxX-minX, maxY-minY)
		self._minX = minX
		self._minY = minY
		self.setRect(rect)
		self._polygon = polygon

	polygon = property(getPolygon, setPolygon, doc="The Polygon to be rendered.")
#}

	def draw(self, context):
		points = self._polygon.getPoints()
		if len(points) < 3:
			return
		color = self._fillColor
		context.set_source_rgba(color.r, color.g, color.b, color.a)
		x = self._minX
		y = self._minY
		context.move_to(points[0].x-x, points[0].y-y)
		for point in points[1:]:
			context.line_to(point.x-x, point.y-y)
		context.close_path()
		context.fill()
		context.set_line_width(self._strokeThickness)
		color = self._strokeColor
		context.set_source_rgba(color.r, color.g, color.b, color.a)
		context.move_to(points[0].x-x, points[0].y-y)
		for point in points[1:]:
			context.line_to(point.x-x, point.y-y)
		context.close_path()
		context.stroke()

class RectangleNode(PolygonNode):
	"""
	Displays a rectangle.
	"""
	def __init__(self, rect=None, fillColor=None, strokeColor=None, strokeThickness=0.0):
		"""
		Initialization method.

		@param rect: The bounding box of the Node. Default is L{RectZero}.
		@type rect: L{Rect}
		@param fillColor: The color which will fill the rectangle. Default is L{WhiteColor}.
		@type fillColor: L{Color}
		@param strokeColor: The color which will outline the rectangle. Default is L{ClearColor}.
		@type strokeColor: L{Color}
		@param strokeThickness: The thickness of the line.
		@type strokeThickness: Non-negative C{float}
		"""
		x = rect.point.x
		y = rect.point.y
		w = rect.size.width
		h = rect.size.height
		
		polygon = Polygon(Point(x,y), Point(x+w,y), Point(x+w,y+h), Point(x,y+h))
		PolygonNode.__init__(self, polygon, fillColor, strokeColor, strokeThickness)


class EllipseNode(AbstractFillableNode):
	"""
	Displays an ellipse in the given L{Rect}.
	"""
	def __init__(self, rect=None, color=None):
		AbstractFillableNode.__init__(self, color)
		self.setRect(rect)

	def getColor(self):
		return self._fillColor

	def setColor(self, color):
		self._fillColor = color

	def draw(self, context):
		context.save()
		w = self.getRect().size.width
		h = self.getRect().size.height
		context.translate(w/2., h/2.)
		context.scale(w/2., h/2.)
		color = self._fillColor
		context.set_source_rgba(color.r, color.g, color.b, color.a)
		context.arc(0., 0., 1., 0., 2*math.pi)
		context.fill()
		context.restore()

class PointNode(EllipseNode):
	"""
	Draws a circle with a given radius at a L{Point}.
	"""
	def __init__(self, point, fillColor=None, radius=1.0):
		"""
		Initialization method.

		@param point: The location of where this Node will be drawn.
		@type point: L{Point}
		@param radius: The radius of the circle to be drawn. Default is 2.0.
		@type radius: Non-negative C{float}
		@param fillColor: The color of the circle to be drawn. Default is L{WhiteColor()}.
		@type fillColor: L{Color}
		"""
		EllipseNode.__init__(self, MakeRect(point.x, point.y, radius*2, radius*2), fillColor)
		self.setAnchorPoint(Point(0.5,0.5))
