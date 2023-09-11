from tkinter import *
from main import scan

class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

    def createWidgets(self):
        self.helloLabel = Label(self, text='Hello, your personal files size is')
        self.helloLabel.pack()
        self.infoLabel = Label(self, text=scan())
        self.infoLabel.pack()
        self.quitButton = Button(self, text='Quit', command=self.quit)
        self.quitButton.pack()

app = Application()
app.master.title('Personal Files Reporter')
app.mainloop()