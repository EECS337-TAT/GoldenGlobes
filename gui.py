from Tkinter import *

root = Tk()
frame = Frame(root)
frame.pack()

bottomframe = Frame(root)
bottomframe.pack( side = BOTTOM )

redbutton = Button(frame, text="Awards")
redbutton.pack( side = LEFT)

greenbutton = Button(frame, text="Nominees")
greenbutton.pack( side = LEFT )

bluebutton = Button(frame, text="Winners")
bluebutton.pack( side = LEFT )

root.mainloop()