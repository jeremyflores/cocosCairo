from cocosCairo.cocosCairo import *

class SplashScene(Scene):
	def __init__(self, transition):
		Scene.__init__(self)
		self._transition = transition

	def setup(self):
		self.setBackgroundColor(WhiteColor())
		self.label = PangoLabel('<span foreground="#000000">cocos</span><span foreground="#0000FF" background="#000000" rise="00000">\nCairo</span>', Point(630,-200))
		self.label.setAnchorPoint(Point(0.5, 0.5))
		self.label.setFontSize(72)
		self.label.setSpacing(20)
		self.label.setRotation(0.3)
		self.addChild(self.label)

	def onEnterFromFinishedTransition(self):
		Scene.onEnterFromFinishedTransition(self)
		moveAction = MoveBy(1.5, Point(0, 600))
		moveAction = EaseBounceOut(moveAction)
		delayAction1 = DelayTime(0.5)
		rotateAction1 = RotateBy(0.5, -0.4)
		rotateAction1 = EaseExponentialInOut(rotateAction1)
		rotateAction2 = RotateBy(0.5, 0.2)
		rotateAction2 = EaseExponentialInOut(rotateAction2)
		rotateAction3 = RotateBy(0.5, -0.1)
		rotateAction3 = EaseExponentialInOut(rotateAction3)
		delayAction2 = DelayTime(1.5)
		callbackAction = CallbackInstantAction(self.onSequenceCompletion)
		sequence = Sequence(moveAction, delayAction1, rotateAction1, rotateAction2, rotateAction3, delayAction2, callbackAction)
		self.label.runAction(sequence)

	def onSequenceCompletion(self):
		self.getDirector().replaceScene(self._transition)
