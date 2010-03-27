import math
import random

class Size:
	"""
	The size of some object (usually a L{Node}), given as its width and height (usually in pixels). A Size is considered a primitive, so its values may be accessed directly. If you wish to render geometric shapes to the screen, see the C{Primitive} module.
	"""
	def __init__(self, width, height):
		"""
		Initialization method.

		@param width: The width.
		@type width: Non-negative C{float}
		@param height: The height.
		@type height: Non-negative C{float}
		"""
		self.width = width		#: The recorded width. Should be a non-negative C{int} or C{float}.
		self.height = height	#: The recorded height. Should be a non-negative C{int} or C{float}.

	def __str__(self):
		return "width: " + str(self.width) + "\t\theight: " + str(self.height)

	def copy(self):
		"""
		Returns a new Size with the same L{width} and L{height}.

		@return: A new Size.
		@rtype: L{Size}
		"""
		return Size(self.width, self.height)



class Point:
	"""
	A two-dimensional coordinate (usually for a L{Node}), given as its x-coordinate and its y-coordinate (usually in pixels). Note that, due to the rendering aspects of Cairo, an increase in the y-coordinate usually means that the point has moved downwards (and not, as might be intuitive, upwards). A Point is considered a primitive, so its values may be accessed directly.
	"""
	def __init__(self, x, y):
		"""
		Initialization method.

		@param x: The x-coordinate.
		@type x: C{float}
		@param y: The y-coordinate.
		@type y: C{float}
		"""
		self.x = x		#: The recorded x value. Should be an C{int} or C{float}.
		self.y = y		#: The recorded y value. Should be an C{int} or C{float}.

	def __str__(self):
		return "x: " + str(self.x) + "\t\ty: " + str(self.y)

	def copy(self):
		"""
		Returns a new Point with the same L{x} and L{y} coordinates.

		@return: A new Point.
		@rtype: L{Point}
		"""
		return Point(self.x, self.y)


class Rect:
	"""
	A L{Point} and a L{Size} which are used to define a rectangle. A Rect is considered a primitive, so its values may be accessed directly.

	If you wish to render a rect to the screen, see L{RectangleNode}.
	"""
	def __init__(self, point, size):
		"""
		Initialization method.

		@param point: A Point.
		@type point: L{Point}
		@param size: A Size.
		@type size: L{Size}
		"""
		self.point = point	#: The recorded L{Point}.
		self.size = size	#: The recorded L{Size}.

	def __str__(self):
		return str(self.point) + " " + str(self.size)

	# TODO: might have to optimize this method more as it may be called multiple times per redraw
	def intersectsRect(self, rect):
		"""
		Tests whether or not this rect intersects some other rect.

		@param rect: The rect to test against.
		@type rect: L{Rect}
		@return: Whether or not the rects intersect.
		@rtype: C{bool}
		"""
		left1 = self.point.x
		top1 = self.point.y
		right1 = self.point.x+self.size.width
		bottom1 = self.point.y+self.size.height

		left2 = rect.point.x
		top2 = rect.point.y
		right2 = rect.point.x+rect.size.width
		bottom2 = rect.point.y+rect.size.height

		doesIntersect = 	(left2 < right1) and \
							(right2 > left1) and \
							(top2 < bottom1) and \
							(bottom2 > top1)
		if (doesIntersect):
			return True
		else:
			return False

	def containsPoint(self, point):
		"""
		Tests whether or not this rect contains a point.
		
		@param point: The point to test.
		@type point: L{Point}
		@return: Whether or not the point is in the rect.
		@rtype: C{bool}
		"""
		doesIntersect = (point.x >= self.point.x) and \
						(point.x <= self.point.x+self.size.width) and \
						(point.y >= self.point.y) and \
						(point.y <= self.point.y+self.size.height)
		if (doesIntersect):
			return True
		else:
			return False

	def copy(self):
		"""
		Returns a new Rect with the same L{point} and L{size}.

		@return: A new Rect.
		@rtype: L{Rect}
		"""
		return Rect(self.point.copy(), self.size.copy())


