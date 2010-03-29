"""
The base class for rendering items to the screen.
"""

from Geometry import *
from Color import *

from Timer import *
from AbstractModel import *

import warnings

# TODO: add a convenience method to get and set the absolute position (that is, relative to the top-left of the screen).
# TODO: possibly add some translation stuff so that the origin is at the bottom-left (and NOT top-left) of the screen.

class Node(ModelListener):
	"""
	The base class for rendering items to the screen.

	Note that the position is set relative to the Node's parent. If the Node's parent is the L{Director}, the position is relative to the top-left corner of the screen (in general, this should only apply to L{Scene}C{s}).
	"""
	def __init__(self, rect=None):
		"""
		Initialization method.

		@param rect: The bounding box for the Node. By default, the bounding box is L{RectZero}.
		@type rect: L{Rect} (or C{None})
		"""
		self._transformAnchor = PointZero()
		self._anchorPoint = PointZero()
		self._isAnchorPointRelative = True	# Scenes and Layers should be set to False

		self._position = PointZero()
		self._size = SizeZero()
		if rect is not None:
			self.setRect(rect)

		self._zOrder = 0
		self._isVisible = True
		self._backgroundColor = ClearColor()

		self._rotation = 0.0
		self._scaleX = 1.0
		self._scaleY = 1.0
		self._userData = None
		self._tag = ""

		self._children = []
		self._parent = None
		self._director = None
		self._isRunning = False
		self._controller = None
		self._color = ClearColor()	# convenience color for subclasses that use foreground coloring
		self._opacity = 1.0		# used by subclasses that support opacity
		self._scheduledTimers = {}

		self._gestureListeners = []
		self._controllers = []	# there may be GestureListeners that are not Controllers

#{ Appearance methods.
	def getOpacity(self):
		"""
		Returns the opacity for Node subclasses that use it. Default is C{1.0}.

		@return: The opacity.
		@rtype: C{float}
		"""
		return self._opacity

	def setOpacity(self, opacity):
		"""
		Sets the opacity for Node subclasses that use it. This should be set between C{0.0} (fully transparent) and C{1.0} (fully opaque).

		@param opacity: The opacity.
		@type opacity: C{float}
		"""
		self._opacity = opacity

	def getZOrder(self):
		"""
		The z-order of this current Node in relation to other Nodes.

		@return: The z-order.
		@rtype: C{int} (or possibly C{float})
		"""
		return self._zOrder

	def setZOrder(self, zOrder):
		"""
		Sets the z-order of this current Node in relation to other Nodes. Children are drawn in order relative to this z-order. Default is C{0}.

		@param zOrder: The z-order.
		@type zOrder: C{int} (or C{float})
		"""
		self._zOrder = zOrder

	def isVisible(self):
		"""
		Whether or not this Node and its children are visible. Default is C{True}.

		@return: Whether or not this Node and its children are visible.
		@rtype: C{bool}
		"""
		return self._isVisible

	def setVisible(self, isVisible):
		"""
		Whether or not this node and its children are visible. Default is C{True}.

		@param isVisible: Whether or not this node and its children are visible.
		@type isVisible: C{bool}
		"""
		self._isVisible = isVisible

	def getBackgroundColor(self):
		"""
		The background color of this Node. Default is L{ClearColor}.

		@return: The background color.
		@rtype: L{Color}
		"""
		return self._backgroundColor

	def setBackgroundColor(self, backgroundColor):
		"""
		Background color for the node. Default is C{Color(0,0,0,0)} (i.e. the background is fully transparent). Any child with a zOrder less than the node's zOrder will appear behind the background.

		@param backgroundColor: The background color.
		@type backgroundColor: L{Color}
		"""
		self._backgroundColor = backgroundColor.copy()

	def getRotation(self):
		"""
		The current angle at which this Node is rotated. Default is C{0.0}.

		@return: The current rotation angle in radians.
		@rtype: C{float}
		"""
		return self._rotation

	def setRotation(self, rotation):
		"""
		The rotation angle in radians. Default is C{0.0}.

		@param rotation: The rotation angle in radians.
		@type rotation: C{float}
		"""
		self._rotation = rotation

	def getScaleX(self):
		"""
		The scale factor for the X dimension. Default is C{1.0}.

		@return: Scale factor.
		@rtype: C{float}
		"""
		return self._scaleX

	def setScaleX(self, scaleX):
		"""
		Scale factor for the X dimension. Default is C{1.0}.

		@param scaleX: Scale factor for the X dimension.
		@type scaleX: C{float}
		"""
		self._scaleX = scaleX

	def getScaleY(self):
		"""
		The scale factor for the Y dimension. Default is C{1.0}.

		@return: Scale factor.
		@rtype: C{float}
		"""
		return self._scaleY

	def setScaleY(self, scaleY):
		"""
		Scale factor for the Y dimension. Default is C{1.0}.

		@param scaleY: Scale factor for the Y dimension.
		@type scaleY: C{float}
		"""
		self._scaleY = scaleY

	def getColor(self):
		"""
		Returns the foreground color for Node subclasses that use it. Default is L{ClearColor}.

		@return: The foreground color.
		@rtype: L{Color}
		"""
		return self._color.copy()

	def setColor(self, color):
		"""
		Method for children who have color foregrounds for, e.g. tinting (like L{Sprite}C{s}).

		@param color: L{Color}.
		"""
		self._color = color.copy()

	def setColors(self, r, g, b, a=1.0):
		"""
		Method for children who have color foregrounds for, e.g. tinting (like L{Sprite}C{s}).

		@param r: C{float}.
		@param g: C{float}.
		@param b: C{float}.
		@param a: C{float}.
		"""
		self._color = Color(r, g, b, a)

	def getScale(self):
		"""
		Returns the scale amount if both scaleX and scaleY are equal. If they are not equal, it will raise a warning and only return scaleX.

		@return: Scale amount.
		@rtype: C{float}
		"""
		if self._scaleX != self._scaleY:
			warnings.warn("scaleX and scaleY have different values. Returning scaleX.")
		return self._scaleX

	def setScale(self, scale):
		"""
		Set the scale amount for both the x-axis and y-axis.

		@param scale: How much to scale this node.
		@type scale: C{float}
		"""
		self._scaleX = scale
		self._scaleY = scale
