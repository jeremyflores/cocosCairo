from Action import *
from InstantAction import *
from Geometry import *
from Color import *
from ListenedObject import *

import math

# TODO: Make the Animate class, fix up Sprite to handle animations.

class AbstractIntervalAction(FiniteTimeAction):
	"""
	A L{FiniteTimeAction} that incrementally performs small changes in intervals over a period of time.
	"""
	def __init__(self, duration):
		if duration is 0:
			duration = 0.00000001	# prevent division by zero on first step
		FiniteTimeAction.__init__(self, duration)
		self._elapsed = 0.0

	def isDone(self):
		if self._elapsed >= self._duration:
			return True
		else:
			return False

	def step(self, dt):
		self._elapsed += dt
		t = self._elapsed/self._duration
		if t > 1.0:
			t = 1.0
		self.update(t)

	def start(self, owner):
		FiniteTimeAction.start(self, owner)
		self._elapsed = 0.0


class DelayTime(AbstractIntervalAction):
	"""
	An L{AbstractIntervalAction} that performs no operations over a period of time. This may be useful, for example, for introducing delays before certain Actions in a L{Sequence}.
	"""
	def update(self, time):
		return

	def reverse(self):
		"""
		Returns a new DelayTime with the same duration as this Action.

		@return: A new DelayTime.
		@rtype: L{DelayTime}
		"""
		return DelayTime(self._duration)

class Sequence(AbstractIntervalAction):
	"""
	An L{AbstractIntervalAction} that executes a series of Actions according to the order in which they are given. 
	"""
	def __init__(self, *actions):
		"""
		Initialization method.

		@param actions: The Actions in the order in which they will be executed.
		@type actions: C{comma-separated Actions}
		"""
		self._actions = []
		self._index = 0
		self._durationPercentages = []
		duration = 0.0
		for action in actions:
			duration += action._duration
			self._actions.append(action)
		for action in actions:
			self._durationPercentages.append(action._duration / duration)
		AbstractIntervalAction.__init__(self, duration)

	def start(self, owner):
		self._index = 0
		AbstractIntervalAction.start(self, owner)

	def stop(self):
		for action in self._actions:
			action.stop()
		AbstractIntervalAction.stop(self)

	def update(self, time):
		# ========================================================================================== #
		#
		# If the update encounters a subsequence of AbstractInstantActions, it will start all of them
		# in the same update loop as well as the first non-AbstractInstantAction that follows it (if
		# it exists).
		#
		# For example, let's say that the sequence is
		#
		#	(action1, instant1, instant2, action2, action3, instant3, instant4),
		#
		# where instant[X] is an AbstractInstantAction and action[X] is an Action that is not
		# instantaneous.
		#
		# On the first update, it will start action1, and on the next few updates, it will update
		# action1.
		#
		# After action1 is complete, then instant1, instant2, and action2 will *all* be started
		# within the same update. After they've been started, the next few updates will be used to
		# update action2.
		#
		# Then, action3 will be started and, as expected, the next few updates will update action3.
		#
		# Finally, when action3 is complete, the sequence is technically complete because, since the
		# instantaneous Actions have a duration of 0, the percentage complete is now at 100%. So,
		# immediately after action3 completes, instant3 and instant4 will be started.
		#
		# ========================================================================================== #
		if self._index >= len(self._actions):
			return

		# ========================================================================================== #
		#
		# This loop is to start all adjacent AbstractInstantActions simultaneously as well as the
		# first non-AbstractInstantAction that follows the InstantAction subsequence.
		#
		# The variable "action" will either be the last action in the sequence or the first
		# non-AbstractInstantAction found in the actions that has not been executed yet.
		#
		# If we're currently updating a non-AbstractInstantAction, "action" will refer to it, and
		# it won't be erroneously started more than once. In this case, therefore, the for loop
		# does nothing more than the equivalent of
		#
		# "action = self._actions[self._index]".
		#
		# This loop will always "catch" on a non-instantaneous Action, so it shouldn't continue in
		# the sequence beyond where it should be (e.g. starting a non-instantaneous Action while
		# another non-instantaneous Action is still being updated).
		#
		# ========================================================================================== #
		action = None	# initialize to None in case there are no remaining Actions left (shouldn't happen)
		for action in self._actions[self._index:]:	# for all remaining actions
			if action.getOwner() is None:	
				action.start(self._owner)
			if not isinstance(action, AbstractInstantAction):
				break
			else:	# if it is an AbstractInstantAction
				self._index += 1

		# ========================================================================================== #
		#
		# If the last action from the for loop is not an AbstractInstantAction, then we have to 
		# update it.
		#
		# ========================================================================================== #
		if not isinstance(action, AbstractInstantAction):
			for i in range(0, self._index):	# get the elapsed time since the action started
				time -= self._durationPercentages[i]
			percent = time / self._durationPercentages[self._index]
			if percent >= 1.0 or abs(percent-1.0) <= 0.0000001: # accommodate for rounding errors
				percent = 1.0	# so normalize it back to 1.0
			action.update(percent)	# update the action with the percentage complete
			if percent >= 1.0:	# if the action is done
				action.stop()		# then stop it
				self._index += 1	# and, on the next update, move on to the next Action in the sequence

				# finally, if there are only AbstractInstantActions left, start all of them now
				remainingActions = self._actions[self._index:]
				numNonInstantActions = len([action for action in remainingActions if not isinstance(action, AbstractInstantAction)])
				if numNonInstantActions is 0:	# if all the remaining actions are instantaneous
					for action in remainingActions:
						action.start(self._owner)	# fire them all now
						self._index += 1			# and increment so that self._index == len(self._actions)


	def reverse(self):
		"""
		Returns a new Sequence whose Actions are in the reverse order of this Sequence.

		@return: A new Sequence with Actions in reverse order.
		@rtype: L{Sequence}
		"""
		tempList = []
		for action in self._actions:
			tempList.append(action)	# copy the list without changing this instance's list
		tempList.reverse()
		return Sequence(*tempList)


