from cocosCairo.cocosCairo import *	# Convenience module to import all cocosCairo modules

class MyScene(Scene):
	def setup(self):
		node0 = Node(MakeRect(170,150,10,10))
		node0.setBackgroundColor(Color(0,0,0,1.0))
		node0.setAnchorPoint(Point(0.5,0.5))
		self.addChild(node0, 20)

		self.node1 = Node(MakeRect(170,150,100,250))
		self.node1.setBackgroundColor(BlueColor())
		self.node1.setAnchorPoint(Point(0.0,0.5))
		self.node1.setScale(0.5)
		self.addChild(self.node1, 9)

		self.node3 = SVGSprite("images/system_block.svg", Point(0,100))
		self.node1.addChild(self.node3, 1)

		node4 = Node(MakeRect(100,150,175,150))
		node4.setBackgroundColor(Color(1.0, 0.0, 0.0, 0.5))
		self.node3.addChild(node4,1)

		node2 = Node(MakeRect(50, 75, 200, 100))
		node2.setBackgroundColor(GreenColor())
		self.addChild(node2, -1)

		node5 = SVGSprite("images/system_block.svg", Point(400,400))
		node5.setStylePropertyValueById("rect", "fill", "#FFFFFF")
		node5.setStylePropertyValueById("rect", "stroke", "#FF0000")
		#node5.setSize(Size(50, 200))
		self.addChild(node5)

		node1Action = RotateBy(2.0, math.pi*2)
		node1Action = EaseSineInOut(node1Action)
		node1Action = RepeatForever(Sequence(node1Action, node1Action.reverse()))
		self.node1.runAction(node1Action)

		action1 = MoveBy(1.5, Point(125, -125))
		action1 = EaseExponentialInOut(action1)
		action2 = FadeOut(0.75)
		action3 = JumpBy(1.5, Point(90, -200), -150, 2)
		action4 = ScaleBy(2.0, 4.0)
		action4 = EaseInOut(action4, 5.0)
		sequence = Sequence(action1, action2, action2.reverse(), action3, action3.reverse(), action1.reverse(), action4, action4.reverse())
		repeatForever = RepeatForever(sequence)
		node5.runAction(repeatForever)


# TODO: fix the whole GTKWindow thing, look into making Activity.
# TODO: test out on OLPC

if __name__ == "__main__":
	director = Director()
	director.setWindow()
	director.runWithScene(MyScene())
