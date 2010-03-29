"""
The central part of the application.
"""

from Geometry import *

from GTKInterface import *
from GTKWindow import *

from GestureDispatch import *
from ActionManager import *
from Scheduler import *

from Transition import *

from Color import *

import gobject
import time

import warnings

gobject.threads_init()


class Director:
	"""
	The central point of the application. It handles the main run loop, L{Scene} transitions, and propagating redraw events to the Scene's children. It is also the owner of the L{GestureDispatch}, L{ActionManager}, L{Scheduler}, and the L{GTKInterface}.

	Normally only one Director should exist per application.
	"""
	def __init__(self):
		"""
		Initialization method.
		"""
		self._gtkInterface = None	# set this up in setWindow()
		self._gestureDispatch = GestureDispatch()
		self._scheduler = Scheduler()
		self._actionManager = ActionManager(self._scheduler)

		self._isShowingFPS = False

		self._runningScene = None
		self._nextScene = None
		self._scenesStack = []

		self._oldAnimationInterval = 1.0/30.0
		self._animationInterval = 1.0/30.0
		self._frames = 0
		self._isPaused = False
		self._dt = 0
		self._isNextDeltaTimeZero = False
		self._lastTimeStamp = 0
		#self._accumDt = 0		# TODO: finish implementing these
		#self._frameRate = 0
		self._isRecording = False
		self._backgroundColor = BlackColor()

#{ Accessor methods.
	def isShowingFPS(self):
		"""
		Whether or not the Director is displaying frames per second. Default is C{False}.

		@return: Whether or not the Director is displaying frames per second (FPS).
		@rtype: L{bool}
		"""
		return self._isShowingFPS

	def setShowingFPS(self, isShowingFPS):
		"""
		Sets whether or not the Director displays frames per second.

		@param isShowingFPS: Whether or not the Director displays frames per second.
		@type isShowingFPS: C{bool}
		"""
		self._isShowingFPS = isShowingFPS

	def getSize(self):
		"""
		Returns the size of the main application window.

		@return: Size of the main application window.
		@rtype: L{Size}
		"""
		return self._gtkInterface.getSize()

	def getGestureDispatch(self):
		"""
		Returns the L{GestureDispatch} for the application, which sends out notifications of L{GestureEvent}s to L{GestureListener}s.

		@return: The dispatch.
		@rtype: L{GestureDispatch}
		"""
		return self._gestureDispatch

	def getActionManager(self):
		"""
		Reutrns the L{ActionManager} for the application, which manages the L{Action}s.

		@return: The manager.
		@rtype: L{ActionManager}
		"""
		return self._actionManager

	def getScheduler(self):
		"""
		Returns the L{Scheduler} for the application, which manages the L{Timer}s.

		@return: The scheduler.
		@rtype: L{Scheduler}
		"""
		return self._scheduler

	def setBackgroundColor(self, color):
		"""
		Sets the color for the background of the application.

		@param color: The color of the background.
		@type color: L{Color}
		"""
		if self._gtkInterface is not None:
			self._gtkInterface.setBackgroundColor(color)
		self._backgroundColor = color

	def setWindow(self, window=None):
		"""
		Sets the main window for the application. If window is C{None}, a L{GTKWindow} is generated automatically.

		@param window: The main application window.
		@type window: L{AbstractWindow} (or C{None})
		"""
		if self._gtkInterface == None:
			self._gtkInterface = GTKInterface(self, window) # if window is None, defaults to GTKWindow()
			self._gtkInterface.setBackgroundColor(self._backgroundColor)
		else:
			warnings.warn("Window is already set.")

	def getGTKLayout(self):
		if self._gtkInterface is not None:
			return self._gtkInterface.getGTKLayout()
		else:
			return None
#}


#{ Scene methods.
	def getRunningScene(self):
		"""
		Returns the L{Scene} which is currently running or C{None} if there is not a scene currently running.

		@return: The running Scene.
		@rtype: L{Scene} (or C{None})
		"""
		return self._runningScene

	def runWithScene(self, scene):
		"""
		Starts the application with a L{Scene}. This starts the main run loop.

		@param scene: The opening scene.
		@type scene: L{Scene}
		"""

		if self._runningScene:
			warnings.warn("Scene is already running. Use replaceScene or pushScene instead.")
			return

		self.pushScene(scene)
		self._startAnimation()

	def replaceScene(self, scene):
		"""
		Replaces the currently running L{Scene} with a new Scene.

		@param scene: The new Scene.
		@type scene: L{Scene}
		"""
		scene.setRect(Rect(Point(0,0), self._gtkInterface.getSize()))
		scene._setDirector(self)
		index = len(self._scenesStack)-1
		self._scenesStack[index] = scene
		self._nextScene = scene

	def pushScene(self, scene):
		"""
		Pushes a new L{Scene} onto the stack of Scenes.

		@param scene: The new Scene.
		@type scene: L{Scene}
		"""
		scene.setRect(Rect(Point(0,0), self._gtkInterface.getSize()))
		scene._setDirector(self)
		self._scenesStack.append(scene)
		self._nextScene = scene

	def popScene(self):
		"""
		Pops the most recently-pushed L{Scene} off the stack of Scenes.
		"""
		scene = self._scenesStack.pop()
		count = len(self._scenesStack)
		if count == 0:
			self.end()
		else:
			self._nextScene = self._scenesStack[count-1]