class Repeat(AbstractIntervalAction):
	"""
	Repeats a given Action a given number of times.
	"""
	def __init__(self, action, times):
		"""
		Initialization method.

		@param action: The Action to be repeated.
		@type action: L{AbstractAction}
		@param times: The number of times the Action will be repeated.
		@type times: Non-negative C{int}
		"""
		totalTime = action._duration * times
		AbstractIntervalAction.__init__(self, totalTime)
		self._times = times
		self._otherAction = action
		self._total = 0	# total number of times this has been repeated so far

	def start(self, owner):
		self._total = 0
		AbstractIntervalAction.start(self, owner)
		self._otherAction.start(self._owner)

	def stop(self):
		AbstractIntervalAction.stop(self)
		self._otherAction.stop()

	def update(self, dt):
		t = dt * self._times
		r = math.fmod(t, 1.0)
		if t > self._total + 1:
			self._otherAction.update(1.0)
			self._total += 1
			self._otherAction.stop()
			self._otherAction.start(self._owner)
			self._otherAction.update(0.0)
		else:
			if dt == 1.0:
				r = 1.0
				self._total += 1
			self._otherAction.update(min(r,1.0))

	def isDone(self):
		if self._times == self._total:
			return True
		else:
			return False

	def reverse(self):
		"""
		Returns a new Repeat whose wrapped Action is reversed.

		@return: A new Repeat.
		@rtype: L{Repeat}.
		"""
		return Repeat(self._otherAction.reverse(), self._times)

class Spawn(AbstractIntervalAction):
	"""
	Starts multiple Actions simultaneously.
	"""
	def __init__(self, *actions):
		"""
		Initialization method.

		@param actions: The Actions to be spawned simultaneously.
		@type actions: C{Comma-separated Actions}
		"""
		durations = [action._duration for action in actions]
		duration = max(durations)
		AbstractIntervalAction.__init__(self, duration)
		self._actions = []
		for action in actions:
			if action._duration == duration:
				self._actions.append(action)
			else:
				delayTime = DelayTime(duration-action._duration)
				sequence = Sequence(action, delayTime)
				self._actions.append(sequence)

	def start(self, owner):
		AbstractIntervalAction.start(self, owner)
		for action in self._actions:
			action.start(self._owner)

	def stop(self):
		for action in self._actions:
			action.stop()
		AbstractIntervalAction.stop(self)

	def update(self, time):
		for action in self._actions:
			action.update(time)

	def reverse(self):
		"""
		Returns a new Spawn whose wrapped Actions are reversed.

		@return: A new Spawn.
		@rtype: L{Spawn}
		"""
		tempList = []
		for action in self._actions:
			tempList.append(action.reverse())
		return Spawn(*tempList)

