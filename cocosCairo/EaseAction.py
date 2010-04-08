"""
Actions which modifies the rate at which other Actions execute, usually by some geometric curve.
"""

from IntervalAction import *
from Geometry import *
from Color import *
import math

# TODO: have tables for math.pow and math.cos instead of doing calculations on the fly. might save some
# TODO: CPU cycles, and t is in [0,1], so it should be pretty manageable.

class AbstractEaseAction(AbstractIntervalAction):
	"""
	An abstract L{AbstractAction} wrapper that modifies the rate at which the wrapped Action executes, usually by some geometric curve.
	"""
	def __init__(self, action):
		"""
		Initialization method.

		@param action: The wrapped Action.
		@type action: L{AbstractAction}
		"""
		AbstractIntervalAction.__init__(self, action._duration)
		self._action = action

	def start(self, owner):
		AbstractIntervalAction.start(self, owner)
		self._action.start(owner)

	def stop(self):
		AbstractIntervalAction.stop(self)
		self._action.stop()

	def update(self, time):
		self._action.update(time)

	def reverse(self):
		"""
		Returns a new copy of the L{AbstractEaseAction} whose wrapped Action is reversed.

		@return: A new, reversed Action.
		@rtype: L{AbstractEaseAction}
		"""
		return self.__class__(self._action.reverse())


class AbstractEaseRateAction(AbstractEaseAction):
	"""
	An L{AbstractEaseAction} whose curve is determined by a given rate.
	"""
	def __init__(self, action, rate=2.0):
		"""
		Initialization method.

		@param action: The wrapped Action.
		@type action: L{AbstractAction}
		@param rate: The rate at which the curve will change. Default is C{2.0}.
		@type rate: Non-negative C{float}
		"""
		AbstractEaseAction.__init__(self, action)
		self._rate = rate

	def getRate(self):
		"""
		Returns the rate at which the curve will change.

		@return: The rate.
		@rtype: C{float}
		"""
		return self._rate

	def setRate(self, rate):
		"""
		Sets the rate at which the curve will change.

		@param rate: The rate.
		@type rate: Non-negative C{float}
		"""
		self._rate = rate

	rate = property(getRate, setRate, doc="The rate at which the curve will change.")

	def reverse(self):
		"""
		Returns a new copy of the L{AbstractEaseRateAction} whose wrapped Action is reversed and whose rate is inverted.

		@return: A new, reversed Action.
		@rtype: L{AbstractEaseRateAction}
		"""
		return self.__class__(self._action.reverse(), 1/self._rate)

class EaseIn(AbstractEaseRateAction):
	"""
	An L{AbstractEaseRateAction} that starts slowly then increases speed as it nears completion.
	"""
	def update(self, t):
		newTime = math.pow(t, self._rate)
		self._action.update(newTime)

class EaseOut(AbstractEaseRateAction):
	"""
	An L{AbstractEaseRateAction} that starts quickly then decreases speed as it nears completion.
	"""
	def update(self, t):
		newTime = math.pow(t, 1./self._rate)
		self._action.update(newTime)

class EaseInOut(AbstractEaseRateAction):
	"""
	An L{AbstractEaseRateAction} that starts slowly, speeds up to being 50% complete, then slows back down as it nears completion.
	"""
	def update(self, t):
		sign = 1
		r = int(self._rate)
		if (r%2) == 0:
			sign = -1
		t *= 2
		if t < 1:
			newTime = 0.5 * math.pow(t, self._rate)
		else:
			newTime = sign * 0.5 * (math.pow(t-2, self._rate) + sign * 2)
		self._action.update(newTime)

	def reverse(self):
		"""
		Returns a reversed copy of this Action.

		@return: A new, reversed Action.
		@rtype: L{EaseInOut}
		"""
		return EaseInOut(self._action.reverse(), self._rate)

class EaseExponentialIn(AbstractEaseAction):
	"""
	An L{AbstractEaseAction} that starts slowly then increases speed as it nears completion. It uses an exponential curve.
	"""
	def update(self, t):
		if t == 0:
			newTime = 0
		else:
			newTime = math.pow(2, 10 * (t - 1))	# TODO: check this out. cocos2d does weird stuff
		self._action.update(newTime)

	def reverse(self):
		"""
		Returns an EaseExponentialOut whose wrapped Action is reversed.

		@return: A new, reversed Action.
		@rtype: L{EaseExponentialOut}
		"""
		return EaseExponentialOut(self._action.reverse())

