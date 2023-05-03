import gdb

class gdbHandler():
    lineHistory = []
    globalHistory = dict()


    #TODO: find a way to delete BREAKpoints directly after they have been set SOLUTION: temporary=True?
    #TODO: get the given variables from a function call
    #TODO: does a variable get discovered even if it isn't assigned but just part of a function call?
    #TODO: values are sometimes initialized with 0 so setting them to zero doesn't trigger a watchpoint

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

    #might get simplified
    def setBreakPoint(self, place):
        print("### setting breakpoint ###")
        #if int build a line break statement else just simple break
        exe = self.cName + ":" + str(place) if type(place) is int else place
        gdb.Breakpoint(exe, gdb.BP_BREAKPOINT, temporary=True)
        gdb.execute("break " + exe)

    #to stop directly after a value is assigned
    def setWatchPoint(self, varName):
        print("### setting watchpoint ###")
        # TODO: test

        #gdb.execute("watch {}", varName)
        watchP = gdb.Breakpoint(varName, gdb.BP_WATCHPOINT, temporary=True)

        print('set Watchpoint  ' , watchP)

    #important if the current line doesnt have a var just step to next
    def step(self):
        gdb.execute("step")

    def addLineToHistory(self, line):
        self.lineHistory.append(line)

    #sets all the neccesary variables
    #does not update the current variable so access to the previous one is still possible
    def updateLocals(self):
        self.frame = gdb.selected_frame()
        self.block = self.frame.block()
        self.line = self.frame.find_sal().line

    def findVarInLine(self):
        print("### finding var in line ###")
        for sym in self.block:
            if sym.is_variable and sym.line == self.line:
                self.var = sym
                var = sym.name
                #var = gdb.parse_and_eval(sym.name)
                #print(sym.name, '=', var)
                return var
        return None #if we are on something weird like a function head


    def analyzeLine(self):
        self.updateLocals()
        self.findVarInLine()
        print('found variable: ' + self.var.name)
        self.setWatchPoint(self.var.name)
        self.continueExecution()
        value = self.getVarValue(self.var.name)
        print(self.var.name , '=' , value)
        self.deleteAllBreakpoints()


    def getVarValue(self, varName):
        print("### getting var value ###")
        res = gdb.parse_and_eval(varName)
        return res

    def run(self):
        print("### running program ###")
        gdb.execute("run")

    def quit(self):
        gdb.execute("quit")

    def continueExecution(self):
        gdb.execute("continue")

    def deleteAllBreakpoints(self):
        print("### getting current breakpoints ###")
        for bp in gdb.breakpoints():
            bp.delete()



if __name__ == "__main__":
    gdbHandler = gdbHandler("a.out", "hello.c")
    gdbHandler.setBreakPoint(9)
    gdbHandler.run()
    gdbHandler.analyzeLine()

    gdbHandler.quit()