class Polygon:
	"""
	A sequence of L{Point}C{s} which defines a polygon. Note that the polygon is assumed to be closed by having the last given Point connect to the first given Point.
	"""
	def __init__(self, *points):
		"""
		Initialization method.

		@param points: The order in which the polygon's outline will be traced.
		@type points: C{Comma-separated Points}
		"""
		self._points = []
		for point in points:
			self.addPoint(point)

	def getPoints(self):
		"""
		Returns an ordered list of the Polygon's Points.

		@return: The Polygon's Points.
		@rtype: C{list of Points}
		"""
		return [point.copy() for point in self._points]

	def getPointAtIndex(self, index):
		"""
		Returns a copy of the Point at the given index, if it exists. If not, it will return C{None}.

		@param index: The index of desired Point.
		@type index: C{int}
		@return: The Point at that index.
		@rtype: L{Point} (or C{None})
		"""
		if index >= len(self._points) or len < 0:
			return None
		return self._points[index].copy()

	def clearPoints(self):
		"""
		Removes all points from the Polygon.
		"""
		self._points = []

	def addPoint(self, point):
		"""
		Adds a new Point to the Polygon if it is not already added.

		@param point: The Point to add.
		@type point: L{Point}
		"""
		matchingPoints = [p for p in self._points if p.x==point.x and p.y==point.y]
		if len(matchingPoints) < 1:
			self._points.append(point.copy())

	def addPoints(self, *points):
		"""
		Adds a sequence of new Points to the Polygon.

		@param points: The sequence of Points to add.
		@type points: C{Comma-separated Points}
		"""
		for point in points:
			self.addPoint(point)

	def containsPoint(self, point):
		"""
		Returns whether or not the Polygon contains a point.

		@param point: The Point to test.
		@type point: L{Point}
		@return: Whether or not the Point is in the Polygon.
		@rtype: C{bool}
		"""
		x = point.x
		y = point.y
		xp = [p.x for p in self._points]
		yp = [p.y for p in self._points]
		oddNodes = False
		j = len(self._points)-1
		for i in range(0, len(self._points)):
			if (yp[i]<y and yp[j]>=y) or (yp[j]<y and yp[i]>=y):
				 if xp[i]+(y-yp[i])/(yp[j]-yp[i])*(xp[j]-xp[i]) < x:
					oddNodes = not oddNodes
			j = i
		return oddNodes


class Path:
	"""
	A sequence of L{Point}C{s} which defines a path.
	"""
	def __init__(self, *points):
		"""
		Initialization method.

		@param points: The points which define the path.
		@type points: C{Comma-separated Points}
		"""
		self._points = points

	def getPoints(self):
		"""
		Returns the list of Points for the path.

		@return: The Points for the path.
		@rtype: C{list}
		"""
		return self._points

	def addPoint(self, point):
		"""
		Adds a Point to the path.

		@param point: A Point.
		@type point: L{Point}
		"""
		self._points.append(point)
		
class RelativePath(Path):
	"""
	A sequence of L{Point}C{s} which defines a path. The first Point is used as the absolute starting point, and all subsequent Points are relative to the first Point.
	"""
	pass

#{ Constructor functions.
def MakePolygon(*points):
	"""
	Creates the smallest possible convex polygon which encompasses the given points. (That is, it returns the convex hull of the points.)

	@param points: The L{Point}C{s} to be bounded by a Polygon.
	@type points: C{comma-separated Points}
	@return: The convex polygon bounding the points.
	@rtype: L{Polygon}
	"""
	# Based on the Jarvis gift-wrapping algorithm.
	def isRightTurn(p0,p1,p2):
		p02x = p2.x-p0.x
		p02y = p2.y-p0.y
		p01x = p1.x-p0.x
		p01y = p1.y-p0.y
		return (p02x*p01y-p02y*p01x) > 0
	points = [point.copy() for point in points]
	polygon = Polygon()
	if len(points) < 1:
		return polygon
	if len(points) < 3:
		for point in points:
			polygon.addPoint(point)
		return polygon
	px = [p.x for p in points]
	index = px.index(min(px))
	r0 = points[index]
	hull = [r0]
	r,u = r0,None
	remainingPoints = [x for x in points if x not in hull]
	while u != r0 and remainingPoints:
		u = random.choice(remainingPoints)
		for t in points:
			if	t != u and \
				(isRightTurn(r,u,t) or \
				(areThreePointsCollinear(r,u,t) and \
				pointToAngle(Point(u.x-r.x,u.y-r.y)) == pointToAngle(Point(t.x-u.x,t.y-u.y)))):
				u = t
		r = u
		points.remove(r)
		hull.append(r)
		if remainingPoints.count(r) > 0:
			remainingPoints.remove(r)
	polygon.addPoints(*hull)
	return polygon
		
		

