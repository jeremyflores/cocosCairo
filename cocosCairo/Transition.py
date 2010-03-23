from Director import *
from GestureDispatch import *
from Scene import *
from IntervalAction import *
from InstantAction import *
from EaseAction import *
from ColorNode import *

import math

import warnings

class AbstractTransition(Scene):
	"""
	A type of L{Scene} that provides a transition animation from the currently-running Scene to a new Scene. Subclasses provide the different transition animations.
	"""
	def __init__(self, duration, destinationScene):
		"""
		Initialization method.

		@param duration: The duration of the transition.
		@type duration: C{float} (should be greater than 0.0).
		@param destinationScene: The Scene to which this will be transitioning.
		@type destinationScene: L{Scene}.
		"""
		Scene.__init__(self)
		self._duration = duration
		self._dstScene = destinationScene
		self._srcScene = None	# defined in setDirector
		self._isDstSceneOnTop = True
		self._sceneOrder()

#{ Subclass methods.
	def _sceneOrder(self):
		"""
		Method for subclasses to override so that they may determine whether or not the destination L{Scene} is rendered above the source Scene. Default is C{True}.
		"""
		self._isDstSceneOnTop = True

	def hideSourceShowDestination(self):
		"""
		Method for subclasses to hide the source L{Scene} and show the destination Scene.
		"""
		self._dstScene.setVisible(True)
		self._srcScene.setVisible(False)
#}


#{ Private methods.
	def finish(self):
		"""
		Private method which should be called when the Transition is finished with its L{Action}s.
		"""
		self._dstScene.setVisible(True)
		self._dstScene.setPosition(Point(0,0))
		self._dstScene.setScale(1.0)
		self._dstScene.setRotation(0.0)

		self._srcScene.setVisible(False)
		self._srcScene.setPosition(Point(0,0))
		self._srcScene.setScale(1.0)
		self._srcScene.setRotation(0.0)

		self.scheduleCallback(self.setNewScene)

	def setNewScene(self, dt):
		"""
		Private method called after the Transition is finshed to re-enable the L{GestureDispatch} and replace the currently running L{Scene} from the Transition to the destination Scene.
		"""
		self.unscheduleCallback(self.setNewScene)
		self.getDirector().replaceScene(self._dstScene)
		gestureDispatch = self.getDirector().getGestureDispatch()
		gestureDispatch.setDispatching(True)	# re-enable events now that transition is done
		self._srcScene.setVisible(True)	# TODO: see if this is necessary (re: cocos2d-iPhone Issue #267)
#}


	def setDirector(self, director):
		Scene.setDirector(self, director)
		self._dstScene.setDirector(director)
		gestureDispatch = self.getDirector().getGestureDispatch()
		gestureDispatch.setDispatching(False)	# disable events while transitioning
		self._srcScene = director.getRunningScene()
		self._dstScene.setRect(self._srcScene.getRect())
		if self._srcScene == self._dstScene:
			warnings.warn("TransitionScene's source and destination Scenes are the same.")

	def draw(self, context):
		if self._isDstSceneOnTop:
			self._srcScene._visit(context)
			self._dstScene._visit(context)
		else:
			self._dstScene._visit(context)
			self._srcScene._visit(context)

	def onEnter(self):
		Scene.onEnter(self)
		self._dstScene.onEnter()

	def onExit(self):
		Scene.onExit(self)
		self._srcScene.onExit()
		self._dstScene.onEnterFromFinishedTransition()

	def onEnterFromFinishedTransition(self):
		Scene.onEnterFromFinishedTransition(self)