class RotateTo(AbstractIntervalAction):
	"""
	Rotates a L{Node} to a certain angle in radians over a period of time.
	"""
	def __init__(self, duration, angle):
		"""
		Initialization method.

		@param duration: How long the action will take.
		@type duration: Non-negative C{float}
		@param angle: The final angle to which the object will be rotated.
		@type angle: C{float}
		"""
		AbstractIntervalAction.__init__(self, duration)
		self._angle = angle
		self._startAngle = 0

	def start(self, owner):
		AbstractIntervalAction.start(self, owner)
		self._startAngle = self._owner.getRotation()
		if self._startAngle > 0:
			self._startAngle = math.fmod(self._startAngle, 360.0)
		else:
			self._startAngle = math.fmod(self._startAngle, -360.0)
		self._angle = -self._startAngle
		if self._angle > 180.0:
			self._angle = -360.0 + self._angle
		if self._angle < -180.0:
			self._angle = 360.0 + self._angle

	def update(self, time):
		self._owner.setRotation(self._startAngle + self._angle * time)

class RotateBy(AbstractIntervalAction):
	"""
	Rotates a L{Node} by a certain angle over a period of time.
	"""
	def __init__(self, duration, angle):
		"""
		Initialization method.

		@param duration: How long the action will take.
		@type duration: Non-negative C{float}
		@param angle: The final angle by which the object will be rotated.
		@type angle: C{float}
		"""
		AbstractIntervalAction.__init__(self, duration)
		self._angle = angle
		self._startAngle = 0

	def start(self, owner):
		AbstractIntervalAction.start(self, owner)
		self._startAngle = self._owner.getRotation()

	def update(self, time):
		self._owner.setRotation(self._startAngle + self._angle * time)

	def reverse(self):
		"""
		Returns a new RotateBy whose angle is the negative value of the original.

		@return: A new RotateBy.
		@rtype: L{RotateBy}
		"""
		return RotateBy(self._duration, -self._angle)

class MoveTo(AbstractIntervalAction):
	"""
	Moves a L{Node} to a certain L{Point} over a period of time.
	"""
	def __init__(self, duration, position):
		"""
		Initialization method.

		@param duration: How long the action will take.
		@type duration: Non-negative C{float}
		@param position: The final position to which the object will be moved.
		@type position: L{Point}
		"""
		AbstractIntervalAction.__init__(self, duration)
		self._endPosition = position
		self._startPosition = PointZero()
		self._delta = PointZero()

	def start(self, owner):
		AbstractIntervalAction.start(self, owner)
		self._startPosition = self._owner.getPosition()
		self._delta = pointSub(self._endPosition, self._startPosition)

	def update(self, time):
		p = PointZero()
		p.x = self._startPosition.x + self._delta.x * time
		p.y = self._startPosition.y + self._delta.y * time
		self._owner.setPosition(p)

class MoveBy(MoveTo):
	"""
	Moves a L{Node} by a certain distance (given by a L{Point}) over a period of time.
	"""
	def __init__(self, duration, position):
		"""
		Initialization method.

		@param duration: How long the action will take.
		@type duration: Non-negative C{float}
		@param position: How far in the x-axis and y-axis the object should be moved.
		@type position: L{Point}
		"""
		MoveTo.__init__(self, duration, position)
		self._delta = position

	def start(self, owner):
		temp = self._delta
		MoveTo.start(self, owner)
		self._delta = temp

	def reverse(self):
		"""
		Returns a new MoveBy whose position is the negative value of the original MoveBy.

		@return: a new MoveBy.
		@rtype: L{MoveBy}
		"""
		return MoveBy(self._duration, Point(-self._delta.x, -self._delta.y))


