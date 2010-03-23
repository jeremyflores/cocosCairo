from Action import *
from copy import copy

class AbstractInstantAction(FiniteTimeAction):
	"""
	An Action that executes once instantaneously.
	"""
	def __init__(self):	
		FiniteTimeAction.__init__(self, 0)

	def isDone(self):
		"""
		Returns whether or not the Action is complete. Since AbstractInstantActions are instantaneous, this will return C{True} by default.

		@return: Whether or not the Action is complete.
		@rtype: C{bool}
		"""
		return True

	def step(self, dt):
		self.update(1)

	def update(self, dt):
		pass

	def reverse(self):
		"""
		Returns a copy of this Action.

		@return: A new copy of the Action.
		@rtype: L{AbstractInstantAction}
		"""
		return copy(self)


class Show(AbstractInstantAction):
	"""
	When executed, shows an object.
	"""
	def start(self, owner):
		AbstractInstantAction.start(self, owner)
		owner.setVisible(True)

	def reverse(self):
		"""
		Returns a new L{Hide} Action.

		@return: A new Hide Action.
		@rtype: L{Hide}
		"""
		return Hide()

class Hide(AbstractInstantAction):
	"""
	When executed, hides an object.
	"""
	def start(self, owner):
		AbstractInstantAction.start(self, owner)
		owner.setVisible(False)

	def reverse(self):
		"""
		Returns a new L{Show} Action.

		@return: A new Show Action.
		@rtype: L{Show}
		"""
		return Show()

class ToggleVisibility(AbstractInstantAction):
	"""
	When executed, toggles an object's visibility.
	"""
	def start(self, owner):
		AbstractInstantAction.start(self, owner)
		owner.setVisible(not owner.isVisible())

class Place(AbstractInstantAction):
	"""
	When executed, sets a new position for an object.
	"""
	def __init__(self, position):
		"""
		Initialization method.

		@param position: The owner's new position.
		@type position: L{Point}
		"""
		AbstractInstantAction.__init__(self)
		self._position = position

	def start(self, owner):
		AbstractInstantAction.start(self, owner)
		owner.setPosition(self._position)

class CallbackInstantAction(AbstractInstantAction):
	"""
	When executed, calls a callback. This may be used, for example, at the end of a L{Sequence} to notify a method that the Sequence is complete.
	"""
	def __init__(self, callback):
		"""
		Initialization method.

		@param callback: The callback to be called.
		@type callback: C{function}
		"""
		AbstractInstantAction.__init__(self)
		self._callback = callback

	def start(self, owner):
		AbstractInstantAction.start(self, owner)
		self.execute()

	def execute(self):
		self._callback()

class CallbackWithOwner(CallbackInstantAction):
	"""
	When executed, calls a callback and passes the method the Action's owner.
	"""
	def execute(self):
		self._callback(self._owner)

class CallbackWithOwnerAndData(CallbackWithOwner):
	"""
	When executed, calls a callback and passes the method the Action's owner as well as some given data.
	"""
	def __init__(self, callback, data):
		"""
		Initialization method.

		@param callback: The callback to be called.
		@type callback: C{function}
		@param data: The data to be passed to the callback.
		@type data: C{user defined}
		"""
		CallbackWithOwner.__init__(self, callback)
		self._data = data

	def execute(self):
		self._callback(self._owner, self._data)