#}


#{ Information methods.
	def getUserData(self):
		"""
		Any peripheral data the user wishes to attach. Default is C{None}.

		@return: User data.
		@rtype: C{User defined}
		"""
		return self._userData

	def setUserData(self, userData):
		"""
		Any peripheral data the user wishes to attach. Default is C{None}.

		@param userData: Peripheral data.
		@type userData: C{User defined}.
		"""
		self._userData = userData

	def getTag(self):
		"""
		A convenience string with which to identify this Node. Default is the empty string.

		@return: Convenience string.
		@rtype: C{string}
		"""
		return self._tag

	def setTag(self, tag):
		"""
		A convenience string with which to identify this Node.

		@param tag: The tag with which to identify this Node.
		@type tag: C{string}.
		"""
		self._tag = tag
#}


#{ Director methods.
	def getDirector(self):
		"""
		A convenience method to get the L{Director} of the application. If this Node has not yet been parented to a running L{Scene}, this will return C{None}.

		@return: The Director of the application.
		@rtype: L{Director} (or C{None})
		"""
		return self._director

	def _setDirector(self, director):
		"""
		Sets the L{Director} of the application. This method is used automatically and should not normally be called manually.

		@param director: The Director of the application.
		@type director: L{Director}
		"""
		self._director = director
		for child in self.getChildren():
			child._setDirector(director)
#}