class RotoZoomTransition(AbstractTransition):
	"""
	A L{Transition} that spins and zooms out the previous L{Scene} then spins and zooms in on the next Scene.
	"""
	def onEnter(self):
		AbstractTransition.onEnter(self)
		self._dstScene.setScale(0.001)
		self._srcScene.setScale(1.0)
		self._dstScene.setAnchorPoint(Point(0.5, 0.5))
		self._srcScene.setAnchorPoint(Point(0.5, 0.5))
		scaleAction1 = ScaleTo(self._duration/2, 0.001)
		rotateAction1 = RotateBy(self._duration/2, math.pi*2)
		spawnAction1 = Spawn(scaleAction1, rotateAction1)
		self._srcScene.runAction(spawnAction1)
		scaleAction2 = ScaleTo(self._duration/2, 1.0)
		rotateAction2 = RotateBy(self._duration/2, math.pi*2)
		spawnAction2 = Spawn(scaleAction2, rotateAction2)
		delayAction2 = DelayTime(self._duration/2)
		sequence2 = Sequence(delayAction2, spawnAction2, CallbackInstantAction(self.finish))
		self._dstScene.runAction(sequence2)


class ShrinkGrowTransition(AbstractTransition):
	"""
	A L{Transition} that shrinks the previous L{Scene} then grows the next Scene.
	"""
	def onEnter(self):
		AbstractTransition.onEnter(self)
		self._dstScene.setScale(0.001)
		self._srcScene.setScale(1.0)
		self._srcScene.setAnchorPoint(Point(2.0/3.0, 0.5))
		self._dstScene.setAnchorPoint(Point(1.0/3.0, 0.5))
		scaleDst = EaseInOut(ScaleTo(self._duration, 1.0), 2.0)
		scaleSrc = EaseInOut(ScaleTo(self._duration, 0.001), 2.0)
		sequence = Sequence(scaleSrc, CallbackInstantAction(self.finish))
		self._dstScene.runAction(scaleDst)
		self._srcScene.runAction(sequence)

class JumpZoomTransition(AbstractTransition):
	"""
	A L{Transition} that shrinks the previous L{Scene} and has it jump off-screen, then has the next Scene jump on-screen and grow.
	"""
	def onEnter(self):
		AbstractTransition.onEnter(self)
		size = self.getDirector().getSize()
		self._dstScene.setScale(0.5)
		self._dstScene.setPosition(Point(size.width, 0))
		self._dstScene.setAnchorPoint(Point(0.5, 0.5))
		self._srcScene.setAnchorPoint(Point(0.5, 0.5))
		jump = JumpBy(self._duration/4, Point(-size.width, 0), -size.width/4, 2)
		scaleIn = ScaleTo(self._duration/4, 1.0)
		scaleOut = ScaleTo(self._duration/4, 0.5)
		jumpZoomOut = Sequence(scaleOut, jump)
		jumpZoomIn = Sequence(jump, scaleIn)
		delay = DelayTime(self._duration/2)
		sequence = Sequence(delay, jumpZoomIn, CallbackInstantAction(self.finish))
		self._srcScene.runAction(jumpZoomOut)
		self._dstScene.runAction(sequence)


class MoveInLeftTransition(AbstractTransition):
	"""
	A L{Transition} that leaves the previous L{Scene} in place and has the next Scene slide over it coming from left to right.
	"""
	def onEnter(self):
		AbstractTransition.onEnter(self)
		self._initializeScenes()
		action = self._getAction()
		action = self._easeAction(action)
		sequence = Sequence(action, CallbackInstantAction(self.finish))
		self._dstScene.runAction(sequence)
		
	def _initializeScenes(self):
		width = self.getDirector().getSize().width
		self._dstScene.setPosition(Point(-width, 0))

	def _getAction(self):
		return MoveTo(self._duration, Point(0,0))

	def _easeAction(self, action):
		return EaseInOut(action, 2.0)

class MoveInRightTransition(MoveInLeftTransition):
	"""
	A L{Transition} that leaves the previous L{Scene} in place and has the next Scene slide over it coming from right to left.
	"""
	def _initializeScenes(self):
		width = self.getDirector().getSize().width
		self._dstScene.setPosition(Point(width, 0))

class MoveInTopTransition(MoveInLeftTransition):
	"""
	A L{Transition} that leaves the previous L{Scene} in place and has the next Scene slide over it coming from top to bottom.
	"""
	def _initializeScenes(self):
		height = self.getDirector().getSize().height
		self._dstScene.setPosition(Point(0, -height))

