import turtle as t

mz = t.Screen()
mz.setup(800,600)
mz.bgcolor('white')
mz.title('Alice in Music Maze')
mz.register_shape('grass1.gif')

pen = t.Turtle()
pen.shape('grass1.gif')

mz.mainloop()