from cocosCairo.cocosCairo import *

class WordCollectionModel(AbstractModel):
	def __init__(self):
		self._tiles = {}	# of the form [x,y] : tileChar


class WordCollectionNode(Node):
	def __init__(self, letterCallback):
		rect = MakeRect(250, 50, 500, 200)
		Node.__init__(self, rect)
		self._letterCallback = letterCallback
		self.setBackgroundColor(GreyColor())

class WordCollectionController(AbstractController):
	def __init__(self, letterCallback):
		AbstractController.__init__(self, WordCollectionNode(letterCallback), WordCollectionModel(letter))