def MakeRect(x, y, w, h):
	"""
	Convenience method to construct a L{Rect}.

	@param x: The x-coordinate.
	@type x: C{float}
	@param y: The y-coordinate.
	@type y: C{float}
	@param w: The width.
	@type w: Non-negative C{float}
	@param h: The height.
	@type h: Non-negative C{float}
	@return: A new Rect.
	@rtype: L{Rect}
	"""
	return Rect(Point(x,y), Size(w,h))

def PointZero():
	"""
	Returns a new L{Point} with values C{(0, 0)}.

	@return: A new Point with values C{(0, 0)}.
	@rtype: L{Point}
	"""
	return Point(0,0)

def SizeZero():
	"""
	Returns a new L{Size} with values C{(0, 0)}.

	@return: A new Size with values C{(0, 0)}.
	@rtype: L{Size}
	"""
	return Size(0,0)

def RectZero():
	"""
	Returns a new L{Rect} with values C{(0, 0, 0, 0)}.

	@return: A new Rect with values C{(0, 0, 0, 0)}.
	@rtype: L{Rect}
	"""
	return Rect(PointZero(), SizeZero())
#}


#{ Polygon functions.
def addPolygons(*polygons):
	"""
	Returns the smallest possible convex polygon which encompasses all points generated from pointwise addition of the polygons. (That is, it returns the convex hull of the Minkowski summation of the polygons.)

	@param polygons: The L{Polygon}C{s} to add up.
	@type polygons: C{comma-separated Polygons}
	@return: The smallest possible convex polygon which encompasses all the points.
	@rtype: L{Polygon}
	"""
	points = []
	for polygon1 in polygons:
		for polygon2 in polygons:
			if polygon1 == polygon2:
				continue
			for point1 in polygon1.getPoints():
				for point2 in polygon2.getPoints():
					points.append(pointAdd(point1,point2))
	return MakePolygon(*points)

def multiplyPolygons(*polygons):
	"""
	Returns the smallest possible convex polygon which encompasses all points generated from pointwise multiplication of the polygons. (That is, it returns the convex hull of the multiplication of the polygons.)

	@param polygons: The L{Polygon}C{s} to multiply.
	@type polygons: C{comma-separated Polygons}
	@return: The smallest possible convex polygon which encompasses all the points.
	@rtype: L{Polygon}
	"""
	points = []
	for polygon1 in polygons:
		for polygon2 in polygons:
			if polygon1 == polygon2:
				continue
			for point1 in polygon1.getPoints():
				for point2 in polygon2.getPoints():
					points.append(pointMult(point1,point2))
	return MakePolygon(*points)
#}


#{ Point arithmetic functions.
def pointAdd(*points):
	"""
	Adds up a series of L{Point}C{s} and returns a new Point that is the result.

	@param points: A series of Points.
	@type points: Comma-separated L{Point}C{s}
	@return: A Point with the result.
	@rtype: L{Point}
	"""
	p = PointZero()	# the additive identity
	for point in points:
		p.x += point.x
		p.y += point.y
	return p

def pointSub(p1, *points):
	"""
	Subtracts a series of L{Point}C{s} and returns a new Point that is the result.

	@param p1: The original point from which all other values will be subtracted.
	@type p1: L{Point}
	@param points: A series of Points.
	@type points: Comma-separated L{Point}C{s}
	@return: A Point with the result.
	@rtype: L{Point}
	"""
	p = p1.copy()
	for point in points:
		p.x -= point.x
		p.y -= point.y
	return p

def pointMult(*points):
	"""
	Multiplies a series of L{Point}C{s} by each other and returns a new Point that is the result.

	@param points: A series of Points.
	@type points: Comma-separated L{Point}C{s}
	@return: A Point with the result.
	@rtype: L{Point}
	"""
	p = Point(1, 1)	# the multiplicative identity
	for point in points:
		p.x *= point.x
		p.y *= point.y
	return p

def pointConstMult(point, value):
	"""
	Returns a new L{Point} whose value is the given Point multiplied by the given value.

	@param point: A Point.
	@type point: L{Point}
	@param value: The value by which the Point is multiplied.
	@type value: C{float}
	@return: A Point with the result.
	@rtype: L{Point}
	"""
	p = point.copy()
	p.x *= value
	p.y *= value
	return p

def pointNeg(point):
	"""
	Returns the a new L{Point} whose values are the negative of the given Point.

	@param point: The Point.
	@type point: L{Point}
	@return: A Point with the result.
	@rtype: L{Point}
	"""
	return Point(-point.x, -point.y)

