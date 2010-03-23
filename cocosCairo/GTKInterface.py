import pygtk
pygtk.require('2.0')
import gtk

from GTKWindow import *
from Geometry import *
from AbstractWindow import *

from Color import *

import os

GTK_EVENT_MASKS = gtk.gdk.BUTTON_RELEASE_MASK | gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.ENTER_NOTIFY_MASK | gtk.gdk.LEAVE_NOTIFY_MASK | gtk.gdk.POINTER_MOTION_MASK | gtk.gdk.POINTER_MOTION_HINT_MASK | gtk.gdk.KEY_PRESS_MASK | gtk.gdk.KEY_RELEASE_MASK | gtk.gdk.SCROLL_MASK


# TODO: implement double buffering

class GTKLayout(gtk.Layout):
	"""
	A GTK widget to which any L{Scene} is "attached" for rendering. Any L{Node}, therefore, is drawn onto this (which writes to the video hardware). Most applications should never have to directly talk to the GTKLayout as the L{Director} will handle this by childing / de-childing Scenes automatically.
	"""
	def __init__(self, director, size, color):
		gtk.Layout.__init__(self)
		self._director = director
		self._color = color
		self._size = size
		#self.set_double_buffered(True)	# this is possibly set by default. need to come up with another double buffering solution
		self._screenshotPath = ""
		self._screenshotName = ""
		self._isRecording = False
		self._exposeCounter = 0
		self.set_flags(gtk.CAN_FOCUS)
		self.grab_focus()
		self.set_events(GTK_EVENT_MASKS)
		self.set_size_request(size.width, size.height)
		self.connect("expose-event", self._onExpose)
		gestureDispatch = self._director.getGestureDispatch()
		self.connect("motion-notify-event", gestureDispatch._onMouseMotion)
		self.connect("button-press-event", gestureDispatch._onMousePress)
		self.connect("button-release-event", gestureDispatch._onMouseRelease)
		self.connect("scroll-event", gestureDispatch._onMouseScroll)
		self.connect("key-press-event", gestureDispatch._onKeyPress)
		self.connect("key-release-event", gestureDispatch._onKeyRelease)

	def startRecording(self, directoryPath):
		if self._isRecording is True:
			return
		directoryPath = directoryPath.strip()
		separator = os.sep
		if directoryPath[-1:] is not separator:
			directoryPath += separator
		self._screenshotPath = directoryPath
		self._screenshotName = "record.png"
		if not os.path.exists(self._screenshotPath):
			os.makedirs(self._screenshotPath)
		self._isRecording = True

	def stopRecording(self):
		self._isRecording = False

	def takeScreenshot(self, screenshotPath):
		"""
		Takes a screenshot of the next expose event and saves it to the specified file. Note that PyGTK widgets will not appear in the screenshot as it will only render the gtk.Layout.

		@param screenshotPath: The path for the file to be saved.
		@type screenshotPath: C{string}
		"""
		screenshotPath = screenshotPath.strip()
		if screenshotPath.endswith(".png") is not True:
			screenshotPath += ".png"
		separator = os.sep
		self._screenshotPath = os.path.split(screenshotPath)[0] + separator
		self._screenshotName = os.path.split(screenshotPath)[1]
		if not os.path.exists(self._screenshotPath):
			os.makedirs(self._screenshotPath)

	def _onExpose(self, widget, event):
		context = widget.bin_window.cairo_create()

		# Push a new context state onto the stack
		context.save()

		# Clip the context
		context.rectangle(event.area.x, event.area.y, event.area.width, event.area.height)
		context.clip()

		# Draw the background color
		context.set_source_rgba(self._color.r, self._color.g, self._color.b, self._color.a)
		context.rectangle(event.area.x, event.area.y, event.area.width, event.area.height)
		context.fill()

		# Traverse the node tree.
		scene = self._director.getRunningScene()
		if scene is not None:
			scene._visit(context)

		# Done with the new context state, so pop it.
		context.restore()

		if self._screenshotPath is not "":
			if self._isRecording is True:
				path = self._screenshotPath + str(self._exposeCounter) + "_" + self._screenshotName
			else:
				path = self._screenshotPath + self._screenshotName
			surface = context.get_group_target()
			surface.write_to_png(path)
			if self._isRecording is not True:
				self._screenshotPath = ""

		self._exposeCounter += 1


# TODO: this class will likely have to change to appropriately accommodate both Sugar activities and normal windowed applications.
class GTKInterface:
	"""
	"""
	def _destroy(self, widget):
		self._director._stopAnimation()
		gtk.main_quit()

	def __init__(self, director, window=None, size=None, color=None):
		"""
		Initialization method.
		
		@param window: The main application window.
		@type window: L{AbstractWindow}.
		@param size: The size of the window.
		@type size: 
		"""
		if window is None:
			window = GTKWindow()
		if size is None:
			size = Size(800,600)
		if color is None:
			color = BlackColor()
		self._director = director
		self._window = window
		self._window.connect("destroy", self._destroy)
		self._window.set_size_request(size.width, size.height)
		self._layout = GTKLayout(director, size, color)
		self._window.add(self._layout)
		self._size = size

	def getGTKLayout(self):
		return self._layout

	def getSize(self):
		return self._size

	def redraw(self):
		self._layout.queue_draw()

	def setBackgroundColor(self, color):
		self._layout._color = color

	def start(self):
		self._window.show_all()
		gtk.main()