class MoveAlongPath(Sequence):
	"""
	Moves a L{Node} along a given L{Path}.
	"""
	def __init__(self, duration, path, maxRotationDuration=0.5, isAutorotating=True):
		"""
		Initialization method.

		@param duration: How long the action will take.
		@type duration: Non-negative C{float}
		@param path: The Path which the Node will traverse.
		@type path: L{Path}
		@param maxRotationDuration: The maximum time in seconds an automatic rotation should take.
		@type maxRotationDuration: Non-negative C{float}
		@param isAutorotating: Whether or not the Node will rotate automatically at turns.
		@type isAutorotating: C{bool}
		"""
		self._path = path
		self._isAutorotating = isAutorotating
		points = self._path.getPoints()
		totalDistance = 0.0
		for i in range(0, len(points)-1):
			totalDistance += pointDistance(points[i], points[i+1])
		actions = []
		self._startingAngle = getAngleBetweenLines(points[0], Point(points[0].x+1, points[0].y), points[0], points[1])
		if isinstance(self._path, RelativePath):
			MoveClass = MoveBy
		else:
			MoveClass = MoveTo
		rotateAction = None
		for i in range(1, len(points)):
			moveDuration = pointDistance(points[i-1], points[i]) / totalDistance * duration
			action = MoveClass(moveDuration, points[i])
			if self._isAutorotating:
				if rotateAction is not None:
					action = Spawn(action, rotateAction)
				if i+1 < len(points):
					p1 = points[i-1]
					p2 = points[i]
					p3 = points[i+1]
					angle = getAngleBetweenLines(p1, p2, p2, p3)
					rotateDuration = abs(angle)/(2*math.pi)*maxRotationDuration
					if angle != 0.0:
						rotateAction = RotateBy(rotateDuration, angle)
			actions.append(action)
		Sequence.__init__(self, *actions)

	def start(self, owner):
		Sequence.start(self, owner)
		owner.setPosition(self._path.getPoints()[0])
		if self._isAutorotating:
			owner.setRotation(self._startingAngle)


class JumpBy(AbstractIntervalAction):
	"""
	Moves a L{Node} by a certain distance by having it "jump" to its final destination.
	"""
	def __init__(self, duration, position, height, jumps):
		"""
		Initialization method.

		@param duration: How long the action will take.
		@type duration: Non-negative C{float}
		@param position: How far in the x-axis and y-axis the object should be moved.
		@type position: L{Point}
		@param height: How high each jump should be
		@type height: C{float}
		@param jumps: The number of jumps to be performed before reaching the final destination.
		@type jumps: Non-negative C{int}
		"""
		AbstractIntervalAction.__init__(self, duration)
		self._delta = position
		self._height = height
		self._jumps = jumps
		self._startPosition = PointZero()

	def start(self, owner):
		AbstractIntervalAction.start(self, owner)
		self._startPosition = self._owner.getPosition()

	def update(self, time):
		fraction = math.fmod(time * self._jumps, 1.0)
		y = self._height * 4 * fraction * (1-fraction)
		y += self._delta.y * time
		x = self._delta.x * time
		point = pointAdd(Point(x,y), self._startPosition)
		self._owner.setPosition(point)

	def reverse(self):
		"""
		Returns a new JumpBy whose distance values are negative of the original.

		@return: A new, reversed JumpBy.
		@rtype: L{JumpBy}
		"""
		return JumpBy(self._duration, Point(-self._delta.x, -self._delta.y), self._height, self._jumps)

class JumpTo(JumpBy):
	"""
	Moves a L{Node} to a certain L{Point} by having it "jump" there.
	"""
	def start(self, owner):
		JumpBy.start(self, owner)
		self._delta = Point(self._delta.x-self._startPosition.x, self._delta.y-self._startPosition.y)

def bezierat(a, b, c, d, t):
	"""
	Calculates cubic Bezier curve's value for the given parameters in a certain axis. Starts a point a going toward point b, then ends at point d coming from point c.

	@param a: Axis value of point a (e.g. y-value).
	@type a: C{float}
	@param b: Axis value of point b.
	@type b: C{float}
	@param c: Axis value of point c.
	@type c: C{float}
	@param d: Axis value of point d.
	@type d: C{float}
	@param t: Where in the Bezier curve (percentage). Between C{0.0} and C{1.0}.
	@type t: C{float}
	"""
	return math.pow(1-t,3)*a + 3*t*math.pow(1-t,2)*b + 3*math.pow(t,2)*(1-t)*c + math.pow(t,3)*d