class EaseExponentialOut(AbstractEaseAction):
	"""
	An L{AbstractEaseAction} that starts quickly then decreases speed as it nears completion. It uses an exponential curve.
	"""
	def update(self, t):
		if t == 1:
			newTime = 1
		else:
			newTime = -math.pow(2, -10*t) + 1	# TODO: check this out. cocos2d has weird implementation
		self._action.update(newTime)

	def reverse(self):
		"""
		Returns an EaseExponentialIn whose wrapped Action is reversed.

		@return: A new, reversed Action.
		@rtype: L{EaseExponentialIn}
		"""
		return EaseExponentialIn(self._action.reverse())

class EaseExponentialInOut(AbstractEaseAction):
	"""
	An L{AbstractEaseAction} that starts slowly, speeds up to being 50% complete, then slows back down as it nears completion. It uses an exponential curve.
	"""
	def update(self, t):
		t /= 0.5
		if (t < 1):
			newTime = 0.5 * math.pow(2, 10*(t-1))
		else:
			newTime = 0.5 * (-math.pow(2, -10 * (t-1)) + 2)
		self._action.update(newTime)

class EaseSineIn(AbstractEaseAction):
	"""
	An L{AbstractEaseAction} that starts slowly then increases speed as it nears completion. It uses a sine curve.
	"""
	def update(self, t):
		newTime = -1*math.cos(t*math.pi/2) + 1
		self._action.update(newTime)

	def reverse(self):
		"""
		Returns an EaseSineOut whose wrapped Action is reversed.

		@return: A new, reversed Action.
		@rtype: L{EaseSineOut}
		"""
		return EaseSineOut(self._action.reverse())

class EaseSineOut(AbstractEaseAction):
	"""
	An L{AbstractEaseAction} that starts quickly then decreases speed as it nears completion. It uses a sine curve.
	"""
	def update(self, t):
		newTime = math.sin(t*math.pi/2)
		self._action.update(newTime)

	def reverse(self):
		"""
		Returns an EaseSineIn whose wrapped Action is reversed.

		@return: A new, reversed Action.
		@rtype: L{EaseSineIn}
		"""
		return EaseSineIn(self._action.reverse())

class EaseSineInOut(AbstractEaseAction):
	"""
	An L{AbstractEaseAction} that starts slowly, speeds up to being 50% complete, then slows back down as it nears completion. It uses a sine curve.
	"""
	def update(self, t):
		newTime = -0.5*(math.cos(math.pi*t) - 1)
		self._action.update(newTime)



class AbstractEaseElastic(AbstractEaseAction):
	"""
	An L{AbstractEaseAction} whose curve oscillates so as to produce an elastic effect.
	"""
	def __init__(self, action, period=0.3):
		AbstractEaseAction.__init__(self, action)
		self._period = period

	def getPeriod(self):
		return self._period

	def setPeriod(self, period):
		self._period = period

	period = property(getPeriod, setPeriod)

	def reverse(self):
		"""
		Override this.
		"""
		return None

class EaseElasticIn(AbstractEaseElastic):
	"""
	An L{AbstractEaseAction} which oscillates at the beginning before reaching completion.
	"""
	def update(self, t):
		if t is 0 or t is 1:
			newTime = t
		else:
			s = self._period / 4
			t = t-1
			newTime = -math.pow(2, 10*t) * math.sin((t-s) * 2 * math.pi / self._period)
		self._action.update(newTime)

	def reverse(self):
		"""
		Returns an EaseElasticOut whose wrapped Action is reversed.

		@return: A new, reversed Action.
		@rtype: L{EaseElasticOut}
		"""
		return EaseElasticOut(self._action.reverse(), self._period)

class EaseElasticOut(AbstractEaseElastic):
	"""
	An L{AbstractEaseAction} which oscillates at the end as it reaches completion.
	"""
	def update(self, t):
		if t is 0 or t is 1:
			newTime = t
		else:
			s = self._period / 4
			newTime = math.pow(2, -10*t) * math.sin((t-s) * 2 * math.pi / self._period) + 1
		self._action.update(newTime)

	def reverse(self):
		"""
		Returns an EaseElasticIn whose wrapped Action is reversed.

		@return: A new, reversed Action.
		@rtype: L{EaseElasticIn}
		"""
		return EaseElasticIn(self._action.reverse(), self._period)

