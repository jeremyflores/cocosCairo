"""
A ListenedObject that is responsible for sending user gestures to handlers.
"""

import pygtk
import gtk

from ListenedObject import *
from GestureEvent import *
from Geometry import *

_DOUBLE_PRESS_ENUM = 5

# TODO: add drag and drop
# TODO: possibly add onMouseEnter, onMouseLeave?

class GestureDispatch(object, ListenedObject):
	"""
	A L{ListenedObject} that is responsible for sending user gestures to handlers (which could, but not necessarily, be an L{AbstractController}).
	"""

	def __init__(self):
		ListenedObject.__init__(self)
		self._isDispatching = True
		self._lastMousePressTime = 0	# needed to determine if the mouse press event is a double press

#{ Allow / disallow dispatching.
	def isDispatching(self):
		"""
		Returns whether or not the GestureDispatch will send out events. By default, this is C{True}.

		@return: Whether or not the GestureDispatch will send out events.
		@rtype: C{bool}
		"""
		return self._isDispatching

	def setDispatching(self, isDispatching):
		"""
		Sets whether or not the GestureDispatch will send out events.

		@param isDispatching: Whether or not to send out events.
		@type isDispatching: C{bool}
		"""
		self._isDispatching = isDispatching

	dispatching = property(isDispatching, setDispatching, doc="Whether or not the GestureDispatch will send out events.")
#}


#{ Private GTK event handlers.
	def _onMouseMotion(self, widget, event):
		"""
		Private method. Receives mouse motion events from GTK. It constructs a L{MouseGestureEvent}, then dispatches it via L{dispatchMouseMotionGesture}.

		@param widget: The GTK widget in which the event occurred. This should normally be the L{GTKLayout}.
		@type widget: C{gtk.Widget}
		@param event: The GTK event with the event information.
		@type event: C{gtk.gdk.MOTION_NOTIFY}
		"""
		point = Point(event.x, event.y)
		gestureEvent = MouseGestureEvent(point, event.time, -1)
		self.dispatchMouseMotionGesture(gestureEvent)

	def _onMousePress(self, widget, event):
		"""
		Private method. Receives mouse press events from GTK. It constructs a L{MouseGestureEvent}, then dispatches it via L{dispatchMousePressGesture} (or L{dispatchMouseDoublePressGesture} if it was a double press). Note that, when a user double presses, two single-press events will be dispatched before the double-press event is dispatched.

		@param widget: The GTK widget in which the event occurred. This should normally be the L{GTKLayout}.
		@type widget: C{gtk.Widget}
		@param event: The GTK event with the event information.
		@type event: C{gtk.gdk.BUTTON_PRESS}
		"""
		point = Point(event.x, event.y)
		gestureEvent = MouseGestureEvent(point, event.time, event.button)
		if self._lastMousePressTime == event.time:
			self.dispatchMouseDoublePressGesture(gestureEvent)
		else:
			self.dispatchMousePressGesture(gestureEvent)
		self._lastMousePressTime = event.time

	def _onMouseRelease(self, widget, event):
		"""
		Private method. Receives mouse release events from GTK. It constructs a L{MouseGestureEvent}, then dispatches it via L{dispatchMouseReleaseGesture}.

		@param widget: The GTK widget in which the event occurred. This should normally be the L{GTKLayout}.
		@type widget: C{gtk.Widget}
		@param event: The GTK event with the event information.
		@type event: C{gtk.gdk.BUTTON_RELEASE}
		"""
		point = Point(event.x, event.y)
		gestureEvent = MouseGestureEvent(point, event.time, event.button)
		self.dispatchMouseReleaseGesture(gestureEvent)

	def _onMouseScroll(self, widget, event):
		"""
		Private method. Receives mouse scroll events from GTK. It constructs a L{MouseScrollGestureEvent}, then dispatches it via L{dispatchMouseScrollGesture}.

		@param widget: The GTK widget in which the event occurred. This should normally be the L{GTKLayout}.
		@type widget: C{gtk.Widget}
		@param event: The GTK event with the event information.
		@type event: C{gtk.gdk.SCROLL}
		"""
		if event.direction is gtk.gdk.SCROLL_UP:
			direction = 'up'
		elif event.direction is gtk.gdk.SCROLL_DOWN:
			direction = 'down'
		elif event.direction is gtk.gdk.SCROLL_LEFT:
			direction = 'left'
		elif event.direction is gtk.gdk.SCROLL_RIGHT:
			direction = 'right'
		else:
			direction = ''
		point = Point(event.x, event.y)
		gestureEvent = MouseScrollGestureEvent(point, event.time, direction)
		self.dispatchMouseScrollGesture(gestureEvent)

	def _onKeyPress(self, widget, event):
		"""
		Private method. Receives key press events from GTK. It constructs a L{KeyboardGestureEvent}, then dispatches it via L{dispatchKeyPressGesture}.

		@param widget: The GTK widget in which the event occurred. This should normally be the L{GTKLayout}.
		@type widget: C{gtk.Widget}
		@param event: The GTK event with the event information.
		@type event: C{gtk.gdk.KEY_PRESS}
		"""
		gestureEvent = KeyboardGestureEvent(event.time, gtk.gdk.keyval_name(event.keyval))
		self.dispatchKeyPressGesture(gestureEvent)

	def _onKeyRelease(self, widget, event):
		"""
		Private method. Receives key release events from GTK. It constructs a L{KeyboardGestureEvent}, then dispatches it via L{dispatchKeyReleaseGesture}.

		@param widget: The GTK widget in which the event occurred. This should normally be the L{GTKLayout}.
		@type widget: C{gtk.Widget}
		@param event: The GTK event with the event information.
		@type event: C{gtk.gdk.KEY_RELEASE}
		"""
		gestureEvent = KeyboardGestureEvent(event.time, gtk.gdk.keyval_name(event.keyval))
		self.dispatchKeyReleaseGesture(gestureEvent)