class BezierConfiguration:
	"""
	An object which holds parameter values for a Bezier curve. Used in L{BezierBy}. A BezierConfiguration is considered a primitive, thus its values may be directly accessed.
	"""
	def __init__(self, endPosition=None, controlPoint1=None, controlPoint2=None):
		"""
		Initialization method.

		@param endPosition: The end position of the curve. Default is L{PointZero}.
		@type endPosition: L{Point}
		@param controlPoint1: A control point for the curve. Default is L{PointZero}.
		@type controlPoint1: L{Point}
		@param controlPoint2: A control point for the curve. Default is L{PointZero}.
		@type controlPoint2: L{Point}

		"""
		if endPosition is None:
			endPosition = PointZero()
		if controlPoint1 is None:
			controlPoint1 = PointZero()
		if controlPoint2 is None:
			controlPoint2 = PointZero()
		self.endPosition = endPosition	#: The end position of the curve.
		self.controlPoint1 = controlPoint1	#: A control point for the curve.
		self.controlPoint2 = controlPoint2	#: A control point for the curve.

	def copy(self):
		"""
		Returns a copy of the configuration with the same end position and control points as the original.
		"""
		return BezierConfiguration(self.endPosition, self.controlPoint1, self.controlPoint2)

class BezierBy(AbstractIntervalAction):
	"""
	Moves a L{Node} along a curved path as defined by a L{BezierConfiguration}.
	"""
	def __init__(self, duration, configuration):
		"""
		Initialization method.

		@param duration: How long the Action will take.
		@type duration: Non-negative C{float}
		@param configuration: The Bezier configuration for the curve.
		@type configuration: L{BezierConfiguration}
		"""
		AbstractIntervalAction.__init__(self, duration)
		self._configuration = configuration
		self._startPosition = PointZero()

	def start(self, owner):
		AbstractIntervalAction.start(self, owner)
		self._startPosition = self._owner.getPosition()

	def update(self, time):
		xa = 0
		xb = self._configuration.controlPoint1.x
		xc = self._configuration.controlPoint2.x
		xd = self._configuration.endPosition.x

		ya = 0
		yb = self._configuration.controlPoint1.y
		yc = self._configuration.controlPoint2.y
		yd = self._configuration.endPosition.y

		x = bezierat(xa, xb, xc, xd, time)
		y = bezierat(ya, yb, yc, yd, time)
		point = pointAdd(Point(x,y), self._startPosition)
		self._owner.setPosition(point)

	def reverse(self):
		"""
		Returns a new BezierBy whose configuration reverses the curve path.

		@return: A new, reversed BezierBy.
		@rtype: L{BezierBy}.
		"""
		configuration = BezierConfiguration()
		configuration.endPosition = pointNeg(self._configuration.endPosition)
		configuration.controlPoint1 = pointAdd(self._configuration.controlPoint2, pointNeg(self._configuration.endPosition))
		configuration.controlPoint2 = pointAdd(self._configuration.controlPoint1, pointNeg(self._configuration.endPosition))
		return BezierBy(self._duration, configuration)

class BezierTo(BezierBy):
	"""
	Moves a L{Node} to a specified L{Point} by following a Bezier curve.
	"""
	def start(self, owner):
		BezierBy.start(self, owner)
		self._configuration.controlPoint1 = pointSub(self._configuration.controlPoint1, self._startPosition)
		self._configuration.controlPoint2 = pointSub(self._configuration.controlPoint2, self._startPosition)
		self._configuration.endPosition = pointSub(self._configuration.endPosition, self._startPosition)

class ScaleTo(AbstractIntervalAction):
	"""
	Scales a L{Node} to a specified percentage in both the x- and y-axes.
	"""
	def __init__(self, duration, scaleX, scaleY=None):
		"""
		Initialization method.

		@param duration: How long the Action will take.
		@type duration: Non-negative C{float}
		@param scaleX: The percentage to which the Node will be scaled in the x-axis. Should be between C{0.0} and C{1.0}.
		@type scaleX: C{float}
		@param scaleY: The percentage to which the Node will be scaled in the y-axis. Should be between C{0.0} and C{1.0}. If C{scaleY} is not given, then scaleY will be set to the value given for scaleX.
		@type scaleY: C{float} (or C{None})
		"""
		AbstractIntervalAction.__init__(self, duration)
		if scaleY is None:
			scaleY = scaleX
		self._endScaleX = scaleX
		self._endScaleY = scaleY
		self._scaleX = self._scaleY = 0
		self._startScaleX = self._startScaleY = 0
		self._deltaX = self._deltaY = 0

	def start(self, owner):
		AbstractIntervalAction.start(self, owner)
		self._startScaleX = self._owner.getScaleX()
		self._startScaleY = self._owner.getScaleY()
		self._deltaX = self._endScaleX - self._startScaleX
		self._deltaY = self._endScaleY - self._startScaleY

	def update(self, time):
		self._owner.setScaleX(self._startScaleX + self._deltaX * time)
		self._owner.setScaleY(self._startScaleY + self._deltaY * time)


