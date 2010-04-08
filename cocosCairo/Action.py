"""
Basic Actions which can be performed on Nodes.
"""

class AbstractAction:
	"""
	The base class for all Actions. An Action is a convenience class used to perform some task over a period of time (or instantaneously). Actions usually perform some task on an object, which is referred to as the Action's "owner". The owner should typically be a L{Node}.
	"""
	def __init__(self):
		self._originalOwner = None
		self._owner = None
		self._tag = None

#{ Accessor methods.
	def getTag(self):
		"""
		Returns the tag of this Action. A tag is used as a convenience to be able to uniquely identify this Action versus other Actions. If the tag has not yet been defined, it will return C{None}.

		@return: A tag.
		@rtype: C{string} (or C{None} if not yet defined)
		"""
		return self._tag

	def setTag(self, tag):
		"""
		Sets the tag of this Action.

		@param tag: A tag.
		@type tag: C{string}
		"""
		self._tag = tag

	tag = property(getTag, setTag, doc="The tag of this Action.")

	def getOriginalOwner(self):
		"""
		Returns the owner of the Action when the Action is started via L{start}. (When the Action is stopped via L{stop}, it will no longer have an owner.) If the owner has not yet been defined, it will return C{None}.

		@return: The original owner.
		@rtype: C{defined by subclasses} (or C{None} if not yet defined)
		"""
		return self._originalOwner

	originalOwner = property(getOriginalOwner, doc="Read-only access to the owner of the Action when the Action is started.")

	def getOwner(self):
		"""
		Returns the owner of the Action. If this is called while the Action is still running (that is, after L{start} has been called but before L{stop} has been called), it will return the owner which the Action is modifying. Otherwise, it will return C{None}.

		@return: The owner of the Action.
		@rtype: C{defined by subclasses} (or C{None} if the action is not running)
		"""
		return self._owner

	def setOwner(self, owner):
		"""
		Sets the owner of the Action. This should not normally be called manually as L{start} and L{ActionManager} take care of this information automatically.

		@param owner: The owner of the Action.
		@type owner: C{defined by subclasses}
		"""
		self._owner = owner

	owner = property(getOwner, setOwner, doc="The current owner of the Action.")
#}


#{ Running methods.
	def start(self, owner):
		"""
		Starts the Action.

		@param owner: The C{object} which the Action will modify.
		@type owner: C{defined by subclasses}
		"""
		self._originalOwner = owner
		self._owner = owner

	def stop(self):
		"""
		Stops the Action.
		"""
		self._owner = None

	def step(self, dt):
		"""
		Called repeatedly by the L{ActionManager} whenever the system "ticks" (that is, whenever the Action should be updated).
		
		Override this method.

		@param dt: The amount of time that has passed since the last time this method was called.
		@type dt: C{float}
		"""
		pass

	def update(self, time):
		"""
		Usually performs the actual task.
		
		Override this method to define what the task may be.

		@param time: Depends on the subclass.
		@type time: C{float}
		"""
		pass

	def isDone(self):
		"""
		Returns whether or not the Action is done. By default, it returns C{True}.

		@return: Whether or not the Action is done.
		@rtype: C{bool}
		"""
		return True
#}


class FiniteTimeAction(AbstractAction):
	"""
	An L{AbstractAction} that will take place over a (finite) period of time.
	"""
	def __init__(self, duration):
		"""
		Initialization method.

		@param duration: How long the Action will take once it has begun.
		@type duration: C{float} (non-negative)
		"""
		AbstractAction.__init__(self)
		self._duration = duration

#{ Accessor methods.
	def getDuration(self):
		"""
		Returns the duration of the Action.

		@return: How long the Action will take to finish once it has begun.
		@rtype: C{float}
		"""
		return self._duration

	def setDuration(self, duration):
		"""
		Sets the duration of the Action.

		@param duration: How long the Action will take to finish once it has begun.
		@type duration: C{float} (non-negative)
		"""
		self._duration = duration

	duration = property(getDuration, setDuration, doc="The duration of the Action.")
#}

	def reverse(self):
		"""
		Returns a reversed copy of this Action, if it exists. Otherwise, it returns C{None}.

		@return: A reversed Action, if it exists.
		@rtype: L{FiniteTimeAction} (or C{None} if the Action is not reversible)
		"""
		return None

class RepeatForever(AbstractAction):
	"""
	An Action wrapper that modifies another L{AbstractAction} by making it repeat forever.
	"""
	def __init__(self, action):
		'''
		Initialization method.

		@param action: The action which will be repeated forever.
		@type action: L{IntervalAction}
		'''
		AbstractAction.__init__(self)
		self._action = action

	def start(self, owner):
		AbstractAction.start(self, owner)
		self._action.start(owner)

	def step(self, dt):
		self._action.step(dt)
		if self._action.isDone():
			self._action.start(self.getOwner())

	def isDone(self):
		"""
		Returns whether or not the Action is done. L{RepeatForever} will always return C{False}.

		@return: C{False}.
		@rtype: C{bool}
		"""
		return False

	def reverse(self):
		"""
		Returns a new L{RepeatForever} object whose wrapped Action is reversed.

		@return: The reversed Action.
		@rtype: L{RepeatForever}
		"""
		return RepeatForever(self._otherAction.reverse())

class Speed(AbstractAction):
	"""
	An Action wrapper that modifies another L{AbstractAction} by changing the speed at which it is run.
	"""
	def __init__(self, action, speed):
		"""
		Initialization method.

		@param action: The action whose speed will be modified.
		@type action: L{AbstractAction}
		@param speed: The scale at which the action's speed will be modified. E.g. a value of C{0.5} will make the action run twice as long, whereas a value of C{2.0} will make the action run half as long.
		@type speed: C{float} (should be non-negative)
		"""
		AbstractAction.__init__(self)
		self._otherAction = action
		self._speed = speed

#{ Accessor methods.
	def getSpeed(self):
		"""
		Returns the scale at which the Action's speed will be modified.

		@return: The speed.
		@rtype: C{float}
		"""
		return self._speed

	def setSpeed(self, speed):
		"""
		Sets the scale at which the Action's speed will be modified.

		@param speed: The speed.
		@type speed: C{float} (non-negative)
		"""
		self._speed = speed

	speed = property(getSpeed, setSpeed, doc="The scale at which the Action's speed will be modified.")
#}

	def start(self, owner):
		AbstractAction.start(self, owner)
		self._otherAction.start(owner)

	def stop(self):
		self._otherAction.stop()
		AbstractAction.stop(self)

	def step(self, dt):
		self._otherAction.step(dt * self._speed)

	def isDone(self):
		"""
		Returns whether or not the wrapped Action is done.

		@return: Whether or not the wrapped Action is done.
		@rtype: C{bool}
		"""
		return self._otherAction.isDone()

	def reverse(self):
		"""
		Returns a new L{Speed} Action with the same speed as the original Speed Action and a reversed copy of the wrapped Action.

		@return: The reversed Action.
		@rtype: L{Speed}
		"""
		return Speed(self._otherAction.reverse(), self._speed)