class EaseElasticInOut(AbstractEaseElastic):
	"""
	An L{AbstractEaseAction} which oscillates both at the beginning and as it reaches completion.
	"""
	def update(self, t):
		if t is 0 or t is 1:
			newTime = t
		else:
			t *= 2
			s = self._period / 4
			t -= 1
			if t < 0:
				newTime = -0.5 * math.pow(2, 10*t) * math.sin((t-s) * 2 * math.pi / self._period)
			else:
				newTime = math.pow(2, -10*t) * math.sin((t-s) * 2 * math.pi / self._period) * 0.5 + 1
		self._action.update(newTime)

	def reverse(self):
		return EaseElasticInOut(self._action.reverse(), self._period)


class AbstractEaseBounce(AbstractEaseAction):
	"""
	An abstract L{AbstractEaseAction} whose curve oscillates so as to produce a bouncing effect.
	"""
	def bounceTime(self, t):
		"""
		Returns the modified time so as to emulate the bouncing effect.

		@param t: The percentage complete.
		@type t: Non-negative C{float}
		@return: The modified percentage complete.
		@rtype: C{float}
		"""
		if t < 1./2.75:
			return 7.5625 * t * t
		elif t < 2 / 2.75:
			t -= 1.5 / 2.75
			return 7.5625 * t * t + 0.75
		elif t < 2.5 / 2.75:
			t -= 2.25 / 2.75
			return 7.5625 * t * t + 0.9375
		else:
			t -= 2.625 / 2.75
			return 7.5625 * t * t + 0.984375

class EaseBounceIn(AbstractEaseBounce):
	"""
	An L{AbstractEaseAction} whose curve first bounces before reaching completion.
	"""
	def update(self, t):
		newTime = 1 - self.bounceTime(1-t)
		self._action.update(newTime)

	def reverse(self):
		"""
		Returns an EaseBounceOut whose wrapped Action is reversed.

		@return: A new, reversed Action.
		@rtype: L{EaseBounceOut}
		"""
		return EaseBounceOut(self._action.reverse())

class EaseBounceOut(AbstractEaseBounce):
	"""
	An L{AbstractEaseAction} whose curve bounces as it reaches completion.
	"""
	def update(self, t):
		newTime = self.bounceTime(t)
		self._action.update(newTime)

	def reverse(self):
		"""
		Returns an EaseBounceIn whose wrapped Action is reversed.

		@return: A new, reversed Action.
		@rtype: L{EaseBounceIn}
		"""
		return EaseBounceIn(self._action.reverse())

class EaseBounceInOut(AbstractEaseBounce):
	"""
	An L{AbstractEaseAction} whose curve first bounces before reaching completion, then again bounces as it reaches completion.
	"""
	def update(self, t):
		if t < 0.5:
			t *= 2
			newTime = 0.5 * (1 - self.bounceTime(1-t))
		else:
			newTime = 0.5 * self.bounceTime(t*2-1) + 0.5
		self._action.update(newTime)

class EaseBackIn(AbstractEaseAction):
	"""
	An L{AbstractEaseAction} whose curve first reverses before reaching completion.
	"""
	def update(self, t):
		overshoot = 1.70158
		newTime = t * t * ((overshoot+1)*t - overshoot)
		self._action.update(newTime)

	def reverse(self):
		"""
		Returns an EaseBackOut whose wrapped Action is reversed.

		@return: A new, reversed Action.
		@rtype: L{EaseBackOut}
		"""
		return EaseBackOut(self._action.reverse())

class EaseBackOut(AbstractEaseAction):
	"""
	An L{AbstractEaseAction} whose curve overshoots and then corrects as it reaches completion.
	"""
	def update(self, t):
		overshoot = 1.70158
		t -= 1
		newTime = t * t * ((overshoot+1)*t + overshoot) + 1
		self._action.update(newTime)

	def reverse(self):
		"""
		Returns an EaseBackIn whose wrapped Action is reversed.

		@return: A new, reversed Action.
		@rtype: L{EaseBackIn}
		"""
		return EaseBackIn(self._action.reverse())

class EaseBackInOut(AbstractEaseAction):
	"""
	An L{AbstractEaseAction} whose curve first reverses then overshoots and corrects as it reaches completion.
	"""
	def update(self, t):
		overshoot = 1.70158 * 1.525
		t *= 2
		if t < 1:
			newTime = t * t * ((overshoot+1)*t - overshoot) / 2
		else:
			t -= 2
			newTime = t * t * ((overshoot+1)*t + overshoot) / 2 + 1
		self._action.update(newTime)