#}


#{ Run methods.
	def end(self):
		"""
		Ends all animations, unregisters all L{GestureDispatch} listeners, and clears out the stack of L{Scene}s. This does not end the program by itself, however.
		"""
		self._runningScene.onExit()
		self._runningScene.cleanup()
		self._scenesStack = []
		self._gestureDispatch.removeAllListeners()
		self._stopAnimation()

	def _setNextScene(self):
		"""
		Private method which handles setting the next L{Scene}. This should not normally be called manually.
		"""
		isTransitionRunning = isinstance(self._runningScene, AbstractTransition)
		isTransitionNext = isinstance(self._nextScene, AbstractTransition)
		if isTransitionNext is not True and self._runningScene is not None:
			self._runningScene.onExit()
		self._runningScene = self._nextScene
		self._nextScene = None
		if isTransitionRunning is not True:
			self._runningScene.onEnter()
			self._runningScene.onEnterFromFinishedTransition()

	def getAnimationInterval(self):
		"""
		Returns the animation interval. Default is C{30.0} FPS.

		@return: Animation interval.
		@rtype: C{float}
		"""
		return self._animationInterval

	def setAnimationInterval(self, animationInterval):
		"""
		Sets the animation interval, that is, the frames per second for the application. Note that this must be set before L{runWithScene} is called, otherwise this method will have no effect.

		@param animationInterval: The animation interval (FPS).
		@type animationInterval: C{float}
		"""
		self._animationInterval = animationInterval

	def pause(self):
		"""
		Pauses the application.
		"""
		if self._isPaused:
			return
		self._oldAnimationInterval = self._animationInterval
		self.setAnimationInterval(1.0/4.0)
		self._isPaused = True

	def resume(self):
		"""
		Resumes the application.
		"""
		if not self._isPaused:
			return
		self.setAnimationInterval(self._oldAnimationInterval)
		self._isPaused = False
		self._dt = 0
#}


#{ Private methods.
	def _startAnimation(self):
		"""
		Private method that calls L{_preMainLoop} to begin the main loop.
		"""
		self._isRunning = True

		self._preMainLoop()
		self._gtkInterface.start()

	def _preMainLoop(self):
		"""
		Private method that sets up the L{_mainLoop} method to be called repeatedly.
		"""
		interval = self._animationInterval*1000
		interval = int(interval)
		gobject.timeout_add(interval, self._mainLoop)

	def _mainLoop(self):
		"""
		Private method which is called repeatedly to redraw the L{Node}s and to update the L{Scheduler} with the time that has passed since the last loop.
		"""
		self._calculateDeltaTime()
		if not self._isPaused:
			if not self._isRecording:
				self._scheduler.tick(self._dt)
			else:
				self._scheduler.tick(self._animationInterval)
		if self._nextScene is not None:
			self._setNextScene()
		self._gtkInterface.redraw()

		if self._isRunning:
			return True
		else:
			return False

	def _calculateDeltaTime(self):
		"""
		Private method which calculates how much time has elapsed since the last loop iteration. This method should generally not be called manually.
		"""
		timestamp = time.time()	# now
		if self._isNextDeltaTimeZero:
			self._dt = 0
			self._isNextDeltaTimeZero = False
		#elif self._lastTimeStamp == 0.0:
		#	self._dt = 0
		else:
			self._dt = timestamp - self._lastTimeStamp
		self._lastTimeStamp = timestamp

	def _stopAnimation(self):
		"""
		Private method which stops the main loop.
		"""
		self._isRunning = False
		self.stopRecording()
#}

#{ Recording methods.
	def takeScreenshot(self, imagePath):
		"""
		Takes a screenshot of the application. Note that PyGTK widgets will not be rendered to the image.

		@param imagePath: The name of the file to be saved.
		@type imagePath: C{string}
		"""
		self._gtkInterface._layout.takeScreenshot(imagePath)

	def startRecording(self, directoryPath):
		self._isRecording = True
		self._gtkInterface._layout.startRecording(directoryPath)

	def stopRecording(self):
		self._isRecording = False
		self._gtkInterface._layout.stopRecording()
#}
