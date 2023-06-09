import gdb
import re
import json



class gdbHandler():


    def __init__(self, fName, cName):
        print("### initialising gdbHandler ###")
        self.fileName = fName
        self.cName = cName
        self.frameAmount = 0
        self.history = exeHistory()
        self.currentStep = 0
        gdb.execute("file " + self.fileName)
        gdb.execute("set pagination off")
        gdb.execute("set style enabled off") # remove colors

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
        if infoLocals == "No locals.\n":
            return None
        infoLocals = infoLocals.strip().split("\n")
        result = {}
        for i in infoLocals:
            iArray = i.split(" ", 2)
            if len(iArray) > 1:
                result[iArray[0]] = iArray[2]

        return result if len(result) > 0 else None

    def getArgs(self):
        args = gdb.execute("info args", to_string=True)
        if args == "No arguments.\n": return
        args = args.strip().split("\n")
        dic = {}
        for arg in args:
            s = arg.split("=", 1)
            dic[s[0].strip()] = s[1].strip()

        return dic if len(dic) > 0 else None

    def getVars(self):
        locs = self.getLocals()
        args = self.getArgs()

        if locs and args:
            args.update(locs)
            return args

        return locs if locs else args

    def analyzeLine(self):
        # save local frame with locals
        currentHeight = self.getFrameAmount()
        currentFrame = gdb.selected_frame()
        currentLine = currentFrame.find_sal().line
        currentLocals = self.getVars()
        currentFile = currentFrame.find_sal().symtab.filename
        currentLineStr = gdb.execute("frame ", to_string=True ).split("\n")[1].split("\t",1)[1].strip()
        currentStep = self.currentStep

        gdb.execute("step")
        self.currentStep += 1

        newFrame = gdb.selected_frame()
        if currentFrame != newFrame:

            # if returned from a function call: kill self
            if currentHeight > self.getFrameAmount():
                return
            # else
            # if entered a new function call: start recursion
            self.saveFunctionParams()
            self.analyzeLine()

        # came back from recursion or just steped on new line
        # find diferences and save them
        self.saveAssiggnmentHistory(currentLine, currentLocals, currentLineStr, currentHeight, currentStep)

        # continue recurse
        self.analyzeLine()

    def saveAssiggnmentHistory(self, line : int, oldlocals : dict, oldLineStr : str, stackHeight : int, currentStep : int):
        file = gdb.selected_frame().find_sal().symtab.filename
        oldLineStr = " "+oldLineStr # to exclude any " or '
        newLocals = self.getVars()
        if newLocals is None: return

        for key in newLocals:
            try:
                if oldlocals[key] != newLocals[key]: # found a difference, save it
                    obj = {"line" : line, "value" : newLocals[key], "var": key, "file" : file, "stackHeight" : stackHeight, "step" : currentStep}
                    self.history.append(obj)
                    return

            except: # means that a new var was added to the scope
                currentLine = gdb.selected_frame().find_sal().line
                obj = {"line" : currentLine, "value" : newLocals[key], "var": key, "file" : file, "stackHeight" : stackHeight, "step" : currentStep}

                # only accept the new var if it came from a for loop
                if self.findForLoop(key):
                    self.history.append(obj)
                    return

        # if no changes detected, attempt to find a var in the line and then save it
        assignmentRegX = r"([^\"\'])(\s*)([a-zA-Z_][a-zA-Z0-9_]*)(\s*)(\+\=|\-\=|\*\=|\/\=|\%\=|\=)(\s*)([a-zA-Z0-9_]+|\-?[0-9]+(\.[0-9]+)?)"
        match = re.search(assignmentRegX, oldLineStr)
        if match:
            res = match.group(3).strip()
            obj = {"line" : line, "value" : oldlocals[res], "var": res, "file" : file, "stackHeight" : stackHeight, "step" : currentStep}
            self.history.append(obj)

    def findForLoop(self, var):
        currentLineStr = gdb.execute("frame ", to_string=True ).split("\n")[1].split("\t",1)[1].strip()
        for_regex = r"^(\s*)(for)(\s*)(\()([a-zA-Z_][a-zA-Z0-9_]*)(\s*)(\+\=|\-\=|\*\=|\/\=|\%\=|\=)(\s*)"
        match = re.search(for_regex, currentLineStr)
        if not match or match.group(5) != var:
            return False
        return True

    def saveFunctionParams(self):
        line = gdb.selected_frame().function().line
        file = gdb.selected_frame().find_sal().symtab.filename
        functionName = gdb.selected_frame().name()
        dic = self.getArgs()
        if dic is None: return

        obj = {"line" : line, "value" : dic, "file": file, "stackHeight" : self.getFrameAmount(), "stackName" : functionName, "step" : self.currentStep}
        self.history.append(obj)


# sad dump cause only one file as source
class argsHistory():
    def __init__(self, stackName):
        self.stackName = stackName
        self.values = []

    def append(self, varObj, step, stackHeight):
        self.values.append({"dict": varObj, "stackHeight": stackHeight, "step": step})
        # step is the first step in this function so it is incorrect, used for finding nearest step with <= step

    def asSerial(self):
        return { "functionName": self.stackName, "values": self.values}


class lineHistory():
    values = []
    var = None

    def __init__(self, var):
        self.var = var
        self.values = []

    def append(self, value, step, stackHeight):
        self.values.append({"value": value, "step": step, "stackHeight": stackHeight})

    def asSerial(self):
        return { "var": self.var, "values": self.values}


class exeHistory():
    history = {}


    def append(self, obj):
        fileName = obj["file"]
        line = obj["line"]
        var = obj["var"] if "var" in obj else None
        value = obj["value"]
        step = obj["step"] if "step" in obj else None
        stackHeight = obj["stackHeight"]
        stackName = obj["stackName"] if "stackName" in obj else None

        if fileName not in self.history: # first time
            self.history[fileName] = {}

        if var is None: # args
            self.handleArgs(fileName, line, value, step, stackHeight, stackName)
        else: # line
            self.handleLines(fileName, line, var, value, step, stackHeight)

    def handleArgs(self, fileName, line, value, step, stackHeight, stackName):
        if line not in self.history[fileName]: # first time
            self.history[fileName][line] = argsHistory(stackName)

        self.history[fileName][line].append(value, step, stackHeight)

    def handleLines(self, fileName, line, var, value, step, stackHeight):
        if line not in self.history[fileName]: # first time
            self.history[fileName][line] = lineHistory(var)

        self.history[fileName][line].append(value, step, stackHeight)


    def asSerial(self):
        return self.history





def serializer(obj):
    if hasattr(obj, "asSerial"):
        return obj.asSerial()
    return obj.__dict__









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
        json.dump(gdbHandler.history, f, indent=4, default=serializer)


    gdb.execute("quit")





