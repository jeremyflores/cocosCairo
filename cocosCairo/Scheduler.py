"""
Manages all Timers for the application.
"""

class Scheduler:
	"""
	Manages all L{Timer}C{s} for the application. It is responsible for updating all Timers whenever it ticks.

	It is owned by the Director. cocosCairo was designed to have one Scheduler per Director (and one Director per application), so this method should be indirectly accessed through the L{Director}.
	"""
	def __init__(self):
		self._scheduledTimers = []
		self._timersToRemove = []
		self._timersToAdd = []
		self.timeScale = 1.0	#: Modifies the time scale of all scheduled timers. Setting a value less than the current one will create a "slow motion" effect, while setting a value greater than the current one will create a "fast forward" effect. Default is C{1.0}.

	def schedule(self, timer):
		"""
		Registers a timer to be notified when the Scheduler ticks.

		@param timer: The timer to be notified.
		@type timer: L{Timer}
		"""
		if timer in self._timersToRemove:
			self._timersToRemove.remove(timer)
			return
		if timer not in self._timersToAdd and timer not in self._scheduledTimers:
			self._timersToAdd.append(timer)

	def unschedule(self, timer):
		"""
		Unregisters a timer to be notified when the Scheduler ticks.

		@param timer: The timer to be unregistered.
		@type timer: L{Timer}
		"""
		if timer in self._timersToAdd:
			self._timersToAdd.remove(timer)
			return
		if timer in self._scheduledTimers:
			self._timersToRemove.append(timer)

	def unscheduleAllTimers(self):
		"""
		Clears out all timers that have been registered.
		"""
		self._scheduledTimers = []
		self._timersToRemove = []
		self._timersToAdd = []

	def tick(self, dt):
		"""
		Called whenever a small amount of time has progressed and notifies all registered timers of the tick. This method should not generally be called manually.

		The Scheduler is ticked once per main loop iteration in L{Director}.

		@param dt: The amount of time since the last tick.
		@type dt: Non-negative C{float}
		"""
		if self.timeScale != 1.0:
			dt *= self.timeScale
		for timer in self._timersToRemove:
			self._scheduledTimers.remove(timer)
		self._timersToRemove = []
		for timer in self._timersToAdd:
			self._scheduledTimers.append(timer)
		self._timersToAdd = []
		for timer in self._scheduledTimers:
			timer.fire(dt)