#{ Geometry methods.
	def getPosition(self):
		'''
		Get the current position of the Node relative to its parent.

		@return: Current position.
		@rtype: L{Point}
		'''
		return self._position.copy()

	def setPosition(self, position):
		'''
		Sets the current position of the Node relative to its parent.

		@param position: L{Point}.
		'''
		self._position = position.copy()

	def getAbsolutePosition(self):
		"""
		Returns the absolute position of this Node.

		@return: The absolute position of this Node.
		@rtype: L{Point}
		"""
		position = self.getPosition()
		node = self
		while node.getParent() is not None:
			node = node.getParent()
			position = pointAdd(position, node.getPosition())
		return position

	def getSize(self):
		'''
		Returns the size of this Node.

		@return: Size.
		@rtype: L{Size}
		'''
		return self._size.copy()

	def setSize(self, size):
		"""
		Sets the size of the Node.

		@param size: L{Size}.
		"""
		self._size = size.copy()
		anchorPoint = self._anchorPoint
		transformAnchor = Point(self._size.width*anchorPoint.x, self._size.height*anchorPoint.y)
		self.setTransformAnchorPoint(transformAnchor)

	def getRect(self):
		"""
		Returns the bounding box for the Node.

		@return: The bounding box.
		@rtype: L{Rect}
		"""
		x = self._position.x - self._size.width*self.getAnchorPoint().x
		y = self._position.y - self._size.height*self.getAnchorPoint().y
		return MakeRect(x, y, self._size.width, self._size.height)

	def setRect(self, rect):
		"""
		Sets the rectangle for the Node. Note that the node or its children may be drawn outside this rectangle (i.e. they will not be clipped).

		@param rect: L{Rect}.
		"""
		self.setPosition(rect.point)
		self.setSize(rect.size)

	def getAnchorPoint(self):
		"""
		How the Node is displayed relative to its position. See L{setAnchorPoint} for a description.

		@return: Anchor point.
		@rtype: L{Point}
		"""
		return self._anchorPoint.copy()

	def setAnchorPoint(self, anchorPoint):
		"""
		Sets how the Node is displayed on the screen relative to its position. E.g. C{Point(0,0)} means that the Node will be drawn with its top left-most corner at the position, C{Point(1,1)} means that the Node will be drawn with its bottom right-most corner at the position, and C{Point(0.5, 0.5)} means that the Node will be drawn with its center at the position.

		@param anchorPoint: L{Point}, with both C{0 <= x <= 1} and C{0 <= y <= 1}.
		"""
		self._anchorPoint = anchorPoint.copy()
		transformAnchor = Point(self._size.width*self._anchorPoint.x, self._size.height*self._anchorPoint.y)
		self.setTransformAnchorPoint(transformAnchor)

	def getTransformAnchorPoint(self):
		"""
		Returns how the Node is transformed relative to its position.

		@return: Transform anchor.
		@rtype: L{Point}
		"""
		return self._transformAnchor.copy()

	def setTransformAnchorPoint(self, anchorPoint):
		"""
		Sets how the Node is transformed relative to its position.

		@param anchorPoint: L{Point}, with both C{0 <= x <= 1} and C{0 <= y <= 1}.
		"""
		self._transformAnchor = anchorPoint.copy()
#}


