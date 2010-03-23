import gtk

class CustomDraw(gtk.Layout):
	def __init__(self):
		gtk.Layout.__init__(self)
		self.set_size_request(100,100)
		self.connect("expose-event", self.onExpose)

	def onExpose(self, widget, event):
		context = widget.bin_window.cairo_create()
		context.set_source_rgba(0.0, 1.0, 0.0, 1.0)
		context.rectangle(0, 0, 50, 50)
		context.fill()

class CompositeDemo(gtk.Window):

	def destroy(self, widget):
		gtk.main_quit()	

	def __init__(self):	
		gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
		self.set_title("Composite Example")
		self.set_size_request(800, 600)
		self.connect("destroy", self.destroy)

		layout = gtk.Layout()
		self.add(layout)

		image1 = gtk.Image()
		image1.set_from_file("background.jpg")
		layout.put(image1, 0, 0)

		widget = CustomDraw()
		layout.put(widget, 400, 300)
	
		self.show_all()


def main():
	gtk.main()
	
if __name__ == "__main__":
	demo = CompositeDemo()
	main()
