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
		self._gestureListeners = []
		self._controllers = []	# there may be GestureListeners that are not Controllers
		self._isSetupComplete = False

	def setDirector(self, director):
		Node.setDirector(self, director)
		if director is not None and self._isSetupComplete is not True:
			self.setup()	# only call this once
			self._isSetupComplete = True

	def addController(self, controller, zOrder=0):
		"""
		Adds an L{AbstractController} to the Scene. This method will parent the controller's Node to the Scene as well as automatically register it as a listener.

		@param controller: The controller to add.
		@type controller: L{AbstractController}
		@param zOrder: The zOrder of the controller's L{Node}.
		@type zOrder: C{int}
		"""
		if controller not in self._controllers:
			node = controller.getNode()
			if node is not None:
				self.addChild(node, zOrder)
			controller._parent = self
			self._controllers.append(controller)
		self.addGestureListener(controller)

	def removeController(self, controller):
		"""
		Removes a Controller from the Scene. This method will deparent the controller's Node from the Scene as well as automatically unregister it as a listener.

		@param controller: The controller to remove.
		@type controller: L{AbstractController}
		"""
		if controller in self._controllers:
			node = controller.getNode()
			if node is not None:
				self.removeChild(node)
			controller._parent = None
			self._controllers.remove(controller)
		self.removeGestureListener(controller)

	def addGestureListener(self, listener):
		"""
		Adds a L{GestureListener} to the Scene, which will be registered to the L{GestureDispatch} when the Scene is entered.

		@param listener: A new listener.
		@type listener: L{GestureListener}
		"""
		if listener not in self._gestureListeners:
			self._gestureListeners.append(listener)
			if self.getDirector() is not None:
				self.getDirector().getGestureDispatch().addListener(listener)

	def removeGestureListener(self, listener):
		"""
		Removes a L{GestureListener} to the Scene, which will be unregistered from the L{GestureDispatch} when the Scene is exited.

		@param listener: The listener to be removed.
		@type listener: L{GestureListener}
		"""
		if listener in self._gestureListeners:
			self._gestureListeners.remove(listener)
			if self.getDirector() is not None:
				self.getDirector().getGestureDispatch().removeListener(listener)

	def onEnter(self):
		gestureDispatch = self.getDirector().getGestureDispatch()
		for listener in self._gestureListeners:
			gestureDispatch.addListener(listener)
		Node.onEnter(self)

	def onExit(self):
		gestureDispatch = self.getDirector().getGestureDispatch()
		for listener in self._gestureListeners:
			gestureDispatch.removeListener(listener)
		Node.onExit(self)

	def setup(self):
		"""
		Override this method to set up your scene.
		"""
		pass
