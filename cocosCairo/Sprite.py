from Node import *
from Geometry import *
import gtk

class Sprite(Node):
	"""
	A L{Node} that renders an image (such as a JPEG or PNG) to the screen.
	"""
	def __init__(self, imageName=None, position=None):
		"""
		Initialization method.

		@param imageName: The filepath to the image.
		@type imageName: C{string}
		@param position: The position of the Node. Default is L{PointZero}.
		@type position: L{Point}
		"""
		Node.__init__(self)
		if position is not None:
			self.setPosition(position)
		self._pixbuf = None
		self._sourcePattern = None
		self.setImageName(imageName)

	def setImageName(self, imageName):
		"""
		Sets a new image by its filepath.

		@param imageName: The new filepath.
		@type imageName: C{string}
		"""
		if imageName is not None:
			self._sourcePattern = None
			self._pixbuf = gtk.gdk.pixbuf_new_from_file(imageName)
			self.setSize(Size(self._pixbuf.get_width(), self._pixbuf.get_height()))

	def draw(self, context):
		if not self._sourcePattern:
			context.set_source_pixbuf(self._pixbuf, 0, 0)
			self._sourcePattern = context.get_source()
		else:
			context.set_source(self._sourcePattern)
		context.paint_with_alpha(self.getOpacity())
		if self._color.a > 0.0:
			context.set_source_rgba(self._color.r, self._color.g, self._color.b, self._color.a)
			context.mask(self._sourcePattern)
