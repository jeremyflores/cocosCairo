from ListenedObject import *
from AbstractListener import *

class ModelListener(AbstractListener):
	"""
	An L{AbstractListener} that receives notifications from an L{AbstractModel} that it has changed.
	"""
	def onModelChange(self, model):
		"""
		Called by the L{AbstractModel} whenever it has changed. Subclass this method to handle what to do when the model changes.

		@param model: The modified model.
		@type model: L{AbstractModel}
		"""
		pass

class AbstractModel(ListenedObject):
	"""
	The model in the model-view-controller design pattern. Information should be stored in here.
	"""
	def didChange(self):
		"""
		Notifies all registered L{ModelListener}s that the model has changed. All subclasses are responsible for calling this method whenever the model changes.
		"""
		for listener in self.getListeners():
			self.notifyListener(listener)

	def notifyListener(self, listener):
		"""
		Notifies a particular L{ModelListener} that the model has changed. The listener may, but does not have to be, registered for this model.

		@param listener: A listener that responds to C{onModelChange}.
		@type listener: L{ModelListener}
		"""
		listener.onModelChange(self)
