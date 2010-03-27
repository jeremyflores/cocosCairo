from Node import *
from Geometry import *

import gtk
from xml.etree.ElementTree import ElementTree
import xml.etree.ElementTree

import os
try:
	import rsvg
	#WINDOWS=False
except ImportError:
	if os.name == 'nt':
		#some workarounds for windows
		from ctypes import *

		l=CDLL('librsvg-2-2.dll')
		g=CDLL('libgobject-2.0-0.dll')
		g.g_type_init()

		class rsvgHandle():
			"""
			Private wrapper class needed to render SVG files in Windows.
			"""
			class RsvgDimensionData(Structure):
				_fields_ = [("width", c_int),
							("height", c_int),
							("em",c_double),
							("ex",c_double)]

			class PycairoContext(Structure):
				_fields_ = [("PyObject_HEAD", c_byte * object.__basicsize__),
							("ctx", c_void_p),
							("base", c_void_p)]

			def __init__(self, file=None, data=None):
				error = ''
				if file is not None:
					self.handle = l.rsvg_handle_new_from_file(file, error)
				elif data is not None:
					self.handle = l.rsvg_handle_new_from_data(data, len(data), error)


			def get_dimension_data(self):
				svgDim = self.RsvgDimensionData()
				l.rsvg_handle_get_dimensions(self.handle,byref(svgDim))
				return (svgDim.width,svgDim.height)

			def render_cairo(self, ctx):
				ctx.save()
				z = self.PycairoContext.from_address(id(ctx))
				l.rsvg_handle_render_cairo(self.handle, z.ctx)
				ctx.restore()



		class rsvgClass():
			"""
			Private wrapper class needed to render SVG files in Windows.
			"""
			def Handle(self,file=None, data=None):
				return rsvgHandle(file, data)

		rsvg = rsvgClass()



class SVGSprite(Node):
	"""
	Renders SVG files to the screen. While L{Sprite} can render SVG files, it first renders the SVG file to a pixel buffer, which forces it to be scaled by interpolating the pixels. SVGSprite, on the other hand, does allow scaling without pixel interpolation.

	Note that if the SVG file is large, it is recommended to use L{Sprite} as SVGSprite might slow down the application.
	"""
	def __init__(self, svgName=None, position=None):
		"""
		Initialization method.

		@param svgName: The path of the SVG file.
		@type svgName: C{string}
		@param position: The position of the Node. Default is L{PointZero()}.
		@type position: L{Point} (or C{None})
		"""
		Node.__init__(self)
		if position is not None:
			self.setPosition(position)
		self._svg = None
		self._svgName = None
		self._root = None
		self._namespace = None
		if svgName is not None:
			self.setSVGName(svgName)

	def getSize(self):
		"""
		Returns the size of the SVG image as specified in the C{<svg>} attributes C{"width"} and C{"height"}.

		@return: The size of the SVG image.
		@rtype: L{Size}
		"""
		return Node.getSize(self)

	def setSize(self, size):
		if self._root is not None:
			self.setSVGAttribute("width", size.width)
			self.setSVGAttribute("height", size.height)
			Node.setSize(self, size)

	def getOpacity(self):
		"""
		Returns the opacity of the SVG. If the SVG tag does not have an opacity attribute (or if the SVG file has not yet been set), then it will return C{1.0}.

		@return: The opacity.
		@rtype: C{float}
		"""
		if self._root is not None:
			opacity = self.getSVGAttribute("opacity")
			if not opacity:
				return float(opacity)
			else:
				return 1.0
		else:
			return 1.0

	def setOpacity(self, opacity):
		"""
		Sets the opacity of the SVG. The value should be between C{0.0} and C{1.0}.

		@param opacity: The SVG's new opacity.
		@type opacity: C{float}
		"""
		self.setSVGAttribute("opacity", opacity)

