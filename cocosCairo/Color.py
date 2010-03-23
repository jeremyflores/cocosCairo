class Color:
	"""
	Defines an C{RGBA} (Red, Green, Blue, Alpha) color. A Color is considered a primitive, so its values may be accessed directly.
	"""
	def __init__(self, r, g, b, a=1.0):
		"""
		Initialization method.

		@param r: The red value.
		@type r: C{float} between C{0.0} (no red) and C{1.0} (full red)
		@param g: The green value.
		@type g: C{float} between C{0.0} (no green) and C{1.0} (full green)
		@param b: The blue value.
		@type b: C{float} between C{0.0} (no blue) and C{1.0} (full blue)
		@param a: The alpha (opacity) value.
		@type a: C{float} between C{0.0} (fully transparent) and C{1.0} (fully opaque)
		"""
		self.r = r	#: The red value.
		self.g = g	#: The green value.
		self.b = b	#: The blue value.
		self.a = a	#: The alpha value.

	def __str__(self):
		return "r:\t" + str(self.r) + "\ng:\t" + str(self.g) + "\nb:\t" + str(self.b) + "\na:\t" + str(self.a)

	def getValues(self):
		"""
		Returns a list of the colors of the form C{[r, g, b, a]}, where r, g, b, and a are between C{0.0} and C{1.0}.

		@return: A list of the values.
		@rtype: C{list}
		"""
		return [self.r, self.g, self.b, self.a]

	def getIntValues(self):
		"""
		Returns a list of the colors of the form C{[r, g, b, a]}, where r, g, b, and a are integers between C{0} and C{255}.

		@return: A list of integer values.
		@rtype: C{list}
		"""
		return [int(x*255) for x in self.getValues()]

	def setIntValues(self, r, g, b, a=255):
		"""
		Sets the values of the color using integers between C{0} and C{255}.

		@param r: The red value.
		@type r: C{int}
		@param g: The green value.
		@type g: C{int}
		@param b: The blue value.
		@type b: C{int}
		@param a: The alpha (opacity) value.
		@type a: C{int}
		"""
		self.r = r/255.
		self.g = g/255.
		self.b = b/255.
		self.a = a/255.

	def getHexString(self):
		"""
		Returns a string of the form C{"#RRGGBB"} where C{RR}, C{GG}, and C{BB} are the red, green, and blue colors, respectively. Note that this ignores the alpha value of the color.

		@return: The hex string of the color.
		@rtype: C{string}
		"""
		colors = self.getIntValues()
		string = "#"
		for i in range(0,3):
			intValue = int(colors[i])
			hexValue = hex(int(colors[i]))[2:]
			if intValue < 16:
				hexValue = "0" + hexValue
			string += hexValue
		return string

	def setHexString(self, string):
		string = string.strip()
		if string[0] is "#":
			string = string[1:]
		r = int(string[0:2], 16)
		g = int(string[2:4], 16)
		b = int(string[4:6], 16)
		if len(string) > 6:
			a = int(string[6:8], 16)
		else:
			a = 255
		self.setIntValues(r, g, b, a)

	def copy(self):
		"""
		Returns a copy of the Color.

		@return: A copy of the Color.
		@rtype: L{Color}
		"""
		return Color(self.r, self.g, self.b, self.a)

def BlackColor():
	"""
	Returns a new L{Color} with C{RGBA} values C{(0, 0, 0, 1)}.

	@return: A new black Color.
	@rtype: L{Color}
	"""
	return Color(0,0,0,1)

def ClearColor():
	"""
	Returns a new L{Color} with C{RGBA} values C{(0, 0, 0, 0)}.

	@return: A new clear Color.
	@rtype: L{Color}
	"""
	return Color(0,0,0,0)

def WhiteColor():
	"""
	Returns a new L{Color} with C{RGBA} values C{(1, 1, 1, 1)}.

	@return: A new white Color.
	@rtype: L{Color}
	"""
	return Color(1,1,1,1)

def RedColor():
	"""
	Returns a new L{Color} with C{RGBA} values C{(1, 0, 0, 1)}.

	@return: A new red Color.
	@rtype: L{Color}
	"""
	return Color(1,0,0,1)

def GreenColor():
	"""
	Returns a new L{Color} with C{RGBA} values C{(0, 1, 0, 1)}.

	@return: A new green Color.
	@rtype: L{Color}
	"""
	return Color(0,1,0,1)

def BlueColor():
	"""
	Returns a new L{Color} with C{RGBA} values C{(0, 0, 1, 1)}.

	@return: A new blue Color.
	@rtype: L{Color}
	"""
	return Color(0,0,1,1)

def YellowColor():
	"""
	Returns a new L{Color} with C{RGBA} values C{(1, 1, 0, 1)}.

	@return: A new yellow Color.
	@rtype: L{Color}
	"""
	return Color(1,1,0,1)

def CyanColor():
	"""
	Returns a new L{Color} with C{RGBA} values C{(0, 1, 1, 1)}.

	@return: A new cyan Color.
	@rtype: L{Color}
	"""
	return Color(0,1,1,1)

def LightGrayColor():
	"""
	Returns a new L{Color} with C{RGBA} values C{(0.75, 0.75, 0.75, 1)}.

	@return: A new light gray Color.
	@rtype: L{Color}
	"""
	return Color(0.75, 0.75, 0.75, 1)

def LightGreyColor():
	return LightGrayColor()

def GrayColor():
	"""
	Returns a new L{Color} with C{RGBA} values C{(0.5, 0.5, 0.5, 1)}.

	@return: A new gray Color.
	@rtype: L{Color}
	"""
	return Color(0.5, 0.5, 0.5, 1.0)

def GreyColor():
	return GrayColor()