def pointMid(p1, p2):
	"""
	Returns a new L{Point} whose values are the midpoint of the given Points.

	@param p1: A Point.
	@type p1: L{Point}
	@param p2: Another Point.
	@type p2: L{Point}
	@return: A Point with the result.
	@rtype: L{Point}
	"""
	return pointConstMult(pointAdd(p1,p2), 0.5)

def pointLength(point):
	"""
	Returns the distance of the given L{Point} from the origin (L{PointZero}).

	@param point: A point.
	@type point: L{Point}
	@return: The distance.
	@rtype: C{float}
	"""
	return math.sqrt(pointDot(point, point))

def pointDistance(p1, p2):
	"""
	Returns the distance between two Points.

	@param p1: A Point.
	@type p1: L{Point}
	@param p2: A Point.
	@type p2: L{Point}
	return: The distance between the two Points.
	@rtype: C{float}
	"""
	return pointLength(pointSub(p1, p2))
#}


#{ Point line functions.
def pointProjectToLine(p1, m, b):
	"""
	Projects a point onto a line (that is, it constructs a line perpendicular to the given line that intersects the given point, then returns where the given line and perpendicular line intersect).

	@param p1: The Point to project.
	@type p1: L{Point}
	@param m: The slope of the line.
	@type m: C{float}
	@param b: The y-intercept of the line.
	@type b: C{float}
	@return: A Point on the given line.
	@rtype: L{Point}
	"""
	x = (m*p1.y + p1.x - m*b) / (m*m + 1)
	y = (m*m*p1.y + m*p1.x + b) / (m*m + 1)
	return Point(x, y)

def pointProjectToLineWithPoints(p1, p2, p3):
	"""
	Projects a point onto a line (that is, it constructs a line perpendicular to the given line that intersects the given point, then returns where the given line and perpendicular line intersect).

	@param p1: The Point to project.
	@type p1: L{Point}
	@param p2: A Point on the line.
	@type p2: L{Point}
	@param p3: Another Point on the line.
	@type p3: L{Point}
	@return: The projected Point on the given line.
	@rtype: L{Point}
	"""
	m = (p3.y-p2.y)/(p3.x-p2.x)	# m = (y2-y1)/(x2-x1)
	b = p2.y - m*p2.x	# y = m*x + b	<==>	b = y - m*x
	return pointProjectToLine(p1, m, b)

def arePointsCollinear(*points):
	"""
	Returns whether or not the given L{Point}C{s} lie on the same line.

	@param points: A series of Points.
	@type points: Comma-separated L{Point}C{s}
	@return: Whether or not the given Points lie on the same line.
	@rtype: C{bool}
	"""
	if len(points) < 3:
		return True
	if len(points) == 3:
		return areThreePointsCollinear(p1,p2,p3)
	for i in range(0, len(points)-2):
		p1 = points[i]
		p2 = points[i+1]
		p3 = points[i+2]
		if not areThreePointsCollinear(p1, p2, p3):
			return False
	return True	

def areThreePointsCollinear(p1, p2, p3):
	"""
	Returns whether or not three points lie on the same line.

	@param p1: A Point.
	@type p1: L{Point}
	@param p2: Another Point.
	@type p2: L{Point}
	@param p3: A third Point.
	@type p3: L{Point}
	@return: Whether or not three points lie on the same line.
	@rtype: C{bool}
	"""
	line12 = getSlopeAndIntercept(p1,p2)
	m12 = line12[0]
	b12 = line12[1]
	line23 = getSlopeAndIntercept(p2,p3)
	m23 = line23[0]
	b23 = line23[1]
	line13 = getSlopeAndIntercept(p1,p3)
	m13 = line13[0]
	b13 = line13[1]
	if m12==m23==m13==None:	# if they're all vertical lines
		return True
	elif None in [m12,m23,m13]:		# else if at least one of the lines is vertical but not all of them are
		return False
	else:	# otherwise, none of the lines are vertical, so do normal comparison
		slopesAreEqual = 	abs(line12[0]-line23[0])<0.0000001 and \
							abs(line12[0]-line13[0])<0.0000001 and \
							abs(line23[0]-line13[0])<0.0000001
	if	slopesAreEqual and \
		abs(line12[1]-line23[1])<0.0000001 and \
		abs(line12[1]-line13[1])<0.0000001 and \
		abs(line23[1]-line13[1])<0.0000001:
		return True
	return False
	