#{ SVG methods.
	def getSVGName(self):
		"""
		Returns the file path of the SVG file (or C{None} if it is not defined).

		@return: The file path.
		@rtype: C{string} (or C{None})
		"""
		return self._svgName

	def setSVGName(self, svgName):
		"""
		Sets the file path of the SVG file to be rendered.

		@param svgName: The path of the SVG file.
		@type svgName: C{string}
		"""
		self._svgName = svgName
		tree = ElementTree()
		tree.parse(self._svgName)
		self._setupSVGParsingWithTree(tree)

	'''
	def setSVGString(self, string):
		"""
		Sets the text string of the SVG to be rendered.

		@param string: The string of the SVG.
		@type string: C{string}
		"""
		tree = ElementTree()
		tree = xml.etree.ElementTree.fromstring(string)
		#tree.fromstring(string)
		self._setupSVGParsingWithTree(tree)
	'''

	def _setupSVGParsingWithTree(self, tree):
		self._root = tree.getroot()
		self._namespace = self.getSVGAttribute("xmlns")
		width = int(self.getSVGAttribute("width"))	# set the size of the Node to the size of the SVG
		height = int(self.getSVGAttribute("height"))
		if width is not None and height is not None:
			self._size = Size(width, height)
		self._setSVGFromData()

	def getSVGAttribute(self, attribute):
		"""
		Returns the value of an attribute of the SVG (that is, the C{<svg>} tag). If the SVG file has not yet been defined or if the SVG does not have the attribute, it will return C{None}.

		@param attribute: The name of the attribute whose value will be returned.
		@type attribute: C{string} (or C{None})
		"""
		if self._root is not None:
			return self._root.get(attribute)
		else:
			return None

	def setSVGAttribute(self, attribute, value):
		"""
		Sets the value of an attribute of the SVG.

		@param attribute: The name of the attribute.
		@type attribute: C{string}
		@param value: The value for the attribute.
		@type value: C{string}
		@return: Whether or not the attribute's value was successfully set.
		@rtype: C{bool}
		"""
		if self._root is not None:
			if not isinstance(attribute, str):
				attribute = str(attribute)
			if not isinstance(value, str):
				value = str(value)
			self._root.set(attribute, value)
			self._setSVGFromData()
			return True
		return False

	def getChildElementById(self, elementId):
		"""
		Returns an C{xml.etree.ElementTree._ElementInterface} for a child of the C{<svg>} tag (or C{None} if the child does not exist or if the SVG file has not yet been defined).

		@param elementId: The id of the child.
		@type elementId: C{string}
		@return: The child.
		@rtype: C{xml.etree.ElementTree._ElementInterface} (or C{None})
		"""
		if self._root is not None:
			if not isinstance(elementId, str):
				elementId = str(elementId)
			allChildren = self._root.findall('.//*')
			for child in allChildren:
				if child.get("id") == elementId:
					return child
		return None

	def getAttributeById(self, elementId, attribute):
		"""
		Returns the attribute's value for a child (or C{None} if it does not exist or if the SVG file has not yet been defined).

		@param elementId: The id of the child.
		@type elementId: C{string}
		@return: The value of the attribute.
		@rtype: C{string} (or C{None})
		"""
		if not isinstance(attribute, str):
			attribute = str(attribute)
		child = self.getChildElementById(elementId)
		if child is not None:
			return child.get(attribute)
		return None

	def setAttributeById(self, elementId, attribute, value):
		"""
		Sets the attribute's value for a child.

		@param elementId: The id of the child.
		@type elementId: C{string}
		@param attribute: The attribute's name.
		@type attribute: C{string}
		@param value: The new value for the attribute.
		@type value: C{string}
		@return: Whether or not setting the new value succeeded.
		@rtype: C{bool}
		"""
		if not isinstance(attribute, str):
			attribute = str(attribute)
		if not isinstance(value, str):
			value = str(value)
		child = self.getChildElementById(elementId)
		if child is not None:
			child.set(attribute, value)
			self._setSVGFromData()
			return True
		return False

	def getStyleDictionaryById(self, elementId):
		"""
		Returns a Python dictionary of all style properties (the keys of the dictionary) and their corresponding values (the values of the dictionary) for a particular child. If the child does not exist or if the child does not have the "style" attribute, then this will return an empty dictionary.

		@param elementId: The id of the child.
		@type elementId: C{string}
		@return: The dictionary.
		@rtype: C{dict}
		"""
		child = self.getChildElementById(elementId)
		if child is not None:
			style = child.get("style")
			styleList = style.split(";")
			styleDict = {}
			for item in styleList:
				item = item.strip()
				if len(item) < 1:
					continue
				styleProperty = item.split(":")[0].strip()
				styleValue = item.split(":")[1].strip()
				styleDict[styleProperty] = styleValue
			return styleDict

	def setStyleDictionaryById(self, elementId, styleDictionary):
		"""
		Sets the style for a child from a dictionary whose keys are the attributes and the corresponding values are the attribute values.

		@param elementId: The id of the child.
		@type elementId: C{string}
		@param styleDictionary: The dictionary.
		@type styleDictionary: C{dict}
		@return: Whether or not setting the new style succeeded.
		@rtype: C{bool}
		"""
		child = self.getChildElementById(elementId)
		if child is not None:
			styleString = ""
			for styleProperty in styleDictionary.keys():
				styleValue = styleDictionary[styleProperty]
				styleString += styleProperty + ":" + styleValue + ";"
			child.set("style", styleString)
			self._setSVGFromData()
			return True
		return False

	def getStylePropertyValueById(self, elementId, styleProperty):
		"""
		Returns the value of a particular style property for a child. If the property is not found, it will return C{None}.

		@param elementId: The id of the child.
		@type elementId: C{string}
		@param styleProperty: The property's name.
		@type styleProperty: C{string}
		@return: The value for the property.
		@rtype: C{string} (or C{None})
		"""
		styleDict = self.getStyleDictionaryById(elementId)
		if styleDict != {}:
			styleProperty = str(styleProperty)
			if styleProperty in styleDict:
				return styleDict[styleProperty]
		return None

	def setStylePropertyValueById(self, elementId, styleProperty, styleValue):
		"""
		Sets the value of a particular style property for a child.

		@param elementId: The id of the child.
		@type elementId: C{string}
		@param styleProperty: The property's name.
		@type styleProperty: C{string}
		@param styleValue: The value for the property.
		@type styleValue: C{string} (or C{None})
		@return: Whether or not setting the value succeeded.
		@rtype: C{bool}
		"""
		styleDict = self.getStyleDictionaryById(elementId)
		if styleDict != {}:
			styleDict[styleProperty] = styleValue
			return self.setStyleDictionaryById(elementId, styleDict)
		return False
			

	def _setSVGFromData(self):
		"""
		Private method called whenever the SVG's XML is altered to update the display. This method should not usually need to be called manually.
		"""
		if self._root is not None:
			string = xml.etree.ElementTree.tostring(self._root)
			self._svg = rsvg.Handle(data=string)
#}

	def draw(self, context):
		if self._svg is not None:
			self._svg.render_cairo(context)
