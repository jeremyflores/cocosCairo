"""
Calls a given callback every given seconds.
"""

class Timer:
	"""
	Calls a callback every given seconds.
	"""
	def __init__(self, callback, interval=0.0):
		"""
		Initialization method.

		@param callback: The callback to be called.
		@type callback: C{callback}
		@param interval: How often the callback should be called.
		@type interval: Non-negative C{float}
		"""
		self._callback = callback
		self._interval = interval
		self._elapsed = -1.0

	def getInterval(self):
		"""
		Returns how often the callback will be called.

		@return: How often the callback will be called.
		@rtype: C{float}
		"""
		return self._interval

	def setInterval(self, interval):
		"""
		Sets how often the callback will be called.

		@param interval: How often the callback will be called.
		@type interval: C{float}
		"""
		self._interval = interval

	interval = property(getInterval, setInterval, doc="How often the callback will be called.")

	def fire(self, dt):
		"""
		Causes the timer to call the callback.

		@param dt: The amount of time that has elapsed since the last time it was fired.
		@type dt: Non-negative C{float}
		"""
		if self._elapsed == -1.0:
			self._elapsed = 0.0
		else:
			self._elapsed += dt
		if self._elapsed >= self._interval:
			self._callback(self._elapsed)
			self._elapsed = 0.0
