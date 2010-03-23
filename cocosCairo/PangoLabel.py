import pango
import pangocairo

from Node import *
from Color import *

_STRETCH_DICT = { \
-4: pango.STRETCH_ULTRA_CONDENSED, \
-3: pango.STRETCH_EXTRA_CONDENSED, \
-2: pango.STRETCH_CONDENSED, \
-1: pango.STRETCH_SEMI_CONDENSED, \
0: pango.STRETCH_NORMAL, \
1: pango.STRETCH_SEMI_EXPANDED, \
2: pango.STRETCH_EXPANDED, \
3: pango.STRETCH_EXTRA_EXPANDED, \
4: pango.STRETCH_ULTRA_EXPANDED, \
}

_WRAP_DICT = { \
"word": pango.WRAP_WORD, \
"word-char": pango.WRAP_WORD_CHAR, \
"char": pango.WRAP_CHAR, \
}

_ALIGN_DICT = { \
"left": pango.ALIGN_LEFT, \
"center": pango.ALIGN_CENTER, \
"right": pango.ALIGN_RIGHT, \
}

# TODO: add alpha / opacity somehow (doesn't look like pango.Layout + context.show_layout can do it).

class PangoLabel(Node):
	"""
	A L{Node} used to render text to the screen.

	PangoLabel uses the Pango text-rendering library and provides an HTML-like markup language for in-line decoration (such as italics and underlining). See http://pygtk.org/docs/pygtk/pango-markup-language.html for the markup specification.
	"""
	def __init__(self, markupText="", point=None):
		"""
		Initialization method.

		@param markupText: The text to be displayed. Default is C{""}.
		@type markupText: C{string}
		@param point: The position for the Node.
		@type point: L{Point}
		"""
		if point is None:
			point = PointZero()
		Node.__init__(self)	# TODO: add rect to constructor
		self.setPosition(point)
		self._markupText = markupText
		self._accelMarker = None
		self._fontFamily = "serif"
		self._fontSize = 12
		self._isItalic = False
		self._isSmallCaps = False
		self._fontWeight = 0.375	# maps from [0, 1] to [100, 900]
		self._fontStretch = 0	# an integer in [-4, 4]. Used in conjunction with _STRETCH_DICT
		self._wrappingType = "none"
		self._width = -1
		self._indentation = 0
		self._spacing = 0
		self._isJustified = False
		self._alignment = "left"
		self._isSingleParagraph = False
		self._isDirty = True
		self._isAlwaysRedrawing = False

	def isAlwaysRedrawing(self):
		"""
		Whether or not this Node will be redrawn every loop. By default, this is C{False}. This should only be used to fix a Pango rendering bug when the Node is originally rendered at a small scale and then is scaled up.

		@return: Whether or not this Node will be redrawn every loop.
		@rtype: C{bool}.
		"""
		return self._isAlwaysRedrawing

	def setAlwaysRedrawing(self, isAlwaysRedrawing):
		"""
		@param isAlwaysRedrawing: Whether or not this Node should redraw every loop.
		@type isAlwaysRedrawing: C{bool}.
		"""
		self._isAlwaysRedrawing = isAlwaysRedrawing

	def setWidth(self, width):
		"""
		This value is ignored if C{wrappingType} is set to "none".
		"""
		if self._width != width:
			self._width = width
			self.dirty()	# self._size will be set when redrawn.

	def getMarkupText(self):
		"""
		Returns the marked-up text to be rendered.

		@return: The marked-up text.
		@rtype: C{string}
		"""
		return self._markupText

	def setMarkupText(self, markupText):
		"""
		Sets the marked-up text to be rendered.

		@param markupText: The marked-up text.
		@type markupText: C{string}
		"""
		if self._markupText != markupText:
			self._markupText = markupText
			self.dirty()

	def getAccelMarker(self):
		"""
		Returns the accel marker.

		@return: The accel marker.
		@rtype: C{string}
		"""
		return self._accelMarker

	def setAccelMarker(self, accelMarker):
		"""
		Sets the accel marker for the marked=up text. Set it to C{None} if an accelMarker should not be used. Default is C{None}.

		@param accelMarker: The accel marker.
		@type accelMarker: C{string}
		"""
		if self._accelMarker != accelMarker:
			self._accelMarker = accelMarker
			self.dirty()

	def getFontFamily(self):
		"""
		Returns the font family to be used in rendering the text.

		@return: The font family (either "serif", "monospace", "sans", or "normal").
		@rtype: C{string}
		"""
		return self._fontFamily

	def setFontFamily(self, fontFamily):
		"""
		Common (and possibly the only) values are "serif", "monospace", "sans", or "normal".

		Default is C{"serif"}.

		@param fontFamily: The font family.
		@type fontFamily: C{string}
		"""
		if self._fontFamily != fontFamily:
			self._fontFamily = fontFamily
			self.dirty()

	def getFontSize(self):
		"""
		Returns the font size for the text. Default is C{12}.

		@return: The font size.
		@rtype: C{float}
		"""
		return self._fontSize

	def setFontSize(self, fontSize):
		"""
		Sets the font size for the text. Default is C{12}.

		@param fontSize: The font size.
		@type fontSize: Non-negative C{float}
		"""
		if self._fontSize != fontSize:
			self._fontSize = fontSize
			self.dirty()

	def isItalic(self):
		"""
		Returns whether or not the text is rendered in italics. This is C{False} by default.

		@return: Whether or not the text is rendered in italics.
		@rtype: C{bool}
		"""
		return self._isItalic

	def setItalic(self, isItalic):
		"""
		Sets whether or not the text is rendered in italics. Default is C{False}.

		@param isItalic: Whether or not the text is rendered in italics.
		@type isItalic: C{bool}
		"""
		if self._isItalic != isItalic:
			self._isItalic = isItalic
			self.dirty()

	def isSmallCaps(self):
		"""
		Returns whether or not the text is rendered in small caps. Default is C{False}.

		@return: Whether or not hte text is rendered in small caps.
		@rtype: C{bool}
		"""
		return self._isSmallCaps

	def setSmallCaps(self, isSmallCaps):
		"""
		Sets whether or not the text is rendered in small caps. Doesn't currently work. Default is C{False}.

		@param isSmallCaps: Whether or not the text is rendered in small caps.
		@type isSmallCaps: C{bool}
		"""
		if self._isSmallCaps != isSmallCaps:
			self._isSmallCaps = isSmallCaps
			self.dirty()

	def getFontWeight(self):
		"""
		Returns the font weight. Default is C{0.375}.

		@return: The font weight between C{0.0} and C{1.0}.
		@rtype: C{float}
		"""
		return self._fontWeight

	def setFontWeight(self, fontWeight):
		"""
		Sets the font weight. Only works for bolding the text, e.g. for fontWeight >= 0.5. Default is C{0.375}.

		@param fontWeight: The font weight between C{0.0} and C{1.0}.
		@type fontWeight: C{float}
		"""
		if self._fontWeight != fontWeight:
			self._fontWeight = fontWeight
			self.dirty()

	def getFontStretch(self):
		"""
		Gets the amount by which the text will be stretched.

		@return: The stretch amount (between C{-4} and C{4} inclusively).
		@rtype: C{int}
		"""
		return self._fontStretch

	def setFontStretch(self, fontStretch):
		"""
		Sets the amount by which the text will be stretched. Doesn't currently work. Might work for a newer version of Pango? Default is C{0}.

		@param fontStretch: The amount to stretch (between C{-4} and C{4} inclusively).
		@type fontStretch: C{int}
		"""
		if self._fontStretch != fontStretch:
			self._fontStretch = fontStretch
			self.dirty()

	def getWrappingType(self):
		"""
		Returns how the text is wrapped. See L{setWrappingType} for more details.

		@return: The wrapping type.
		@rtype: C{string}
		"""
		return self._wrappingType

	def setWrappingType(self, wrappingType):
		"""
		This value is ignored if C{width} is negative.

		Set it to C{"none"} if there should not be any wrapping, C{"word"} if it should break only between words, C{"word-char"} if it should try to break at words first before falling back to breaking between individual characters, or C{"char"} if it should break between individual characters.

		By default, C{wrappingType} is C{"none"}.

		@param wrappingType: The wrapping type.
		@type wrappingType: C{string}
		"""
		if wrappingType not in _WRAP_DICT and wrappingType is not "none":	# 'type' check
			return
		if self._wrappingType != wrappingType:
			self._wrappingType = wrappingType
			self.dirty()

	def getIndentation(self):
		"""
		Returns the amount by which the text is indented. Default is C{0.0}.

		@return: Indentation amount.
		@rtype: C{float}
		"""
		return self._indentation

	def setIndentation(self, indentation):
		"""
		Sets the amount by which the text is indented. Default is C{0.0}.

		@param indentation: Indentation amount.
		@type indentation: C{float}
		"""
		if self._indentation != indentation:
			self._indentation = indentation
			self.dirty()

	def getSpacing(self):
		"""
		Returns the spacing between lines of text. Default is C{0.0}.

		@return: Spacing amount.
		@rtype: C{float}
		"""
		return self._spacing

	def setSpacing(self, spacing):
		"""
		Sets the spacing between lines of text. Default is C{0.0}.

		@param spacing: Spacing amount.
		@type spacing: C{float}
		"""
		if self._spacing != spacing:
			self._spacing = spacing
			self.dirty()

	def isJustified(self):
		"""
		Returns whether or not the text is justified. Default is C{False}.

		@return: Whether or not the text is justified.
		@rtype: C{bool}
		"""
		return self._isJustified

	def setJustified(self, isJustified):
		"""
		Sets whether or not the text is justified. Default is C{False}.

		@param isJustified: Whether or not the text is justified.
		@type isJustified: C{bool}
		"""
		if isJustified not in _ALIGN_DICT:
			return
		if self._isJustified != isJustified:
			self._isJustified = isJustified
			self.dirty()

	def getAlignment(self):
		"""
		Returns the alignment for the text. Default is C{"left"}. See L{setAlignment} for more details.

		@return: The alignment for the text.
		@rtype: C{string}
		"""
		return self._alignment

	def setAlignment(self, alignment):
		"""
		Sets the alignment for the text. Set it to C{"left"} for left-justified, C{"center"} for center-justified, or C{"right"} for right-justified. Default value is C{"left"}.

		@param alignment: The alignment for the text.
		@type alignment: C{string}
		"""
		if alignment not in _ALIGN_DICT:
			return
		if self._alignment != alignment:
			self._alignment = alignment
			self.dirty()

	def isSingleParagraph(self):
		"""
		Returns whether or not the text is rendered as a single paragraph. Default is C{False}.

		@return: Whether or not the text is rendered as a single paragraph.
		@rtype: C{bool}
		"""
		return self._isSingleParagraph

	def setSingleParagraph(self, isSingleParagraph):
		"""
		Sets whether or not the text should be treated as a single paragraph, that is, whether or not the renderer should ignores newline characters. Default is C{False}.

		@param isSingleParagraph: Whether or not the text is rendered as a single paragraph.
		@type isSingleParagraph: C{bool}
		"""
		if self._isSingleParagraph != isSingleParagraph:
			self._isSingleParagraph = isSingleParagraph
			self.dirty()

	def draw(self, context):
		# TODO: making the layout in the drawing method might slow down rendering / cause flickering. Maybe
		# TODO: move the layout setup to another method for 'offline' rendering.
		if self.isAlwaysRedrawing():
			self.dirty()

		if self._isDirty:
			pangoContext = pangocairo.CairoContext(context)
			self._layout = pangoContext.create_layout()
			if self._accelMarker is not None:
				self._layout.set_markup_with_accel(self._markupText, self._accelMarker)
			else:
				self._layout.set_markup(self._markupText)
			fontDescription = pango.FontDescription()
			fontDescription.set_size(self._fontSize * pango.SCALE)
			fontDescription.set_family(self._fontFamily)
			if self._isItalic:
				fontDescription.set_style(pango.STYLE_ITALIC)
			else:
				fontDescription.set_style(pango.STYLE_NORMAL)
			if self._isSmallCaps:
				fontDescription.set_variant(pango.VARIANT_SMALL_CAPS)
			else:
				fontDescription.set_variant(pango.VARIANT_NORMAL)
			fontDescription.set_weight(int(100 + self._fontWeight*800))
			fontDescription.set_stretch(_STRETCH_DICT[self._fontStretch])
			self._layout.set_font_description(fontDescription)
			if self._wrappingType is "none" or self._width < 0:
				self._layout.set_width(-1)
			elif self._wrappingType is not "none" and self._width >= 0:
				self._layout.set_width(self._width*pango.SCALE)
				self._layout.set_wrap(_WRAP_DICT[self._wrappingType])
			self._layout.set_indent(self._indentation * pango.SCALE)
			self._layout.set_spacing(self._spacing * pango.SCALE)
			self._layout.set_justify(self._isJustified)
			self._layout.set_alignment(_ALIGN_DICT[self._alignment])
			self._layout.set_single_paragraph_mode(self._isSingleParagraph)
			width = self._layout.get_pixel_size()[0]
			height = self._layout.get_pixel_size()[1]
			self.setSize(Size(width, height))
			self._isDirty = False

		context.show_layout(self._layout)


	def dirty(self):
		"""
		Notifies the drawing method that the layout has changed and needs to be redrawn. This method is automatically called whenever any parameters for C{PangoLabel} are changed, so it should not typically need to be called manually.
		"""
		self._isDirty = True
		

	'''
	def getRectOfCharacterFromIndex(self, index):
		if self._layout is not None:
			rectTuple = self._layout.index_to_pos(index)
			offset = self.getTransformOffset()
			x = rectTuple[0] / pango.SCALE + offset.x
			y = rectTuple[1] / pango.SCALE + offset.y
			w = rectTuple[2] / pango.SCALE
			h = rectTuple[3] / pango.SCALE
			return MakeRect(x, y, w, h)

	# Currently doesn't work, and there are other things that still need to be implemented.
	def getIndexOfCharacterFromPoint(self, point):
		if self._layout is not None:
			offset = self._getTransformOffset()
			return self._layout.xy_to_index(point.x - offset.x*pango.SCALE, point.y - offset.y*pango.SCALE)
	'''