def getSlopeAndIntercept(p1, p2):
	"""
	Returns the slope and intercept of the line which passes between two given points. It will return a list in the form [m, b] where m is the slope and b is the intercept. If it is a vertical line, it will return [None, None].

	@param p1: A Point.
	@type p1: L{Point}
	@param p2: Another Point.
	@type p2: L{Point}
	@return: The slope and intercept of the line in the form [m, b].
	@rtype: C{list}
	"""
	if p2.x==p1.x:
		return [None, None]
	m = (p2.y-p1.y)/(p2.x-p1.x)
	b = p2.y - m*p2.x
	return [m, b]

def getAngleBetweenLines(p1, p2, q1, q2):
	"""
	Returns the angle between two lines.

	@param p1: A Point on the line C{p}.
	@type p1: L{Point}
	@param p2: Another Point on the line C{p}.
	@type p2: L{Point}
	@param q1: A Point on the line C{q}.
	@type q1: L{Point}
	@param q2: A Point on the line C{q}.
	@type q2: L{Point}
	"""
	pVector = Point(p2.x-p1.x, p2.y-p1.y)
	qVector = Point(q2.x-q1.x, q2.y-q1.y)
	angle = math.atan2(pVector.y, pVector.x) - math.atan2(qVector.y, qVector.x)
	return -angle
#}


#{ Point geometry functions.
def pointDot(p1, p2):
	"""
	Returns the dot product of the given Points.

	@param p1: A Point.
	@type p1: L{Point}
	@param p2: Another Point.
	@type p2: L{Point}
	@return: The dot product.
	@rtype: C{float}
	"""
	return p1.x*p2.x + p1.y*p2.y

def pointCross(p1, p2):
	"""
	Returns the cross product of the given Points.

	@param p1: A Point.
	@type p1: L{Point}
	@param p2: Another Point.
	@type p2: L{Point}
	@return: The cross product.
	@rtype: C{float}
	"""
	return p1.x*p2.y - p1.y*p2.x

def pointPerp(point):
	"""
	Returns a new L{Point} which is perpendicular to the given point, rotated pi/2 radians counter-clockwise (that is, the new Point has the value C{(-y, x)}.

	@param point: A Point.
	@type point: L{Point}
	@return: A Point with the result.
	@rtype: L{Point}
	"""
	return Point(-point.y, point.x)

def pointRPerp(point):
	"""
	Returns a new L{Point} which is perpendicular to the given point, rotated pi/2 radians clockwise (that is, the new Point has the value C{(y, -x)}.

	@param point: A Point.
	@type point: L{Point}
	@return: A Point with the result.
	@rtype: L{Point}
	"""
	return Point(point.y, -point.x)

def pointProject(p1, p2):
	"""
	Returns the projection of p1 over p2.

	@param p1: A Point.
	@type p1: L{Point}
	@param p2: A Point.
	@type p2: L{Point}
	@return: A Point with the result.
	@rtype: L{Point}
	"""
	return pointConstMult(p2, pointDot(p1,p2) / pointDot(p2,p2))

def pointRotate(p1, p2):
	"""
	Returns a new L{Point} which is the rotation of the two given points.

	@param p1: A Point.
	@type p1: L{Point}
	@param p2: A Point.
	@type p2: L{Point}
	return: A Point with the result.
	@rtype: L{Point}
	"""
	return Point(p1.x*p2.x - p1.y*p2.y, p1.x*p2.y + p1.y*p2.x)

def pointUnrotate(p1, p2):
	"""
	Returns a new L{Point} which is the reversed rotation of the two given points.

	@param p1: A Point.
	@type p1: L{Point}
	@param p2: A Point.
	@type p2: L{Point}
	return: A Point with the result.
	@rtype: L{Point}
	"""
	return Point(p1.x*p2.x + p1.y*p2.y, p1.y*p2.x - p1.x*p2.y)

def pointNormalize(point):
	"""
	Returns a new L{Point} whose length is 1 (that is, the Point's unit vector).

	@param point: A Point.
	@type point: L{Point}
	@return: A Point with the result.
	@rtype: L{Point}
	"""
	return pointConstMult(point, 1.0/pointLength(point))

def pointForAngle(angle):
	"""
	Returns a new L{Point} whose length is 1 and has an angle as provided in radians (that is, a unit vector).

	@param angle: The angle (in radians) away from the x-axis.
	@type angle: C{float}
	@return: A Point with the result.
	@rtype: L{Point}
	"""
	return Point(math.cos(angle), math.sin(angle))

def pointToAngle(point):
	"""
	Returns the angle (in radians) of the vector from C{Point(0, 0)} to the given L{Point}.

	@param point: A Point.
	@type point: L{Point}
	@return: The angle in radians.
	@rtype: C{float}
	"""
	return math.atan2(point.y, point.x)
#}