#{ Parenting methods.
	def getParent(self):
		"""
		Returns the parent Node of this Node.
		
		@return: The parent of this node or None if there is no parent.
		@rtype: C{Node} (or C{None})
		"""
		return self._parent

	def getChildren(self):
		"""
		Returns a list of children.

		@return: List of children.
		@rtype: C{List}
		"""
		return self._children

	def getChildByTag(self, tag):
		"""
		Returns a child C{Node} whose tag matches the given C{string}. If the child is not found, this will return C{None}.

		@param tag: The child's tag.
		@type tag: C{string}
		@return: A child C{Node} if the child is found, C{None} otherwise.
		@rtype: C{Node} (or C{None})
		"""
		for child in self.getChildren():
			if child.getTag() == tag:
				return child
		return None

	def addChild(self, child, zOrder=None, tag=None):
		"""
		Adds a child C{Node} to this node.

		@param child: The child to add.
		@type child: C{Node}
		@param zOrder: The zOrder at which the child will be added. Default is the child's current zOrder.
		@type zOrder: C{int}
		@param tag: A tag ID by which to reference the child. Default is the child's current tag.
		@type tag: C{str}
		"""
		if child._parent != None:
			warnings.warn("Failed to add child. Child must not have a parent.")
			return

		if zOrder is None:
			zOrder = child.getZOrder()
		if tag is None:
			tag = child.getTag()
		self._insertChild(child, zOrder)
		child.setTag(tag)
		child._parent = self
		child._setDirector(self.getDirector())
		if self._isRunning:
			child.onEnter()

	def reorderChild(self, child, zOrder):
		"""
		Changes the zOrder of a child of this node.

		@param child: The child to add.
		@type child: C{Node}
		@param zOrder: The zOrder at which the child will be added.
		@type zOrder: C{int}
		"""
		if child in self._children:
			self._children.remove(child)
		self._insertChild(child, zOrder)

	def _insertChild(self, child, zOrder):
		"""
		Private method. Inserts a child into the Node's child list, which is sorted by the children's zOrders.

		@param child: The Node to add.
		@type child: C{Node}
		@param zOrder: The zOrder at which the child will be added.
		@type zOrder: C{int}
		"""
		def comparator(child1, child2):
			if child1.getZOrder() > child2.getZOrder():
				return 1
			elif child1.getZOrder() == child2.getZOrder():
				return 0
			else:
				return -1
		child.setZOrder(zOrder)
		self._children.append(child)
		self._children.sort(comparator)

	def removeChild(self, child, shouldCleanup=True):
		"""
		Removes a child C{Node} from this node.
		
		@param child: The child to add.
		@type child: C{Node}
		@param shouldCleanup: Whether or not the child and its children should be cleaned up, i.e. stopping actions and removing all Timer callbacks. Default is True.
		@type shouldCleanup: C{bool}
		"""
		if child in self._children:
			self._detachChild(child, shouldCleanup)

	def removeChildByTag(self, tag, shouldCleanup=True):
		"""
		Removes a child C{Node} from this node as identified by its tag.
		
		@param tag: The child's unique identifier.
		@type tag: C{str}
		@param shouldCleanup: Whether or not the child and its children should be cleaned up, i.e. stopping actions and removing all Timer callbacks. Default is True.
		@type shouldCleanup: C{bool}
		"""
		child = self.getChildByTag(tag)
		if child:
			self.removeChild(child, tag)

	def removeAllChildren(self, shouldCleanup=True):
		"""
		Removes all children from this node.

		@param shouldCleanup: Whether or not the child and its children should be cleaned up, i.e. stopping actions and removing all Timer callbacks. Default is True.
		@type shouldCleanup: C{bool}
		"""
		for child in self._children:
			self._detachChild(child, shouldCleanup)

	def _detachChild(self, child, shouldCleanup):
		if self._isRunning:
			child.onExit()
		if shouldCleanup:
			child._cleanup()
		child._parent = None
		child._setDirector(None)
		self._children.remove(child)
#}


#{ Controller methods.
	def getController(self):
		"""
		Returns the controller of this Node. Default is C{None} if it is not defined.

		@return: The controller of this Node.
		@rtype: L{AbstractController} (or C{None})
		"""
		return self._controller

	def addController(self, controller):
		"""
		Adds an L{AbstractController} to the Scene. This method will parent the controller's Node to the Scene as well as automatically register it as a listener.

		@param controller: The controller to add.
		@type controller: L{AbstractController}
		"""
		if controller not in self._controllers:
			node = controller.getNode()
			if node is not None:
				self.addChild(node)
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
#}


