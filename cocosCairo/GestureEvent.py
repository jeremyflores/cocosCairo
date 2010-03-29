"""
An object that contains information about a detected gesture.
"""

from Geometry import *

# TODO: add state stuff so GestureListeners know if, e.g., Ctrl or Alt keys are pressed when gesture is
# TODO: dispatched.

class AbstractGestureEvent:
	"""
	An object that contains information about a detected gesture (e.g. a mouse press or a key release). AbstractGestureEvents are considered primitives, so values may be accessed directly (e.g. C{event.point} if event is a L{MouseGestureEvent}).
	"""
	pass

class MouseGestureEvent(AbstractGestureEvent):
	"""
	An event for mouse press, mouse double press, mouse release, and mouse motion. If the gesture is a mouse motion, the button is not recorded and instead is defined as C{-1}.
	"""
	def __init__(self, point=None, time=0, button=0):
		"""
		Initialization method.

		@param point: The Point at which the event occurred. Default is C{None}.
		@type point: L{Point}
		@param time: The time at which the event occurred. Default is C{0}.
		@type time: Non-negative C{int}
		@param button: For press and release events, the index of the button for which the event occurred. If the gesture is a mouse motion, the value is C{-1}. Default is C{0}.
		@type button: Non-negative C{int}
		"""
		self.point = point		#: The Point to which the event occurred.
		self.time = time		#: The time at which the event occurred.
		self.button = button	#: The index of the button for which the event occurred (C{-1} if the event is a mouse motion event).

class MouseScrollGestureEvent(AbstractGestureEvent):
	"""
	An event for when the mouse scrolls.
	"""
	def __init__(self, point=None, time=0, direction=''):
		"""
		@param point: The Point at which the event occurred. Default is C{None}.
		@type point: L{Point}
		@param time: The time at which the event occurred. Default is C{0}.
		@type time: Non-negative C{int}
		@param direction: The direction in which the mouse scrolled (C{'up'}, C{'down'}, C{'left'}, C{'right'}). Default is the empty string (C{""}).
		@type direction: C{string}
		"""
		self.point = point			#: The Point at which the event occurred.
		self.time = time			#: The time at which the event occurred.
		self.direction = direction	#: The direction of the scrolling.

class KeyboardGestureEvent(AbstractGestureEvent):
	"""
	An event for when a key is pressed or released.
	"""
	def __init__(self, time=0, key=''):
		"""
		Initialization method.

		@param time: The time at which the event occurred. Default is C{0}.
		@type time: Non-negative C{int}
		@param key: The key for which the event occurred. Default is the empty string (C{""}).
		@type key: C{string}
		"""
		self.time = time	#: The time at which the event occurred.
		self.key = key		#: The keyboard key for which the event occurred.
