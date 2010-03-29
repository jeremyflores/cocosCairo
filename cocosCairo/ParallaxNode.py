"""
Creates a parallax effect.
"""
from Node import *

class ParallaxNode(Node):
	"""
	Creates a parallax effect for any attached children.
	"""
	def __init__(self):
		Node.__init__(self)
		self._lastPosition = None
		self._parallaxDict = {}	# entries are of the form "child : [ratio, offset]"

	def addChild(self, child, zOrder=0, ratio=None, offset=None):
		"""
		Adds a child to the ParallaxNode.

		@param child: The child Node to add.
		@type child: L{Node}
		@param zOrder: The z-order of the child.
		@type zOrder: C{int}
		@param ratio: The ratio at which the child will move relative to the ParallaxNode. Default is C{Point(1.0, 1.0)}.
		@type ratio: L{Point}
		@param offset: Its offset from the ParallaxNode's origin. Default is L{PointZero}.
		@type offset: L{Point}
		"""
		if child in self._parallaxDict:	# if the child is already parented to the ParallaxNode
			return							# then don't do anything
		if ratio is None:
			ratio = Point(1.0, 1.0)
		if offset is None:
			offset = Point(0.0, 0.0)
		self._parallaxDict[child] = [ratio, offset]
		position = self.getPosition()
		x = position.x * ratio.x + offset.x
		y = position.y * ratio.y + offset.y
		child.setPosition(Point(x,y))
		Node.addChild(self, child, zOrder)

	def _detachChild(self, child, shouldCleanup):
		if child in self._parallaxDict:
			del self._parallaxDict[child]
		Node._detachChild(self, child, shouldCleanup)

	def _visit(self, context):
		currentAbsolutePosition = self.getAbsolutePosition()
		if self._lastPosition is None or currentAbsolutePosition != self._lastPosition:
			for child in self._parallaxDict:
				ratio = self._parallaxDict[child][0]
				offset = self._parallaxDict[child][1]
				x = -currentAbsolutePosition.x + currentAbsolutePosition.x*ratio.x + offset.x
				y = -currentAbsolutePosition.y + currentAbsolutePosition.y*ratio.y + offset.y
				child.setPosition(Point(x,y))
			self._lastPosition = currentAbsolutePosition
		Node._visit(self, context)
