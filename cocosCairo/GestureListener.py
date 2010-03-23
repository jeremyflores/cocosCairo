class GestureListener:
	def onMousePress(self, event):
		"""
		Override this method to handle a button press event.

		@param event: Event details.
		@type event: L{MouseGestureEvent}
		@return: Whether or not this listener will handle the event.
		@rtype: C{bool}
		"""
		return False

	def onMouseMotion(self, event):
		"""
		Override this method to handle a mouse motion event.

		@param event: Event details.
		@type event: L{MouseGestureEvent}
		@return: Whether or not this listener will handle the event.
		@rtype: C{bool}
		"""
		return False

	def onMouseRelease(self, event):
		"""
		Override this method to handle a button release event.

		@param event: Event details.
		@type event: L{MouseGestureEvent}
		@return: Whether or not this listener will handle the event.
		@rtype: C{bool}
		"""
		return False

	def onMouseDoublePress(self, event):
		"""
		Override this method to handle a double press event.
		If two mouse press gesture were detected within 0.25 seconds of each other. If a double press gesture is detected, the GestureDispatch will first send the two individual mouse press gesture events, then send the double press gesture event.

		@param event: Event details.
		@type event: L{MouseGestureEvent}
		@return: Whether or not this listener will handle the event.
		@rtype: C{bool}
		"""
		return False

	def onMouseScroll(self, event):
		"""
		Override this method to handle a mouse scroll event.

		@param event: Event details.
		@type event: L{MouseScrollGestureEvent}
		@return: Whether or not this listener will handle the event.
		@rtype: C{bool}
		"""
		return False

	def onKeyPress(self, event):
		"""
		Override this method to handle a key press event.

		@param event: Event details.
		@type event: L{KeyboardGestureEvent}
		@return: Whether or not this listener will handle the event.
		@rtype: C{bool}
		"""
		return False

	def onKeyRelease(self, event):
		"""
		Override this method to handle a key release event.

		@param event: Event details.
		@type event: L{KeyboardGestureEvent}
		@return: Whether or not this listener will handle the event.
		@rtype: C{bool}
		"""
		return False