class ScaleBy(ScaleTo):
	"""
	Scales a L{Node} by a specified percentage in both the x- and y-axes.
	"""
	def start(self, owner):
		ScaleTo.start(self, owner)
		self._deltaX = self._startScaleX * self._endScaleX - self._startScaleX
		self._deltaY = self._startScaleY * self._endScaleY - self._startScaleY

	def reverse(self):
		return ScaleBy(self._duration, 1/self._endScaleX, 1/self._endScaleY)

class Blink(AbstractIntervalAction):
	"""
	Makes a L{Node} alternately visible and invisible.
	"""
	def __init__(self, duration, blinks):
		"""
		Initialization method.

		@param duration: How long the Action will take.
		@type duration: Non-negative C{float}
		@param blinks: The number of times the Node will blink.
		@type blinks: Non-negative C{int}
		"""
		AbstractIntervalAction.__init__(self, duration)
		self._times = blinks

	def update(self, time):
		timeSlice = 1.0 / self._times
		m = math.fmod(time, timeSlice)
		if m > timeSlice / 2:
			self._owner.setVisible(True)
		else:
			self._owner.setVisible(False)

	def reverse(self):
		return Blink(self._duration, self._times)

class FadeIn(AbstractIntervalAction):
	"""
	Fades in a Node (makes it visible). If using this, it may be necessary to set the L{Node}C{'s} opacity to C{0.0} before starting FadeIn.
	"""
	def update(self, time):
		self._owner.setOpacity(1.0 * time)

	def reverse(self):
		"""
		Returns a FadeOut with the same duration.

		@return: A new FadeOut.
		@rtype: L{FadeOut}
		"""
		return FadeOut(self._duration)

class FadeOut(AbstractIntervalAction):
	"""
	Fades out a Node (makes it invisible). If using this, it may be necessary to set the L{Node}C{'s} opacity to C{1.0} before starting FadeOut.
	"""
	def update(self, time):
		self._owner.setOpacity(1.0 * (1.0-time))

	def reverse(self):
		"""
		Returns a FadeIn with the same duration.

		@return: A new FadeIn.
		@rtype: L{FadeIn}
		"""
		return FadeIn(self._duration)

class FadeTo(AbstractIntervalAction):
	"""
	Fades a L{Node} to a specified opacity.
	"""
	def __init__(self, duration, opacity):
		"""
		Initialization method.

		@param duration: How long the Action will take.
		@type duration: Non-negative C{float}
		@param opacity: The final opacity of the Node (between C{0.0} and C{1.0}).
		@type opacity: C{float}
		"""
		AbstractIntervalAction.__init__(self, duration)
		self._toOpacity = opacity
		self._fromOpacity = 0.0

	def start(self, owner):
		AbstractIntervalAction.start(self, owner)
		self._fromOpacity = self._owner.opacity

	def update(self, time):
		opacity = self._fromOpacity + (self._toOpacity - self._fromOpacity) * time
		self._owner.setOpacity(opacity)


