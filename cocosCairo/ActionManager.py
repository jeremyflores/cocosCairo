from Scheduler import *
from Timer import *
from Action import *

class ActionManager:
	"""
	Manages all L{AbstractAction}C{s} for the application. It is responsible for updating Actions whenever the L{Scheduler} ticks.

	It is owned by the Director. cocosCairo was designed to have one ActionManager per Director (and one Director per application), so this method should be indirectly accessed through the L{Director}.

	Note that it is possible that an Action's current owner may not be its original owner (it is possible, but discouraged, for someone to manually call L{AbstractAction.setOwner} after the Action has already begun). Thus, methods like L{removeAllActions} may not necessarily perform as expected.
	"""
	def __init__(self, scheduler):
		"""
		Initialization method.

		@param scheduler: The application's Scheduler.
		@type scheduler: L{Scheduler}
		"""
		timer = Timer(self.tick)
		self._scheduler = scheduler
		self._scheduler.schedule(timer)
		self._dict = {}	# each key is of the form (action, owner), and each value is isPaused.

#{ Adding and removing Actions.
	def addAction(self, action, owner, isPaused):
		"""
		Registers an Action to be updated whenever the L{Scheduler} ticks. If the L{AbstractAction} should not be paused, then it will be started immediately by calling L{AbstractAction.start}.

		@param action: The Action being registered.
		@type action: L{AbstractAction}
		@param owner: The object which the Action is modifying.
		@type owner: C{defined by the Action subclass}
		@param isPaused: Whether or not the Action should currently be paused.
		@type isPaused: C{bool}
		"""
		if (action, owner) not in self._dict:
			self._dict[(action,owner)] = isPaused
			action.start(owner)

	def removeAllActions(self, owner):
		"""
		Removes all L{AbstractAction}C{s} whose original owner matches the one provided.

		@param owner: The original owner of the Action.
		@type owner: C{Defined by Action subclass}
		"""
		for key in [x for x in self._dict if x[1] is owner]:
			del self._dict[key]

	def removeAction(self, action):
		"""
		Removes a specific L{AbstractAction}.

		@param action: The Action to remove.
		@type action: L{AbstractAction}
		"""
		key = (action, action.getOriginalOwner())
		if key in self._dict:
			del self._dict[key]

	def removeActionByTag(self, tag, owner):
		"""
		Removes a specific L{AbstractAction} by its tag and original owner.

		@param tag: The tag of the Action.
		@type tag: C{string}
		@param owner: The original owner of the Action.
		@type owner: C{Defined by Action subclass}
		"""
		for key in [x for x in self._dict if x[0].getTag() is tag and x[1] is owner]:
			del self._dict[key]
#}


#{ Accessor methods.
	def getActionByTag(self, tag, owner):
		"""
		Returns the L{AbstractAction} whose tag and original owner match the ones provided, if it exists. Otherwise, it returns C{None}.

		@param tag: The Action's tag.
		@type tag: C{string}
		@param owner: The Action's original owner.
		@type owner: C{Defined by Action subclass}
		@return: The Action, if it exists.
		@rtype: L{AbstractAction} (or C{None} if not found)
		"""
		keys = [x for x in self._dict if x[0].getTag() is tag and x[1] is owner]
		if len(keys) <= 0 or len(keys) > 1:
			return None
		key = keys[0]	# keys should be a list with only one item
		return key[0]

	def getNumberOfRunningActions(self, owner):
		"""
		Returns the number of running Actions whose original owner is provided.

		@param owner: The Action's original owner.
		@type owner: C{Defined by Action subclass}
		"""
		keys = [x for x in self._dict if x[1] is owner]
		return len(keys)
#}


#{ Pausing and resuming Actions.
	def resumeAllActions(self, owner):
		"""
		Resumes all Actions whose original owner is provided.

		@param owner: The Action's original owner.
		@type owner: C{Defined by Action subclass}
		"""
		for key in [x for x in self._dict if x[1] is owner]:
			self._dict[key] = False	# not paused

	def pauseAllActions(self, owner):
		"""
		Pauses all Actions whose original owner is provided.

		@param owner: The Action's original owner.
		@type owner: C{Defined by Action subclass}
		"""
		for key in [x for x in self._dict if x[1] is owner]:
			self._dict[key] = True	# is paused
#}


#{ Private methods.
	def tick(self, dt):
		"""
		Private method which is called by the L{Scheduler} whenever it ticks and propagates the tick to running Actions' L{AbstractAction.step} method. This should generally never be called manually.

		@param dt: The amount of time that has passed since the last tick.
		@type dt: C{float}
		"""
		actionsToRemove = []
		for key in self._dict.copy():
			if key not in self._dict:
				continue
			isPaused = self._dict[key]
			if not isPaused:
				action = key[0]
				action.step(dt)
				if action.isDone():
					action.stop()
					self.removeAction(action)
#}
