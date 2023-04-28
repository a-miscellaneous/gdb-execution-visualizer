import gdb

class gdbHandler():


    def __init__(self, fName, cName):
        self.breaks = []

        print("### initialising gdbHandler ###")
        self.fileName = fName
        self.cName = cName
        self.setup()


    def setup(self):
        gdb.execute("file " + self.fileName)
        gdb.execute("set pagination off")
        #gdb.execute("starti")
        #gdb.execute("break main")

    def setBreakPoint(self, place):
        if type(place) is int:
            exe = self.cName + ":" + str(place)
            print(exe)
            gdb.execute("break " + exe)
            return

        if type(place) is str:
            exe = place
            print(exe)
            gdb.execute("break " + exe)
            return

        #self.breaks.append(gdb.Breakpoint(exe))




    def showLocalVariables(self):
        print("### showLocalVariables ###")
        self.frame = gdb.selected_frame()
        self.block = self.frame.block()
        gdb.execute("info locals")

    def run(self):
        gdb.execute("run")

    def quit(self):
        gdb.execute("quit")



if __name__ == "__main__":
    print("### main ###")
    gdbHandler = gdbHandler("a.out", "hello.c")
    gdbHandler.setBreakPoint(7)
    gdbHandler.run()
    gdbHandler.showLocalVariables()
    gdbHandler.quit()







#gdb.execute("info variables")
#gdb.execute("info locals")
#gdb.execute("info args")