#}


#{ Public dispatch methods.
	def dispatchMouseMotionGesture(self, gestureEvent):
		"""
		If currently sending out events, notifies listeners of a mouse motion. This may be used to manually fire an event.

		@param gestureEvent: The event.
		@type gestureEvent: L{MouseGestureEvent}
		"""
		if self._isDispatching is True:
			for listener in self.getListeners():
				listenerHandledEvent = listener.onMouseMotion(gestureEvent)
				if listenerHandledEvent:
					break

	def dispatchMousePressGesture(self, gestureEvent):
		"""
		If currently sending out events, notifies listeners of a mouse press. This may be used to manually fire an event.

		@param gestureEvent: The event.
		@type gestureEvent: L{MouseGestureEvent}
		"""
		if self._isDispatching is True:
			for listener in self.getListeners():
				listenerHandledEvent = listener.onMousePress(gestureEvent)
				if listenerHandledEvent:
					break

	def dispatchMouseDoublePressGesture(self, gestureEvent):
		"""
		If currently sending out events, notifies listeners of a mouse double press (that is, a double click). This may be used to manually fire an event.

		@param gestureEvent: The event.
		@type gestureEvent: L{MouseGestureEvent}
		"""
		if self._isDispatching is True:
			for listener in self.getListeners():
				listenerHandledEvent = listener.onMouseDoublePress(gestureEvent)
				if listenerHandledEvent:
					breaks

	def dispatchMouseReleaseGesture(self, gestureEvent):
		"""
		If currently sending out events, notifies listeners of a mouse release. This may be used to manually fire an event.

		@param gestureEvent: The event.
		@type gestureEvent: L{MouseGestureEvent}
		"""
		if self._isDispatching is True:
			for listener in self.getListeners():
				listenerHandledEvent = listener.onMouseRelease(gestureEvent)
				if listenerHandledEvent:
					break

	def dispatchMouseScrollGesture(self, gestureEvent):
		"""
		If currently sending out events, notifies listeners of a mouse scroll. This may be used to manually fire an event.

		@param gestureEvent: The event.
		@type gestureEvent: L{MouseScrollGestureEvent}
		"""
		if self._isDispatching is True:
			for listener in self.getListeners():
				listenerHandledEvent = listener.onMouseScroll(gestureEvent)
				if listenerHandledEvent:
					break

	def dispatchKeyPressGesture(self, gestureEvent):
		"""
		If currently sending out events, notifies listeners of a key press. This may be used to manually fire an event.

		@param gestureEvent: The event.
		@type gestureEvent: L{KeyboardGestureEvent}
		"""
		if self._isDispatching is True:
			for listener in self.getListeners():
				listenerHandledEvent = listener.onKeyPress(gestureEvent)
				if listenerHandledEvent:
					break

	def dispatchKeyReleaseGesture(self, gestureEvent):
		"""
		If currently sending out events, notifies listeners of a key release. This may be used to manually fire an event.

		@param gestureEvent: The event.
		@type gestureEvent: L{KeyboardGestureEvent}
		"""
		if self._isDispatching is True:
			for listener in self.getListeners():
				listenerHandledEvent = listener.onKeyRelease(gestureEvent)
				if listenerHandledEvent:
					break
#}
