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


class gdbHandler():
    lineHistorys = []
    globalHistory = dict()

    #BUG when adding variables in a block they are incorrectly saved into history
    #TODO: get the given variables from a function call
    #TODO BUG: values are sometimes initialized with 0 so setting them to zero doesn't trigger a watchpoint
    #TODO: add increment/decrement to variable finder (prefix and postfix) [https://en.wikipedia.org/wiki/Operators_in_C_and_C%2B%2B]


    def __init__(self, fName, cName):
        print("### initialising gdbHandler ###")
        self.fileName = fName
        self.cName = cName
        self.frameAmount = 0
        gdb.execute("file " + self.fileName)
        gdb.execute("set pagination off")



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
        self.frameAmount = self.getFrameAmount()
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
        return gdb.parse_and_eval(varName)



if __name__ == "__main__":
    gdbHandler = gdbHandler("a.out", "hello.c")
    gdb.execute("b 11")
    gdb.execute("run")

    try:
        gdbHandler.startAnalysis()
    except:
        print("### end of program ###")


    print("### printing history ###")
    with open("history.json", "w") as f:
        for line in gdbHandler.globalHistory:
            f.write(json.dumps(gdbHandler.globalHistory[line].getObject()) + "\n")
    for line in gdbHandler.globalHistory:
        print(gdbHandler.globalHistory[line])

    gdb.execute("quit")

