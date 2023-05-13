import gdb
import re
import json

regX = r"^(\s*)([a-zA-Z_][a-zA-Z0-9_]*)(\s*)(\+\=|\-\=|\*\=|\/\=|\%\=|\=)(\s*)([a-zA-Z0-9_]+|\-?[0-9]+(\.[0-9]+)?)"

class lineHistory():
    def __init__(self, line, var, value):
        self.line = line
        self.var = var
        self.values = [str(value)]

    def append(self, value):
        self.values.append(str(value))

    def __str__(self):
        return "line: {} var: {} values: {}".format(self.line, self.var, self.values)

    def getObject(self):
        return {"line": self.line, "var": self.var, "values": self.values}


class SaveValueWatchpoint(gdb.Breakpoint):
    def __init__(self, spec, callback):
        super().__init__(spec, gdb.BP_WATCHPOINT, gdb.WP_WRITE, internal=True)
        self.saved_value = None
        self.var_name = spec.split()[1]
        self.callback = callback

    def stop(self):
        new_value = gdb.selected_frame().read_var(self.var_name)
        if new_value != self.saved_value:
            self.saved_value = new_value
            self.callback(self.var_name, new_value, gdb.selected_frame().find_sal().line) # gdb stops on next line so wrong line
        return False



class gdbHandler():
    lineHistorys = []
    globalHistory = dict()

    #TODO: dynamic amount of variables per line
    #TODO: get the given variables from a function call
    #TODO: get function arguments
    #TODO BUG: values are sometimes initialized with 0 so setting them to zero doesn't trigger a watchpoint
    #TODO: add increment/decrement to variable finder (prefix and postfix) [https://en.wikipedia.org/wiki/Operators_in_C_and_C%2B%2B]


    def __init__(self, fName, cName):
        print("### initialising gdbHandler ###")
        self.fileName = fName
        self.cName = cName
        gdb.execute("file " + self.fileName)
        gdb.execute("set pagination off")
        gdb.execute("set can-use-hw-watchpoints 0")
        self.frameAmount = 0



    def setBreakPoint(self, place):
        print("### setting breakpoint ###")
        exe = self.cName + ":" + str(place) if type(place) is int else place
        gdb.Breakpoint(exe, gdb.BP_BREAKPOINT, temporary=True)
        #gdb.execute("break " + exe)

    def setWatchPoint(self, varName):
        gdb.Breakpoint(varName, gdb.BP_WATCHPOINT)
        # gdb.execute("commands\nsilent\nend")

    def setLoggingWatchpoint(self, varName):
        SaveValueWatchpoint(varName, self.watchpoint_callback)

    def watchpoint_callback(self, var_name, new_value, line):
        if self.globalHistory.get(line) is None:
            self.globalHistory[line] = lineHistory(line, var_name, new_value)
            return
        self.globalHistory[line].append(new_value)


    def updateLocals(self):
        self.frame = gdb.selected_frame()
        self.block = self.frame.block()
        self.line = self.frame.find_sal().line
        self.lineStr = gdb.execute("frame ", to_string=True ).split("\n")[1].split(" ",1)[1].strip()

    def findVarInLine(self):

        #build all vars in frame
        block = self.block
        while block:
            for sym in block: #if local scope
                if sym.is_variable and sym.line == self.line:
                    print("### found variable {} with gdb ###".format(sym.name))
                    return sym.name

            block = block.superblock

        #attempt regex match
        match = re.match(regX, self.lineStr)
        if match:
            res = match.group(2).strip()
            print("### found variable with regex: {} ###".format(res))
            return res

        print("### no variable found  ###")
        return None #if we are on something weird like a function head or not in scope

    def getFrameAmount(self):
        num_frames = 0
        frame = gdb.newest_frame()
        while frame is not None:
            num_frames += 1
            frame = frame.older()
        print("### frame amount: {} ###".format(num_frames))
        return num_frames

    def startAnalysis(self):
        self.frameAmount = self.getFrameAmount()
        self.analyzeLine()

    def getLocals(self):
        infoLocals = gdb.execute("info locals", to_string=True).split("\n")
        result = {}
        for i in infoLocals:
            iArray = i.split(" ")
            if len(iArray) > 1:
                result[iArray[0]] = iArray[-1]

        return result if len(result) > 0 else None


    def analyzeLine(self):
        currentFrame = gdb.selected_frame()
        currentLine = currentFrame.find_sal().line
        currentLocals = self.getLocals()


        gdb.execute("step")

        newFrame = gdb.selected_frame()
        if currentFrame != newFrame:

            # if returned from a function call: kill self
            if self.frameAmount > self.getFrameAmount():
                print('### returning ###')
                self.frameAmount = self.getFrameAmount()
                return

            # if entered a new function call, start recursion
            print('### entering new function ###')
            self.analyzeLine()

        # came back from recursion or just new line
        if currentFrame != gdb.selected_frame():
            print("current frames: {}".format(self.frames))
            print("current frame: {}".format(gdb.selected_frame().pc()))
            print("current line: {}".format(currentLine))
            print("current locals: {}".format(currentLocals))
            print('SOMETHING WENT VERY WRONG')
            return

        # find diferences from saved locals and save them
        newLocals = self.getLocals()
        if newLocals:
            oldSet = set(currentLocals.items())
            newSet = set(newLocals.items())
            diff = newSet - oldSet
            for i in diff:
                self.addToHistory(currentLine, i[0], i[1])

        # continue recurse
        self.analyzeLine()




    def addToHistory(self, line : int, var : str, value):
        self.lineHistorys.append(line)
        if self.globalHistory.get(line) is None:
            print("### creating new lineHistory ###")
            self.globalHistory[line] = lineHistory(line, var, value)
            return
        self.globalHistory[line].append( value )

    def getVarValue(self, varName):
        # could optimize to get the symbol and then get the value from the symbol (maybe faster)
        return gdb.parse_and_eval(varName)

    def run(self):
        print("### running program ###")
        gdb.execute("run")

    def quit(self):
        gdb.execute("quit")

    def continueExecution(self):
        gdb.execute("continue")

    def step(self):
            gdb.execute("step")

    def next(self):
        gdb.execute("next")


    def showBreakpoints(self):
        print("### active breakpoints ###")
        for bp in gdb.breakpoints():
            print(bp.expression, bp.temporary, bp.enabled, bp.location)


if __name__ == "__main__":
    gdbHandler = gdbHandler("a.out", "hello.c")
    gdbHandler.setBreakPoint(11)
    gdbHandler.run()
    # gdbHandler.analyzeLine()

    try:
        gdbHandler.startAnalysis()
    except:
        # print("### exception: {} ###".format(e))
        print("### end of program ###")


    print("### printing history ###")
    with open("history.json", "w") as f:
        for line in gdbHandler.globalHistory:
            f.write(json.dumps(gdbHandler.globalHistory[line].getObject()) + "\n")
    for line in gdbHandler.globalHistory:
        print(gdbHandler.globalHistory[line])

    gdbHandler.quit()