class TintTo(AbstractIntervalAction):
	"""
	Changes the color value of a L{Node} which uses C{Node.getColor} and C{Node.setColor} (e.g. a L{Sprite}).
	"""
	def __init__(self, duration, r, g, b, a=1.0):
		"""
		Initialization method.

		@param duration: How long the Action will take.
		@type duration: Non-negative C{float}
		@param r: The red value from C{0.0} to C{1.0}.
		@type r: C{float}
		@param g: The green value from C{0.0} to C{1.0}.
		@type g: C{float}
		@param b: The blue value from C{0.0} to C{1.0}.
		@type b: C{float}
		@param a: The alpha value from C{0.0} to C{1.0}.
		@type a: C{float}
		"""
		AbstractIntervalAction.__init__(self, duration)
		self._toColor = Color(r, g, b, a)
		self._fromColor = None

	def start(self, owner):
		AbstractIntervalAction.start(self, owner)
		self._fromColor = self._owner.getColor()

	def update(self, time):
		r = self._fromColor.r + (self._toColor.r-self._fromColor.r)*time
		g = self._fromColor.g + (self._toColor.g-self._fromColor.g)*time
		b = self._fromColor.b + (self._toColor.b-self._fromColor.b)*time
		a = self._fromColor.a + (self._toColor.a-self._fromColor.a)*time
		color = Color(r, g, b, a)
		self._owner.setColor(color)

class TintBy(AbstractIntervalAction):
	"""
	Changes the color value of a L{Node} by a certain amount given for each color channel.
	"""
	def __init__(self, duration, r, g, b, a=1.0):
		"""
		Initialization method.

		@param duration: How long the Action will take.
		@type duration: Non-negative C{float}
		@param r: The red value from C{0.0} to C{1.0}.
		@type r: C{float}
		@param g: The green value from C{0.0} to C{1.0}.
		@type g: C{float}
		@param b: The blue value from C{0.0} to C{1.0}.
		@type b: C{float}
		@param a: The alpha value from C{0.0} to C{1.0}.
		@type a: C{float}
		"""
		AbstractIntervalAction.__init__(self, duration)
		self._deltaColor = Color(r, g, b, a)
		self._fromColor = None

	def start(self, owner):
		AbstractIntervalAction.start(self, owner)
		self._fromColor = self._owner.getColor()

	def update(self, time):
		r = self._fromColor.r + self._deltaColor.r * time
		g = self._fromColor.g + self._deltaColor.g * time
		b = self._fromColor.b + self._deltaColor.b * time
		a = self._fromColor.a + self._deltaColor.a * time
		color = Color(r, g, b, a)
		self._owner.setColor(color)

	def reverse(self):
		"""
		Returns a new TintBy whose color values are the negatives of the original.

		@return: A new TintBy.
		@rtype: L{TintBy}
		"""
		return TintBy(self._duration, -self._deltaColor.r, -self._deltaColor.g, -self._deltaColor.b, -self._deltaColor.a)


class ReverseTime(AbstractIntervalAction):
	"""
	An L{AbstractIntervalAction} whose wrapped Action is run in reverse.
	"""
	def __init__(self, action):
		"""
		Initialization method.

		@param action: The Action to be run in reverse.
		@type action: L{AbstractIntervalAction}
		"""
		AbstractIntervalAction.__init__(self, action._duration)
		self._otherAction = action

	def start(self, owner):
		AbstractIntervalAction.start(self, owner)
		self._otherAction.start(owner)

	def stop(self):
		AbstractIntervalAction.stop(self)
		self._otherAction.stop()

	def update(self, time):
		self._otherAction.update(1.0-time)

#	def reverse(self):
#		TODO: implement copying for all Actions

'''
class Animate(AbstractIntervalAction):
	"""
	Animates a L{Sprite} with a series of pre-rendered images.
	"""
	def __init__(self, animation, shouldRestoreOriginalFrame=True):
		"""
		Initialization method.
		"""
		duration = animation.getNumberOfFrames() * animation.delay
		AbstractIntervalAction.__init__(self, duration)
		self._shouldRestoreOriginalFrame = shouldRestoreOriginalFrame
		self._animation = animation
		self._originalFrame = None

	def start(self, owner):
		AbstractIntervalAction.start(self, owner)
		self._originalFrame = self._owner.getDisplayFrame()

	def stop(self):
		if self._shouldRestoreOriginalFrame:
			self._owner.setDisplayFrame(self._originalFrame)
		AbstractIntervalAction.stop(self)

	def update(self, time):
		index = 0
		timeSlice = 1.0 / self._animation.getNumberOfFrames()
		if index != 0:
			index = time / timeSlice
		if index >= self._animation.getNumberOfFrames():
			index = self._animation.getNumberOfFrames() - 1
		frame = self._animation.getFrameAtIndex(index)
		if not self._owner.isFrameDisplayed(frame):
			self._owner.setDisplayFrame(frame)
'''
