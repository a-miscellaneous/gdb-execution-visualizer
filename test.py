import gdb

class gdbHandler():


    def __init__(self, fName, cName):


        print("### initialising gdbHandler ###")
        self.fileName = fName
        self.cName = cName
        self.setup()


    def setup(self):
        gdb.execute("file " + self.fileName)
        gdb.execute("set pagination off")
        #gdb.execute("starti") # very begginnig of the program
        #gdb.execute("break main") # at main loop

    def setBreakPoint(self, place):
        #if int build a line break statement else just simple break
        exe = self.cName + ":" + str(place) if type(place) is int else place
        gdb.execute("break " + exe)


    def showLocalVariables(self):
        print("### showLocalVariables ###")
        self.frame = gdb.selected_frame()
        self.block = self.frame.block()
        gdb.execute("info locals")
        #gdb.execute("info args")
        #gdb.execute("info variables")
        self.test()

    def test(self):
        print('### test ###')
        self.print_variables_in_current_line()

    def stepFin(self):
        gdb.execute("s")
        gdb.execute("fin")

    def print_variables_in_current_line(self):
        # Get the line table for the current frame
        #line_table = self.frame.find_sal().symtab.linetable


        # Get the line number for the current frame
        line = self.frame.find_sal().line
        print("line: ", line)
        # Iterate over all variables in the current function
        block = gdb.block_for_pc(self.frame.pc())
        for sym in block:
            if sym.is_variable and sym.line == line:

                var = gdb.parse_and_eval(sym.name)
                print(sym.name, '=', var)

    def run(self):
        gdb.execute("run")

    def quit(self):
        gdb.execute("quit")



if __name__ == "__main__":
    gdbHandler = gdbHandler("a.out", "hello.c")
    gdbHandler.setBreakPoint(8)
    gdbHandler.run()
    gdbHandler.showLocalVariables()
    gdbHandler.quit()

