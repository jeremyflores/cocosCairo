from Geometry import *
from Node import *

class Scene(Node):
	"""
	The main type of L{Node} to which other Nodes are added. The L{Director} displays Scenes one at a time.
	"""
	def __init__(self):
		"""
		Initialization method. A Scene does not take in a L{Rect} since it is automatically sized by the L{Director}.
		"""
		Node.__init__(self)
		self._isAnchorPointRelative = False
		#self._gestureListeners = []
		#self._controllers = []	# there may be GestureListeners that are not Controllers
		self._isSetupComplete = False

	def _setDirector(self, director):
		Node._setDirector(self, director)
		if director is not None and self._isSetupComplete is not True:
			self.setup()	# only call this once
			self._isSetupComplete = True

	def setup(self):
		"""
		Override this method to set up your scene.
		"""
		pass