#{ Drawing methods.
	def draw(self, context):
		"""
		Draws the Node's contents to be displayed on the screen. Subclass and do your drawing in here. The context will already be translated to the node's current position, so drawing to C{Point(0,0)} will actually render to L{getPosition}.
		
		@param context: A Cairo context clipped to the dirtied rectangle.
		"""
		pass

	def _visit(self, context):
		"""
		Private method that is called by its parent whenever the node (and its children) need to be redrawn. Do not call this method directly as the L{Director} and L{GTKInterface} handle the redrawing.

		@param context: The Cairo context.
		"""
		# if this node is not visible, then don't draw this node or any of its children
		if not self.isVisible():
			return

		# push a new context onto the stack to transform
		context.save()

		# do any transformations here
		self._transform(context)

		# first draw any children that are behind this node
		for child in self._children:
			if child.getZOrder() < 0:
				child._visit(context)

		# then draw this node
		color = self._backgroundColor
		context.set_source_rgba(color.r, color.g, color.b, color.a)
		context.rectangle(0, 0, self._size.width, self._size.height)
		context.fill()	# first draw the background color
		self.draw(context)	# then do any user-defined drawing

		# finally, draw any children parallel or in front of this node
		for child in self._children:
			if child.getZOrder() >= 0:
				child._visit(context)

		# pop the new context off the stack before continuing.
		context.restore()


	def _transform(self, context):
		"""
		Private method that is called by C{_visit}. Performs transforms onto the current context (e.g. rotation, scaling).

		@param context: The Cairo context.
		"""

		transformAnchor = self.getTransformAnchorPoint()
		position = self.getPosition()

		# translate to the new position in which to scale and rotate.
		offset = self._getTransformOffset()
		context.translate(offset.x, offset.y)

		# rotate
		if (self._rotation != 0.0):
			context.rotate(self._rotation)

		# scale
		if (self._scaleX != 1.0 or self._scaleY != 1.0):
			context.scale(self._scaleX, self._scaleY)

		# translate back to original point before moving on
		if transformAnchor.x != 0.0 or transformAnchor.y != 0.0:
			context.translate(-transformAnchor.x, -transformAnchor.y)
		#if transformAnchor.x != 0.0 or transformAnchor.y != 0.0:
		#	context.translate(-position.x-transformAnchor.x, -position.y-transformAnchor.y)
		#elif position.x != 0.0 or position.y != 0.0:
		#	context.translate(-position.x, -position.y)

	def _getTransformOffset(self):
		"""
		Private method for performing a translation on the current context.
		"""
		transformAnchor = self.getTransformAnchorPoint()
		position = self.getPosition()
		offsetX = 0
		offsetY = 0
		if self._isAnchorPointRelative and (transformAnchor.x != 0.0 or transformAnchor.y != 0.0):
			offsetX -= transformAnchor.x
			offsetY -= transformAnchor.y
		if transformAnchor.x != 0.0 or transformAnchor.y != 0.0:
			offsetX += position.x + transformAnchor.x
			offsetY += position.y + transformAnchor.y
		elif position.x != 0.0 or position.y != 0.0:
			offsetX += position.x
			offsetY += position.y
		return Point(offsetX, offsetY)
#}


#{ Scene management.
	def onEnter(self):
		"""
		Called when this node will first be displayed. Override to have custom behaviors.
		"""
		gestureDispatch = self.getDirector().getGestureDispatch()
		for listener in self._gestureListeners:
			gestureDispatch.addListener(listener)
		for child in self._children:
			child.onEnter()
		self.activateTimers()
		self._isRunning = True

	def onEnterFromFinishedTransition(self):
		"""
		Called if there was a L{Transition}. Override to have custom behaviors.
		"""
		for child in self._children:
			child.onEnterFromFinishedTransition()

	def onExit(self):
		"""
		Called when this node will no longer be displayed. Override to have custom behaviors.
		"""
		gestureDispatch = self.getDirector().getGestureDispatch()
		for listener in self._gestureListeners:
			gestureDispatch.removeListener(listener)
		self.deactivateTimers()
		self._isRunning = False
		for child in self._children:
			child.onExit()
#}


