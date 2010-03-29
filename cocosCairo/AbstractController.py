"""
The controller in the model-view-controller design pattern.
"""

from Node import *
from GestureListener import *
from AbstractModel import *

class AbstractController(GestureListener):
	"""
	The controller in the model-view-controller design pattern. Subclass this and override methods as needed to handle L{GestureEvent}s and to facilitate model-view communications.
	"""
	def __init__(self, node=None, model=None):
		"""
		Initialization method.

		@param node: The Node which this controls, or C{None} if not defined.
		@type node: L{Node} (or C{None})
		@param model: The model for the Node, or C{None} if not defined.
		@type model: L{AbstractModel} (or C{None})
		"""
		self._node = None
		self._model = None
		self._parent = None	# the parent Node
		self._controllers = []
		if node is not None:
			self.setNode(node)
		if model is not None:
			self.setModel(model)

#{ Accessor methods.
	def getNode(self):
		"""
		Returns the Node for this controller. If a Node has not yet been assigned, it will return C{None}.

		@return: The Node.
		@rtype: L{Node} (or C{None})
		"""
		return self._node

	def setNode(self, node):
		"""
		Sets the controller's L{Node}. It will automatically register the view with the L{AbstractModel}, if one has been set for this controller. Also, if there was previously a parented Node, the new Node will become a child of that parent and will inherit the same zOrder as its predecessor. By default, the parent is the L{Scene} to which this C{Controller} has been added.

		@param node: The node.
		@type node: L{Node}
		"""
		parent = self._parent
		zOrder = 0 # default
		if self._node is not None:
			zOrder = self._node.getZOrder()
			parent = self._node.getParent()
			if self._model is not None:
				self._model.removeListener(self._node)
			if parent is not None:
				parent.removeChild(self._node, True)
			for controller in self._controllers:
				self._node.removeController(controller)
		self._node = node
		self._node._controller = self
		for controller in self._controllers:
			self._node.addController(controller)
		if self._model is not None:
			self._model.addListener(self._node)
			self._model.notifyListener(self._node)	# update the node with the model info
		if parent is not None:
			parent.addChild(self._node, zOrder)

	def getModel(self):
		"""
		Returns the model for this Node. If a Model has not yet been assigned, it will return C{None}.

		@return: The model.
		@rtype: L{AbstractModel} (or C{None})
		"""
		return self._model

	def setModel(self, model):
		"""
		Sets the model for this controller. If the L{Node} has been defined, it will unregister the Node from listening to the previous model (if it exists), then it will register the Node to listen to the new model. When the model changes, it will call L{Node.onModelChange}.

		@param model: The new model.
		@type model: L{AbstractModel}
		"""
		if self._model is not None:
			if self._node is not None:
				self._model.removeListener(self._node)
		self._model = model
		if self._node is not None:
			self._model.addListener(self._node)
			self._model.notifyListener(self._node)	# update the node with the model info

	def getDirector(self):
		"""
		Returns the L{Director} of the controller's L{Node}. This will return C{None} if there is currently no Node or if the Node has not yet been attached to the Director.

		@return: The director.
		@rtype: L{Director}
		"""
		if self._node is not None:
			return self._node.getDirector()
		else:
			return None
#}


#{ Controller methods.
	def addController(self, controller):
		if controller not in self._controllers:
			if self.getNode() is not None:
				self.getNode().addController(controller)
			self._controllers.append(controller)

	def removeController(self, controller):
		if controller in self._controllers:
			if self.getNode() is not None:
				self.getNode().removeController(controller)
			self._controllers.remove(controller)
#}


#{ Gesture control methods inherited from GestureListener (repeated here for emphasis). Override as desired.
	def onMousePress(self, event):
		pass
	def onMouseMotion(self, event):
		pass
	def onMouseRelease(self, event):
		pass
	def onMouseDoublePress(self, event):
		pass
	def onMouseScroll(self, event):
		pass
	def onKeyPress(self, event):
		pass
	def onKeyRelease(self, event):
		pass
#}
