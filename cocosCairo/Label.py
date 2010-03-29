"""
A Node which renders text to the screen.
"""

from Node import *
import cairo

_SLANT_DICT = { \
"normal": cairo.FONT_SLANT_NORMAL, \
"italic": cairo.FONT_SLANT_ITALIC, \
"oblique": cairo.FONT_SLANT_OBLIQUE \
}

_WEIGHT_DICT = { \
"normal": cairo.FONT_WEIGHT_NORMAL, \
"bold": cairo.FONT_WEIGHT_BOLD \
}

class Label(Node):
	"""
	Renders text to the screen.
	"""
	def __init__(self, text="", position=None, color=None, isAnimated=False):
		"""
		Initialization method.

		@param text: The text to be displayed.
		@type text: C{string}
		@param position: The position of the Label on the screen.
		@type position: L{Point}
		@param color: The color of the text. Default is L{WhiteColor()}.
		@type color: L{Color} (or C{None})
		@param isAnimated: Whether or not the text will be animated. See L{Label.start}.
		@type isAnimated: C{bool}
		"""
		if position is None:
			position = PointZero()
		if color is None:
			color = WhiteColor()
		Node.__init__(self, MakeRect(position.x, position.y, 0, 0))
		self.setColor(color)
		self._text = text
		self._fontSize = 12.0
		self._fontFamily = "serif"
		self._isItalic = False
		self._isBold = False
		self._isAnimated = isAnimated
		if self._isAnimated:
			self._displayText = ""
		else:
			self._displayText = self._text

#{ Animation methods.
	def start(self, duration=0.05):
		"""
		Starts the text animation in which the characters are added one at a time to the screen.

		@param duration: How long until a new character is added.
		@type duration: Non-negative C{float}
		"""
		if self._isAnimated is True:
			self.scheduleCallback(self._updateDisplayText, duration)

	def stop(self):
		"""
		Stops the text animation which was begun by L{Label.start}.
		"""
		self.unscheduleCallback(self._updateDisplayText)
#}

	def _updateDisplayText(self, dt):
		newString = ""
		index = len(self._displayText)
		for char in self._text[index:]:
			newString += char
			if len(newString.strip()) < 1:
				continue
			else:
				break
		self._displayText += newString
		if self._displayText == self._text:
			self.stop()

	def getOpacity(self):
		return self._color.a

	def setOpacity(self, opacity):
		self._color.a = opacity

#{ Accessor methods.
	def getText(self):
		"""
		Returns the text to be rendered.

		@return: The text to be rendered.
		@rtype: C{string}
		"""
		return self._text

	def setText(self, text):
		"""
		Sets the text to be rendered.

		@param text: The text to be rendered.
		@type text: C{string}
		"""
		self._text = text
		if self._isAnimated is not True:
			self._displayText = self._text

	def getFontSize(self):
		"""
		Returns the text's current font size.

		@return: The font size.
		@rtype: C{float}
		"""
		return self._fontSize

	def setFontSize(self, fontSize):
		"""
		Sets the font size for the Label.

		@param fontSize: The font size.
		@type fontSize: Non-negative C{float}
		"""
		self._fontSize = fontSize

	def getFontFamily(self):
		"""
		Returns the font family for the Label. Default is "serif".

		@return: The font family.
		@rtype: C{string}
		"""
		return self._fontFamily

	def setFontFamily(self, fontFamily):
		"""
		Sets the font family for the Label.

		@param fontFamily: The font family used in rendering.
		@type fontFamily: C{string}
		"""
		self._fontFamily = fontFamily

	def isItalic(self):
		"""
		Returns whether or not the text will be italicized. Default is C{False}.

		@return: Whether or not the text will be italicized.
		@rtype: C{bool}
		"""
		return self._isItalic

	def setItalic(self, isItalic):
		"""
		Sets whether or not the text will be italicized. Note that rendering the text as italic may not currently work.

		@param isItalic: Whether or not the text will be italicized.
		@type isItalic: C{bool}
		"""
		self._isItalic = isItalic

	def isBold(self):
		"""
		Returns whether or not the text will be bolded. Default is C{False}.

		@return: Whether or not the text will be bolded.
		@rtype: C{bool}
		"""
		return self._isBold

	def setBold(self, isBold):
		"""
		Sets whether or not the text will be bolded.

		@param isBold: Whether or not the text will be bolded.
		@type isBold: C{bool}
		"""
		self._isBold = isBold
#}

	def draw(self, context):
		color = self.getColor()
		context.set_source_rgba(color.r, color.g, color.b, color.a)
		if self._isItalic:
			slantFlag = _SLANT_DICT["italic"]
		else:
			slantFlag = _SLANT_DICT["normal"]
		if self._isBold:
			boldFlag = _WEIGHT_DICT["bold"]
		else:
			boldFlag = _WEIGHT_DICT["normal"]
		context.select_font_face(self._fontFamily, slantFlag, boldFlag)
		context.set_font_size(self._fontSize)
		context.show_text(self._displayText)