#{ Timer methods.
	def activateTimers(self):
		"""
		Activates any L{Timer}C{s} that this Node has.
		"""
		for callback in self._scheduledTimers:
			timer = self._scheduledTimers[callback]
			scheduler = self.getDirector().getScheduler()
			scheduler.schedule(timer)
		actionManager = self.getDirector().getActionManager()
		actionManager.resumeAllActions(self)

	def deactivateTimers(self):
		"""
		Deactivates any L{Timer}C{s} that this Node has.
		"""
		for callback in self._scheduledTimers:
			timer = self._scheduledTimers[callback]
			scheduler = self.getDirector().getScheduler()
			scheduler.unschedule(timer)
		actionManager = self.getDirector().getActionManager()
		actionManager.pauseAllActions(self)

	def scheduleCallback(self, callback, interval=0):
		"""
		Registers a function to be called every C{interval} seconds.

		@requires: This method should only be used by a subclass. If you wish to create a timer, see L{Timer} and L{Scheduler}.

		@param callback: The method to be called by the L{Scheduler}.
		@type callback: Python C{function}
		@param interval: How often (in seconds) the C{callback} should be called.
		@type interval: Non-negative C{float}
		"""
		if callback in self._scheduledTimers:
			return
		if interval < 0.0:
			return

		timer = Timer(callback, interval)
		if self._isRunning:
			scheduler = self.getDirector().getScheduler()
			scheduler.schedule(timer)

		self._scheduledTimers[callback] = timer

	def unscheduleCallback(self, callback):
		"""
		Removes a C{callback} that has been added via L{scheduleCallback}.

		@param callback: The scheduled callback to unschedule.
		@type callback: C{function}
		"""
		if callback not in self._scheduledTimers:
			return

		timer = self._scheduledTimers[callback]
		del self._scheduledTimers[callback]

		if self._isRunning:
			scheduler = self.getDirector().getScheduler()
			scheduler.unschedule(timer)

	def getIntervalForScheduledCallback(self, callback):
		"""
		Returns how often (in seconds) the callback will be called (or C{None} if the callback is not currently scheduled).

		@param callback: The scheduled callback.
		@type callback: C{function}
		@return: The interval for the callback.
		@rtype: C{float} (or C{None})
		"""
		if callback not in self._scheduledTimers:
			return None
		return self._scheduledTimers[callback].getInterval()

	def setIntervalForScheduledCallback(self, callback, interval):
		"""
		Sets how often (in seconds) the callback will be called.

		@param callback: The scheduled callback.
		@type callback: C{function}
		@param interval: How often (in seconds) the C{callback} should be called.
		@type interval: Non-negative C{float}
		"""
		if callback not in self._scheduledTimers:
			return
		timer = self._scheduledTimers[callback]
		timer.setInterval(interval)
#}


#{ Action methods.
	def runAction(self, action):
		"""
		Runs an L{Action} on this Node.
		"""
		if self.getDirector() is not None:
			actionManager = self.getDirector().getActionManager()
			actionManager.addAction(action, self, (not self._isRunning))
			return action
		else:
			return None

	def stopAllActions(self):
		"""
		Stops all L{Action}C{s} currently running on this Node.
		"""
		actionManager = self.getDirector().getActionManager()
		actionManager.removeAllActions(self)

	def stopAction(self, action):
		"""
		Stops a particular L{Action} currently running on this Node.
		"""
		actionManager = self.getDirector().getActionManager()
		actionManager.removeAction(action)

	def stopActionByTag(self, tag):
		"""
		Stops a particular L{Action} currently running on this Node.

		@param tag: The tag of the Node.
		@type tag: C{string}
		"""
		actionManager = self.getDirector().getActionManager()
		actionManager.removeActionByTag(tag, self)

	def getActionByTag(self, tag):
		"""
		Gets a particular L{Action} currently running on this Node. If the Action cannot be found, it will return C{None}.

		@param tag: The tag of the Node.
		@type tag: C{string}
		@return: The Action.
		@rtype: L{Action} (or C{None})
		"""
		actionManager = self.getDirector().getActionManager()
		return actionManager.getActionByTag(tag, self)

	def numberOfRunningActions(self):
		"""
		Returns the number of L{Action}C{s} currently running on this Node.
	
		@return: Number of running actions.
		@rtype: C{int}
		"""
		actionManager = self.getDirector().getActionManager()
		return actionManager.getNumberOfRunningActions(self)
#}


#{ Cleanup
	def _cleanup(self):
		"""
		Private method used by Node. Stops all actions for the Node, clears out any scheduled timers, and tells its children to do the same.
		"""
		self.stopAllActions()
		self._scheduledTimers = {}
		for child in self._children:
			child._cleanup()
#}
