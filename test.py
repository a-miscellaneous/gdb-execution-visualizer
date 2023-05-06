import gdb
import re

regX = r"^(\s*)([a-zA-Z_][a-zA-Z0-9_]*)(\s*)(\+\=|\-\=|\*\=|\/\=|\%\=|\=)(\s*)([a-zA-Z0-9_]+|\-?[0-9]+(\.[0-9]+)?)"

class lineHistory():
    def __init__(self, line, var, value):
        self.line = line
        self.var = var
        self.values = [value]

    def append(self, value):
        self.values.append(value)

    def __str__(self):
        return "line: {} var: {} values: {}".format(self.line, self.var, self.values)


class gdbHandler():
    lineHistorys = []
    globalHistory = dict()

    #TODO: dynamic amount of variables per line
    #TODO: get the given variables from a function call
    #TODO: does a variable get discovered even if it isn't assigned but just part of a function call?
    #TODO BUG: values are sometimes initialized with 0 so setting them to zero doesn't trigger a watchpoint
    #TODO: add increment/decrement to variable finder (prefix and postfix) [https://en.wikipedia.org/wiki/Operators_in_C_and_C%2B%2B]


    def __init__(self, fName, cName):
        print("### initialising gdbHandler ###")
        self.fileName = fName
        self.cName = cName
        self.setup()


    def setup(self):
        gdb.execute("file " + self.fileName)
        gdb.execute("set pagination off")

    def setBreakPoint(self, place):
        print("### setting breakpoint ###")
        exe = self.cName + ":" + str(place) if type(place) is int else place
        gdb.Breakpoint(exe, gdb.BP_BREAKPOINT, temporary=True)
        #gdb.execute("break " + exe)

    def setWatchPoint(self, varName):
        gdb.Breakpoint(varName, gdb.BP_WATCHPOINT, temporary=True)
        gdb.execute("commands\nsilent\nend")

    def updateLocals(self):
        self.frame = gdb.selected_frame()
        self.block = self.frame.block()
        self.line = self.frame.find_sal().line
        self.lineStr = gdb.execute("frame ", to_string=True ).split("\n")[1].split(" ",1)[1].strip()

    def findVarInLine(self):
        for sym in self.block: #if local scope
            if sym.is_variable and sym.line == self.line:
                print("### found variable {} ###".format(sym.name))
                self.var = sym
                return sym.name

        #attempt regex match
        match = re.match(regX, self.lineStr)
        if match:
            res = match.group(2).strip()
            print("### found variable with regex: {} ###".format(res))
            return res

        print("### no variable found  ###")
        return None #if we are on something weird like a function head or not in scope

    def analyzeLine(self):
        print("### analyzing line ###")
        self.updateLocals()
        foundVar = self.findVarInLine()
        if not foundVar:
            self.next()
            return

        self.setWatchPoint(self.var.name)
        self.continueExecution()
        value = self.getVarValue(self.var.name)
        self.addToHistory(int(self.line), self.var.name, value)

    def addToHistory(self, line, var, value):
        self.lineHistorys.append(line)
        if self.globalHistory.get(line) is None:
            self.globalHistory[line] = lineHistory(line, var, value)
            return
        self.globalHistory[line].append( str(value) )

    def getVarValue(self, varName):
        return gdb.parse_and_eval(varName)

    def run(self):
        print("### running program ###")
        gdb.execute("run")

    def quit(self):
        gdb.execute("quit")

    def continueExecution(self):
        print("### continuing execution ###")
        gdb.execute("continue")

    def step(self):
            gdb.execute("step")

    def next(self):
        gdb.execute("next")

    # def deleteAllBreakpoints(self):
        for bp in gdb.breakpoints():
            bp.delete()

    def showBreakpoints(self):
        print("### active breakpoints ###")
        for bp in gdb.breakpoints():
            print(bp.expression, bp.temporary, bp.enabled, bp.location)


if __name__ == "__main__":
    gdbHandler = gdbHandler("a.out", "hello.c")
    gdbHandler.setBreakPoint(7)
    gdbHandler.run()

    while True:
        try:
            gdbHandler.analyzeLine()
        except:
            print("### end of program ###")
            break

    print("### printing history ###")
    for line in gdbHandler.lineHistorys:
        print(gdbHandler.globalHistory[line])

    gdbHandler.quit()