class MoveInBottomTransition(MoveInLeftTransition):
	"""
	A L{Transition} that leaves the previous L{Scene} in place and has the next Scene slide over it coming from bottom to top.
	"""
	def _initializeScenes(self):
		height = self.getDirector().getSize().height
		self._dstScene.setPosition(Point(0, height))


class SlideInLeftTransition(AbstractTransition):
	"""
	A L{Transition} that pushes out the previous L{Scene} and moves in the next Scene from left to right.
	"""
	def onEnter(self):
		AbstractTransition.onEnter(self)
		self._initializeScenes()
		srcAction = self._getAction()
		dstAction = self._getAction()
		srcAction = self._easeAction(srcAction)
		dstAction = self._easeAction(dstAction)
		dstAction = Sequence(dstAction, CallbackInstantAction(self.finish))
		self._srcScene.runAction(srcAction)
		self._dstScene.runAction(dstAction)

	def _initializeScenes(self):
		width = self.getDirector().getSize().width
		self._dstScene.setPosition(Point(-width, 0))

	def _getAction(self):
		width = self.getDirector().getSize().width
		action = MoveBy(self._duration, Point(width, 0))
		return action

	def _easeAction(self, action):
		return EaseOut(action, 2.0)

	def _sceneOrder(self):
		self._isDstSceneOnTop = False

class SlideInRightTransition(SlideInLeftTransition):
	"""
	A L{Transition} that pushes out the previous L{Scene} and moves in the next Scene from right to left.
	"""
	def _initializeScenes(self):
		width = self.getDirector().getSize().width
		self._dstScene.setPosition(Point(width, 0))

	def _getAction(self):
		width = self.getDirector().getSize().width
		return MoveBy(self._duration, Point(-width, 0))

	def _sceneOrder(self):
		self._isDstSceneOnTop = True

class SlideInTopTransition(SlideInLeftTransition):
	"""
	A L{Transition} that pushes out the previous L{Scene} and moves in the next Scene from top to bottom.
	"""
	def _initializeScenes(self):
		height = self.getDirector().getSize().height
		self._dstScene.setPosition(Point(0, -height))

	def _getAction(self):
		height = self.getDirector().getSize().height
		return MoveBy(self._duration, Point(0, height))

	def _sceneOrder(self):
		self._isDstSceneOnTop = False

class SlideInBottomTransition(SlideInLeftTransition):
	"""
	A L{Transition} that pushes out the previous L{Scene} and moves in the next Scene from bottom to top.
	"""
	def _initializeScenes(self):
		height = self.getDirector().getSize().height
		self._dstScene.setPosition(Point(0, height))

	def _getAction(self):
		height = self.getDirector().getSize().height
		return MoveBy(self._duration, Point(0, -height))

	def _sceneOrder(self):
		self._isDstSceneOnTop = False


class FadeTransition(AbstractTransition):
	"""
	A L{Transition} that fades from the previous L{Scene} to a L{Color} (default is L{BlackColor()}) then fades to the next Scene.
	"""
	def __init__(self, duration, destinationScene, color=None):
		AbstractTransition.__init__(self, duration, destinationScene)
		if color is None:
			color = BlackColor()
		self.setColor(color)

	def onEnter(self):
		AbstractTransition.onEnter(self)
		size = self.getDirector().getSize()
		rect = Rect(Point(0, 0), size)
		colorNode = ColorNode(rect, self.getColor())
		colorNode.setOpacity(0.0)
		self._dstScene.setVisible(False)
		self.addChild(colorNode, 2, "_FadeColorNode")
		fadeInAction = FadeIn(self._duration/2)
		callbackAction1 = CallbackInstantAction(self.hideSourceShowDestination)
		fadeOutAction = FadeOut(self._duration/2)
		callbackAction2 = CallbackInstantAction(self.finish)
		sequence = Sequence(fadeInAction, callbackAction1, fadeOutAction, callbackAction2)
		colorNode.runAction(sequence)

	def onExit(self):
		AbstractTransition.onExit(self)
		self.removeChildByTag("_FadeColorNode", False)
