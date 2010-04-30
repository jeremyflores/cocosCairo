"""
Provides an interface between cocosCairo and PyGTK.
"""

import pygtk
pygtk.require('2.0')
import gtk

from GTKWindow import *
from Geometry import *
from AbstractWindow import *

from Node import *
from Label import *

from Color import *

from threading import Thread
import os
import subprocess
import shlex

GTK_EVENT_MASKS = gtk.gdk.BUTTON_RELEASE_MASK | gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.ENTER_NOTIFY_MASK | gtk.gdk.LEAVE_NOTIFY_MASK | gtk.gdk.POINTER_MOTION_MASK | gtk.gdk.POINTER_MOTION_HINT_MASK | gtk.gdk.KEY_PRESS_MASK | gtk.gdk.KEY_RELEASE_MASK | gtk.gdk.SCROLL_MASK


# TODO: implement double buffering

class GTKLayout(gtk.Layout):
	"""
	A GTK widget to which any L{Scene} is "attached" for rendering. Any L{Node}, therefore, is drawn onto this (which writes to the video hardware). Most applications should never have to directly talk to the GTKLayout as the L{Director} will handle this automatically.
	"""
	def __init__(self, director, size, color):
		gtk.Layout.__init__(self)
		self._canRecord = True
		try:
			s = subprocess.Popen(['ffmpeg'], \
			stderr=subprocess.STDOUT, stdout=subprocess.PIPE).communicate()[0]
		except OSError:
			self._canRecord = False
		self._director = director
		self._color = color
		self._size = size
		#self.set_double_buffered(True)	# this is possibly set by default. need to come up with another double buffering solution
		self._screenshotPath = ""
		self._screenshotName = ""
		self._isRecording = False

		self._renderNode = Node(MakeRect(0,0,self._size.width, self._size.height))
		self._renderNode.setBackgroundColor(Color(1.0, 1.0, 1.0, 0.90))
		label = Label("Rendering video...", color=BlackColor())
		label.setFontSize(36)
		label.setPosition(Point(0, self._size.height/2))
		self._renderNode.addChild(label)

		self._framerate = None
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

	def _makeFFMpegCommand(self):
		"""
		Private method. Returns a formatted string through which FFmpeg is run.
		"""
		fps = str(int(self._director.getAnimationInterval()**-1))
		w = str(int(self._size.width))
		h = str(int(self._size.height))
		string = ""
		string += "ffmpeg -r " + fps + " -i "
		string += self._screenshotPath + "%d_" + self._screenshotName
		string += " -r " + fps + " -s " + w + "x" + h + " -b 700000 "
		string += self._screenshotPath + self._screenshotName[:-4]
		return string

	def _deleteFolderPngs(self, folderPath):
		"""
		Private method. Deletes all PNG files which were generated by L{startRecording}.
		"""
		for theFile in os.listdir(folderPath):
			if not theFile.endswith(self._screenshotName):
				continue
			filePath = os.path.join(folderPath, theFile)
			try:
				if os.path.isfile(filePath):
					os.unlink(filePath)
			except Exception, e:
				pass

	def startRecording(self, videoPath):
		"""
		Private method. Begins saving a sequence of image stills to be rendered to video. This method is called automatically by the L{Director}.

		@param videoPath: The location where the video (and temporary image files) will be saved.
		@type videoPath: C{string}
		"""
		if self._isRecording is True:
			return
		videoPath = videoPath.strip()
		if videoPath.endswith(".avi") is not True:
			videoPath += ".avi"
		videoPath += ".png"	# for generating the PNG still images
		separator = os.sep
		self._screenshotPath = os.path.split(videoPath)[0]
		if self._screenshotPath is "":
			self._screenshotPath = "."
		self._screenshotPath = self._screenshotPath + separator
		self._screenshotName = os.path.split(videoPath)[1]
		if not os.path.exists(self._screenshotPath):
			os.makedirs(self._screenshotPath)
		self._deleteFolderPngs(self._screenshotPath)	# empty out any PNGs possibly left from previous rendering
		self._isRecording = True

	def stopRecording(self):
		"""
		Private method. Stops recording and, if FFmpeg is available, will call L{_renderVideo}. If there is already a movie file with the same name as the one given in L{startRecording}, that movie file will be deleted. This method is called automatically by the L{Director}.
		"""
		if not self._isRecording:
			return
		command = self._makeFFMpegCommand()
		oldPath = self._screenshotPath
		oldName = self._screenshotName
		self._screenshotPath = ""
		self._screenshotFile = ""
		self._isRecording = False
		if self._canRecord is True:
			self._director.pause()
			path = oldPath + oldName[:-4]	# take off '.png' from screenshotName
			try:
				if os.path.isfile(path):	# if there is already a movie file
					os.unlink(path)				# then delete it
			except Exception, e:
				pass
			self._director.getRunningScene().addChild(self._renderNode, 100000)
			commandArgs = shlex.split(command)
			t = Thread(target=self._renderVideo, args=[commandArgs,oldPath])	# threaded to ensure that the PyGTK thread is not blocked (otherwise, the renderNode will not be displayed)
			t.start()

	def _renderVideo(self, *args):
		"""
		Private method. Renders the sequence of PNG images to a video file using FFmpeg. It will also delete the temporary PNG files and resume the L{Director}.
		
		This will be called automatically by L{stopRecording}.
		"""
		commandArgs = args[0]
		oldPath = args[1]
		s = subprocess.Popen(commandArgs, \
				stderr=subprocess.STDOUT, stdout=subprocess.PIPE).communicate()[0]	# blocks until completion
		self._director.getRunningScene().removeChild(self._renderNode)
		self._deleteFolderPngs(oldPath)
		self._director.resume()

	def takeScreenshot(self, screenshotPath):
		"""
		Private method. Takes a screenshot of the next expose event and saves it to the specified file. This method will be called automatically by the L{Director}. Note that PyGTK widgets will not appear in the screenshot as it will only render the gtk.Layout.

		@param screenshotPath: The path for the file to be saved.
		@type screenshotPath: C{string}
		"""
		screenshotPath = screenshotPath.strip()
		if screenshotPath.endswith(".png") is not True:
			screenshotPath += ".png"
		separator = os.sep
		self._screenshotPath = os.path.split(screenshotPath)[0]
		if self._screenshotPath is "":
			self._screenshotPath = "."
		self._screenshotPath = self._screenshotPath + separator
		self._screenshotName = os.path.split(screenshotPath)[1]
		if not os.path.exists(self._screenshotPath):
			os.makedirs(self._screenshotPath)

	def setFramerate(self, framerate):
		self._framerate = framerate

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

		if self._framerate is not None:
			context.move_to(0, self._size.height-10)
			context.set_font_size(14)
			context.set_source_rgb(1,1,1)
			context.show_text(self._framerate)
			self._framerate = None

		# Done with the new context state, so pop it.
		context.restore()

		if self._screenshotPath is not "":
			if self._isRecording is True:
				path = self._screenshotPath + str(self._exposeCounter) + "_" + self._screenshotName
			else:
				path = self._screenshotPath + self._screenshotName
			path = os.path.normpath(path)
			surface = context.get_group_target()
			surface.write_to_png(path)
			if self._isRecording is not True:
				self._screenshotPath = ""

		self._exposeCounter += 1


# TODO: this class will likely have to change to appropriately accommodate both Sugar activities and normal windowed applications.
class GTKInterface(object):
	"""
	Provides an interface between cocosCairo and PyGTK.
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
