class ListenedObject:
	"""
	A mixin which provides convenience methods for storing, adding, and removing L{AbstractListener}C{s} to an object.
	"""
	def __init__(self):
		self._listeners = []

	def getListeners(self):
		"""
		Returns the list of listeners.

		@return: A list of L{AbstractListener}C{s}.
		@rtype: C{list}
		"""
		return self._listeners

	def addListener(self, listener):
		"""
		Adds a listener if it is not already listening.

		@param listener: A new listener.
		@type listener: L{AbstractListener}
		"""
		if not listener in self._listeners:
			self._listeners.append(listener)

	def removeListener(self, listener):
		"""
		Removes a listener if it is currently listening.

		@param listener: The listener to be removed.
		@type listener: L{AbstractListener}
		"""
		if listener in self._listeners:
			self._listeners.remove(listener)
