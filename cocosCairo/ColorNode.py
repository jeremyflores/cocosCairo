from Node import *
from Color import *

class ColorNode(Node):
	"""
	A Node which fills its bounding box with a certain L{Color}. (Note that the ColorNode merely uses the backgroundColor to render the color, so setting the backgroundColor will actually be setting the ColorNode's color and vice versa).
	"""
	def __init__(self, rect=None, color=None):
		"""
		Initialization method. If a L{Color} is not provided, the default will be a L{BlackColor}.

		@param rect: The rect of the Node.
		@type rect: L{Rect}
		@param color: The color.
		@type color: L{Color}
		"""
		Node.__init__(self, rect)
		if color is None:
			color = BlackColor()
		self.setColor(color)

	def getColor(self):
		"""
		Returns the ColorNode's color.

		@return: The color.
		@rtype: L{Color}
		"""
		return self.getBackgroundColor()

	def setColor(self, color):
		"""
		Sets the ColorNode's color.

		@param color: The color.
		@type color: L{Color}
		"""
		self.setBackgroundColor(color)

	def getOpacity(self):
		"""
		Returns the opacity of this Node (that is, the L{Color}'s alpha value).

		@return: The opacity.
		@rtype: C{float}
		"""
		return self.getColor().a

	def setOpacity(self, opacity):
		"""
		Sets the opacity of this Node (that is, the L{Color}'s alpha value).

		@param opacity: The opacity.
		@type opacity: C{float} between C{0.0} and C{1.0}
		"""
		color = self.getColor()
		color.a = opacity
		self.setColor(color)
