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
    initHistory = []

    #BUG when a variable is initialized in a new block it is incorrectly saved
    #TODO: save for loop variables
    #TODO: get the given variables from a function call
    #TODO: don't step outside of user files (aka dont save printf steps)



    def __init__(self, fName, cName):
        print("### initialising gdbHandler ###")
        self.fileName = fName
        self.cName = cName
        self.frameAmount = 0
        gdb.execute("file " + self.fileName)
        gdb.execute("set pagination off")

    def findVarInLine(self):

        #build all vars in frame
        block = gdb.selected_frame().block()
        line = gdb.selected_frame().find_sal().line
        while block:
            for sym in block: #if local scope
                if sym.is_variable and sym.line == line:
                    print("### found variable {} with gdb ###".format(sym.name))
                    return sym.name

            block = block.superblock

        lineStr = gdb.execute("frame ", to_string=True ).split("\n")[1].split("\t",1)[1].strip()

        #attempt regex match
        match = re.match(regX, lineStr)
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

    def saveInit(self):
        line = gdb.selected_frame().find_sal().line
        localVars = self.getLocals()
        self.initHistory.append({line: localVars})

    def startAnalysis(self):
        self.frameAmount = self.getFrameAmount()
        self.saveInit()
        self.analyzeLine()

    def getLocals(self):
        infoLocals = gdb.execute("info locals", to_string=True).split("\n")
        result = {}
        for i in infoLocals:
            iArray = i.split(" ", 2)
            if len(iArray) > 1:
                result[iArray[0]] = iArray[2]

        return result if len(result) > 0 else None


    def analyzeLine(self):
        # save local frame with locals
        self.frameAmount = self.getFrameAmount()
        currentFrame = gdb.selected_frame()
        currentLine = currentFrame.find_sal().line
        currentVar = self.findVarInLine()


        gdb.execute("step")

        newFrame = gdb.selected_frame()
        if currentFrame != newFrame:

            # if returned from a function call: kill self
            if self.frameAmount > self.getFrameAmount():
                return

            # if entered a new function call: start recursion
            self.saveInit()
            self.analyzeLine()

        # came back from recursion or just steped on new line
        if currentFrame != gdb.selected_frame():
            print('SOMETHING WENT VERY WRONG')
            return

        # find diferences from saved locals and save them
        newLocals = self.getLocals()
        if newLocals:
            for key, value in newLocals.items():
                if key == currentVar:
                    self.addToHistory(currentLine, key, value)


        # continue recurse
        self.analyzeLine()


    def addToHistory(self, line : int, var : str, value):
        self.lineHistorys.append(line)
        if self.globalHistory.get(line) is None:
            self.globalHistory[line] = lineHistory(line, var, value)
            return
        self.globalHistory[line].append( value )

    def getVarValue(self, varName):
        return gdb.parse_and_eval(varName)



if __name__ == "__main__":
    gdbHandler = gdbHandler("a.out", "hello.c")
    gdb.execute("b main")
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

