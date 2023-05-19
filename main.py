import gdb
import re
import json

regX = r"^(\s*)([a-zA-Z_][a-zA-Z0-9_]*)(\s*)(\+\=|\-\=|\*\=|\/\=|\%\=|\=)(\s*)([a-zA-Z0-9_]+|\-?[0-9]+(\.[0-9]+)?)"

ASSIGNMENT = 0
FUNCTION_ARGS = 1
saveTypes = {ASSIGNMENT : "assignment", FUNCTION_ARGS : "functionArgs"}


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
    history = []

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
        gdb.execute("set style enabled off") # remove colors

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

    def startAnalysis(self):
        self.frameAmount = self.getFrameAmount()
        line = gdb.selected_frame().find_sal().line
        file = gdb.selected_frame().find_sal().symtab.filename
        self.saveFunctionParams()
        self.analyzeLine()

    def getLocals(self):
        infoLocals = gdb.execute("info locals", to_string=True)
        if infoLocals == "No locals.\n": return None
        infoLocals = infoLocals.split("\n")
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
        currentFile = currentFrame.find_sal().symtab.filename


        gdb.execute("step")

        if currentVar is None:
            self.analyzeLine()
            return

        newFrame = gdb.selected_frame()
        if currentFrame != newFrame:

            # if returned from a function call: kill self
            if self.frameAmount > self.getFrameAmount():
                return

            # if entered a new function call: start recursion
            self.saveFunctionParams()
            self.analyzeLine()

        # came back from recursion or just steped on new line


        # find diferences between the two frames and save them
        self.addAssignmentHistory(currentLine, currentVar, currentFile)

        # continue recurse
        self.analyzeLine()


    def addAssignmentHistory(self, line : int, var : str, file : str):
        value = gdb.parse_and_eval(var)
        obj = {"line" : line, "value" : str(value), "file" : file, "type" : saveTypes[ASSIGNMENT]}
        self.history.append(obj)


        # self.globalHistory[line].append(value)

    def saveFunctionParams(self):
        line = gdb.selected_frame().find_sal().line
        file = gdb.selected_frame().find_sal().symtab.filename
        args = gdb.execute("info args", to_string=True)
        if args == "No arguments.\n": return
        args = args.strip().split("\n")
        print(args)
        dic = {}
        for arg in args:
            s = arg.split("=", 1)
            dic[s[0].strip()] = s[1].strip()

        obj = {"line" : line, "args" : dic, "file": file, "type" : saveTypes[FUNCTION_ARGS]}
        self.history.append(obj)






if __name__ == "__main__":
    gdbHandler = gdbHandler("a.out", "hello.c")
    gdb.execute("b main")
    gdb.execute("run")

    try:
        gdbHandler.startAnalysis()
    except gdb.error as e:
        print(e)
        print("### end of program ###")


    print("### printing history ###")
    with open("history.json", "w") as f:
        for line in gdbHandler.history:
            f.write(json.dumps(line) + "\n")
            print(line)


    gdb.execute("quit")

