from __future__ import print_function
import pprint
import javalang
import os
import sys
from deepdiff import DeepDiff
classDefs = {}

# insert scaffolding here

def main():
    mainLabDir = "<REPLACE WITH LAB DIRECTORY>"
    for aLab in os.listdir(mainLabDir):
        fileLog = mainLabDir + "/" + aLab + "/__AUTOMARKER.txt"
        global fileLogHandle
        fileLogHandle = open(fileLog, "w")
        log("Now marking " + aLab + "...")
        parsedClasses = {}
        markLab(mainLabDir + "/" + aLab)
        fileLogHandle.flush()
        fileLogHandle.close()


def log(text):
    print(text)
    fileLogHandle.write(text)
    fileLogHandle.write("\n")


fileLogHandle = None


class JavaClass:
    def __init__(self):
        self.methods = []
        self.fields = []
        self.name = ""
        self.exists = True
        self.shouldBeCalled = ""
        self.matched = False
        self.lineNumber = (0, 0)

    def getFileName(self):
        return self.name + ".java"

    def getName(self):
        if (len(self.shouldBeCalled) != 0):
            return self.shouldBeCalled
        else:
            return self.name


class JavaMethod:
    def __init__(self):
        self.name = ""
        self.params = []
        self.returnType = ""
        self.exists = True
        self.shouldBeCalled = ""
        self.correctReturnType = ""
        self.correctParams = []
        self.accessibilityLevel = ""
        self.correctAccessibilityLevel = ""
        self.matched = False
        self.lineNumber = (0, 0)

    def getCorrectSig(self):
        return (self.getName() + "(" + (','.join([str(i) for i in self.correctParams])) + ")").replace("[", "").replace("]", "").replace("'", "")

    def getName(self):
        if (len(self.shouldBeCalled) != 0):
            return self.shouldBeCalled
        else:
            return self.name

    def getSig(self):
        return (self.name + "(" + (','.join([str(i) for i in self.params])) + ")").replace("[", "").replace("]", "").replace("'", "")

    def getVerboseSig(self):
        return self.accessibilityLevel + " " + self.returnType + " " + self.getSig()

    def getVerboseCorrectSig(self):
        return self.correctAccessibilityLevel + " " + self.correctReturnType + " " + self.getCorrectSig()


class JavaField:
    def __init__(self):
        self.name = ""
        self.type = ""
        self.accessibilityLevel = ""
        self.correctAccessibilityLevel = ""
        self.correctType = ""
        self.exists = True
        self.shouldBeCalled = ""
        self.matched = False
        self.lineNumber = (0, 0)

    def getName(self):
        if (len(self.shouldBeCalled) != 0):
            return self.shouldBeCalled
        else:
            return self.name


class multifile(object):
    def __init__(self, files):
        self._files = files

    def __getattr__(self, attr, *args):
        return self._wrap(attr, *args)

    def _wrap(self, attr, *args):
        def g(*a, **kw):
            for f in self._files:
                res = getattr(f, attr, *args)(*a, **kw)
            return res
        return g


def matchFiles(potentiallyExtra, potentiallyMissing, studentClasses, trueClasses):
    for aFile in potentiallyExtra:
        chosenItem = chooseItemFromList(potentiallyMissing, aFile)
        # user chose the "I don't know which file this matched to" option
        if (chosenItem > len(potentiallyMissing)-1):
            log("Unable to match class " + aFile.getName())
            aFile.exists = False
        else:
            # convert list offset into object
            chosenItem = potentiallyMissing[chosenItem]
            for aClass in studentClasses:
                if (aClass.name == aFile.name):
                    aClass.shouldBeCalled = chosenItem.name
                    chosenItem.matched = True
                    aClass.matched = True
                    break


def matchMethods(studentClass, aStudentField, trueClasses):
    trueClassFields = []
    flag = False
    for aClass in trueClasses:
        if (aClass.getName() == studentClass.getName()) and not flag:
            trueClassFields = aClass.methods
            flag = True

    # try to be smart and select a method if an identical one already exists:
    counter = 1
    autoFind = False
    if not autoFind:
        chosenItem = chooseMethodFromList(trueClassFields, aStudentField)
    # user chose the "I don't know which file this matched to" option
    if (chosenItem > len(trueClassFields)-1):
        log("Unable to match " + str(aStudentField))
        aStudentField.exists = False
    else:
        # convert list offset into object
        chosenItem = trueClassFields[chosenItem]
        aStudentField.shouldBeCalled = chosenItem.name
        aStudentField.correctAccessibilityLevel = chosenItem.accessibilityLevel
        aStudentField.correctReturnType = chosenItem.returnType
        aStudentField.correctParams = chosenItem.params
        aStudentField.matched = True
        chosenItem.matched = True
        aStudentField.exists = True
        chosenItem.exists = True
        aStudentField.matched = True
        return


def matchFields(studentClass, aStudentField, trueClasses):
    trueClassFields = []
    flag = False
    for aClass in trueClasses:
        if (aClass.getName() == studentClass.getName()) and not flag:
            trueClassFields = aClass.fields
            flag = True

    chosenItem = 0
    i = 0
    autoMatch = False
    for aField in trueClassFields:
        if (aStudentField.getName() == aField.getName()):
            chosenItem = i
            autoMatch = True
            break
        else:
            i = i + 1

    if not autoMatch:
        chosenItem = chooseItemFromList(trueClassFields, aStudentField)
    # user chose the "I don't know which file this matched to" option
    if (chosenItem > len(trueClassFields)-1):
        log("Unable to match " + str(aStudentField))
        aStudentField.exists = False
    else:
        # convert list offset into object
        chosenItem = trueClassFields[chosenItem]
        aStudentField.shouldBeCalled = chosenItem.name
        aStudentField.correctType = chosenItem.type
        aStudentField.correctAccessibilityLevel = chosenItem.accessibilityLevel
        aStudentField.matched = True
        chosenItem.matched = True
        return


def markLab(labDir):
    trueClasses = []
    studentClasses = []
    files = [f for f in os.listdir(labDir)]
    # asks the user to match files up to classes who have a slightly
    # different name

    # STEP ZERO: find and match files
    for aFile in classDefs.keys():
        trueClass = JavaClass()
        trueClass.name = aFile
        trueClasses.append(trueClass)

    # add .java extension to labFiles
    for aFile in os.listdir(labDir):
        if (aFile.endswith(".java")):
            studentClass = JavaClass()
            studentClass.name = aFile.replace(".java", "")
            studentClasses.append(studentClass)

    ######## MATCH UP CLASSES ##################
    potentiallyMissing = []
    for aClass in trueClasses:
        # try to find the true class name in the student classes
        # if we can't find it, it MIGHT be missing...
        if (next((x for x in studentClasses if x.name == aClass.name), None)) is None:
            potentiallyMissing.append(aClass)

    potentiallyExtra = []
    for aClass in studentClasses:
        # try to find the student class in the true classes
        # if we can't find it, it might be an extra class we don't need
        if (next((x for x in trueClasses if x.name == aClass.name), None)) is None:
            potentiallyExtra.append(aClass)

    if len(potentiallyExtra) != 0:
        # there might be some files to match up
        matchFiles(potentiallyExtra, potentiallyMissing,
                   studentClasses, trueClasses)

    ########## END MATCH UP CLASSES #################

    # STEP ONE: try to compile Java files and ensure compliance with specs
    log("Step one: compiling Java files:")
    compilationMsgs = []
    complianceOutput = []

    for aClass in studentClasses:
        if compileJava(labDir, aClass.getFileName()):
            log("Compilation of " + aClass.getName() + " succeeded.")
        else:
            log("Compilation of " + aClass.getName() + " failed.")

    # STEP TWO: compliance to lab specs:
    log("\n\nStep two: compliance to lab specs:")

    bindClassFiles(labDir, trueClasses, studentClasses)

    ######## MATCH UP FIELDS ##################
    for aClass in studentClasses:
        for aClassField in aClass.fields:
            # check all of them
            matchFields(aClass, aClassField, trueClasses)

    ########## END MATCH UP FIELDS #################

    # generate getters and setters from field names
    for aClass in studentClasses:
        trueClass = "overwrite me"
        newMethods = []

        for aClassField in aClass.fields:
            getterMethod = JavaMethod()

            def upperfirst(x):
                return x[0].upper() + x[1:]
            getterMethod.name = "get" + upperfirst(aClassField.name)

            getterMethod.returnType = aClassField.type

            # get the correct getter return type
            for bClass in trueClasses:
                for aField in bClass.fields:
                    if (aField.getName() == aClassField.getName()):
                        getterMethod.returnType = aField.type
                        getterMethod.correctReturnType = aField.type
                        getterMethod.correctAccessibilityLevel = "public"
                        getterMethod.accessibilityLevel = "public"
                        getterMethod.correctParams = []

            setterMethod = JavaMethod()
            setterMethod.name = "set" + upperfirst(aClassField.name)
            setterMethod.returnType = "void"
            setterMethod.correctReturnType = "void"
            # set correct input var type
            setterMethod.params = [getterMethod.returnType]
            setterMethod.correctParams = [getterMethod.correctReturnType]
            setterMethod.correctAccessibilityLevel = "public"
            setterMethod.accessibilityLevel = "public"
            newMethods.append(getterMethod)
            newMethods.append(setterMethod)

        for bClass in trueClasses:
            if (bClass.getName() == aClass.getName()):
                bClass.methods.extend(newMethods)

    x = 0
    ######## MATCH UP METHODS FIRST DIR ##################
    for aClass in studentClasses:
        for aClassMethod in aClass.methods:
            # check all of them
            if (aClassMethod.name != "main"):
                matchMethods(aClass, aClassMethod, trueClasses)

    ########## END MATCH UP METHODS #################

    ######## MATCH UP METHODS SECOND DIR ##################
    for aClass in trueClasses:
        for aClassMethod in aClass.methods:
            # check all of them
            if (not aClassMethod.matched):
                matchMethods(aClass, aClassMethod, studentClasses)

    ########## END MATCH UP METHODS #################

    log("verifyCompliance(studentClasses)")
    verifyCompliance(studentClasses)

    log("verifyCompliance(trueClasses)")
    verifyCompliance(trueClasses)
    # STEP THREE: General Recommendations
    log("Step three: general recommendations:")

    for aClass in studentClasses:
        if (len(aClass.shouldBeCalled) != 0):
            log("The class " + aClass.name + " should be called " +
                aClass.shouldBeCalled + " instead.")

    # just the required filenames
    labFiles = classDefs.keys()

    # all of the filenames in lowercase
    labFilesLower = [x.lower() for x in labFiles]

    for f in files:
            # warning for .docx files
        if (f.endswith(".docx")):
            log("Note: a WordPad document should be used instead of a Microsoft Word file to help accelerate marking time.")
        elif (f.endswith(".class")):
            log("Note: don't submit .class files! They will be re-created when the Java classes are compiled.")
            classFound = True
        elif (f.endswith(".pdf")):
            log("Note: a WordPad document should be used instead of a PDF to help accelerate marking time.")
        elif not f.endswith(".java") and not f.endswith(".class") and not f.endswith(".txt"):
            log("Note: UNIDENTIFIED file " + f)
        else:
            pass

    # now, check for header comments
    for f in files:
        if (f.endswith(".java")):
            with open(labDir + "/" + f) as myfile:
                totalComments = 0
                totalLines = 0
                data = myfile.read().strip()
                if not (data.startswith("/*") or data.startswith("//")):
                    log("Note: missing header comment on " + f)
            for aLine in data.splitlines():
                if (aLine.strip().startswith("//") or aLine.strip().startswith("/*")):
                    totalComments = totalComments + 1
                totalLines = totalLines + 1
            if (totalComments < 3):
                log("Total comments for " + f + ": " + str(totalComments))
                log("Comment coverage for " + f + ": " +
                    str((float(totalComments)/totalLines)*100) + "%\n")


""" Checks whether a Java file meets the lab specifications in terms of required methods and fields"""


def verifyCompliance(studentClasses):
    for aClass in studentClasses:
        if (not aClass.matched) and (not aClass.exists):
            if (aClass.name != "main"):
                log("Class " + str(aClass.name) + " does not exist.")
        else:
            for aClassField in aClass.fields:
                if (not aClassField.exists) or (not aClassField.matched):
                    log("Field " + aClassField.getName() +
                        " does not exist in " + aClass.getFileName())
                    continue
                if (cvtStr(aClassField.correctAccessibilityLevel) != cvtStr(aClassField.accessibilityLevel)):
                    log("Field " + cvtStr(aClassField.name) + " should have accessibility level " + cvtStr(aClassField.correctAccessibilityLevel) +
                        ", but it was " + cvtStr(aClassField.accessibilityLevel) + "in " + aClass.getFileName() + ":" + str(aClassField.lineNumber[0]))
                if (aClassField.type != aClassField.correctType):
                    log("Field " + aClassField.name + " should have type " + aClassField.correctType + ", but it was " +
                        aClassField.accessibilityLevel + " in " + aClass.getFileName() + ":" + str(aClassField.lineNumber[0]))
            for aClassMethod in aClass.methods:
                if (not aClassMethod.exists):
                    log("Method " + aClassMethod.getSig() +
                        " or one of a similar functionality does not exist in " + aClass.getFileName())
                    continue
                if not aClassMethod.matched:
                    log("Method " + aClassMethod.getSig() + " could not be matched in " +
                        aClass.getFileName() + ":" + str(aClassMethod.lineNumber[0]))
                    continue

                # ASSUME that all methods should be public (a bit of a generalization but...)
                if (aClassMethod.correctAccessibilityLevel == ""):
                    aClassMethod.correctAccessibilityLevel = "public"

                if (aClassMethod.accessibilityLevel == ""):
                    aClassMethod.accessibilityLevel = "public"
                if (cvtStr(aClassMethod.correctAccessibilityLevel) != cvtStr(aClassMethod.accessibilityLevel)):
                    log("Method " + cvtStr(aClassMethod.name) + " should have accessibility level " + cvtStr(aClassMethod.correctAccessibilityLevel) +
                        ", but it was " + aClassMethod.accessibilityLevel + " in " + aClass.getFileName() + ":" + str(aClassMethod.lineNumber[0]))
                if (cvtStr(aClassMethod.correctReturnType) != cvtStr(aClassMethod.returnType)):
                    log("Method " + cvtStr(aClassMethod.name) + " should have return type " + cvtStr(aClassMethod.correctReturnType) +
                        ", but it was " + aClassMethod.returnType + " in " + aClass.getFileName() + ":" + str(aClassMethod.lineNumber[0]))

                if (aClassMethod.getVerboseCorrectSig() != aClassMethod.getVerboseSig()):
                    log("Method " + aClassMethod.getVerboseSig() + " should have method defintion " + cvtStr(
                        aClassMethod.getVerboseCorrectSig()) + " in " + aClass.getFileName() + ":" + str(aClassMethod.lineNumber[0]))


"""Converts a unicode set into a string"""


def cvtStr(inputData):
    return ''.join(inputData)


"""Finds class files, and compiles them into an OOP format to be compared and verified against"""


def bindClassFiles(labDir, trueClasses, studentClasses):

    def findTrueClassInstance(trueClasses, desiredName):
        for aClass in trueClasses:
            if aClass.getName() == desiredName:
                return aClass

    # add classDefs into trueClasses
    for aClass in classDefs.keys():
        trueClassInst = findTrueClassInstance(trueClasses, aClass)
        newFields = []
        newMethods = []
        # the file just has to exist, but doesn't have to contain anything in particular
        if (classDefs[aClass] is None):
            continue
        aClassArray = classDefs[aClass].splitlines()
        for aClassLine in aClassArray:
            # extra line breaks
            aClassLine = aClassLine.strip()
            # not a comment or a blank line, then it must have some instructions
            if not (not aClassLine.startswith("//") and not aClassLine.strip()):
                if (aClassLine.startswith("FIELD: ")):
                    field = JavaField()
                    # replace all <<<class>> instances with correct class name
                    aClassLine = aClassLine.replace("<<<class>>>", aClassLine)
                    # FIELD: <type> <var_name>
                    aClassLine = aClassLine.split(" ")
                    field.accessibilityLevel = ''.join(aClassLine[1])
                    field.correctAccessibilityLevel = field.accessibilityLevel
                    field.type = aClassLine[2]
                    field.correctType = field.type
                    field.name = aClassLine[3]

                    # add the field to the true classes
                    newFields.append(field)
                elif (aClassLine.startswith("METHOD: ")):
                    method = JavaMethod()
                    aClassLine = aClassLine.replace("<<<class>>>", aClass)
                    aClassLine = aClassLine.split(" ")
                    method.accessibilityLevel = aClassLine[1]
                    method.correctAccessibilityLevel = method.accessibilityLevel
                    method.returnType = aClassLine[2]
                    method.correctReturnType = method.returnType
                    methodNameAndSig = aClassLine[3].split("(")
                    method.name = methodNameAndSig[0]
                    # remove last char from parameters (e.g. String,double)) paranthesis
                    someParams = methodNameAndSig[1][:-1].split(",")
                    method.params.append(someParams)
                    method.correctParams.append(someParams)
                    newMethods.append(method)

        # add parsed fields to the true classes
        trueClassInst.fields = newFields
        trueClassInst.methods = newMethods

    for aClass in studentClasses:
        file = open(labDir + "/" + aClass.getFileName(), 'r')
        text = file.read()
        file.close()

        # TODO: this can throw a  javalang.parser.JavaSyntaxError syntax error and aborts the entire program!
        tree = javalang.parse.parse(text)

        trueClassInst = aClass
        studentFields = []
        studentMethods = []
        studentConstructors = []

        for kclass in tree.types:
            for m in kclass.fields:
                for n in m.declarators:
                    studentField = JavaField()
                    studentField.name = n.name
                    studentField.type = m.type.name
                    studentField.lineNumber = m.position
                    studentField.accessibilityLevel = ''.join(m.modifiers)
                    studentFields.append(studentField)

            for m in kclass.methods:
                studentMethod = JavaMethod()
                studentMethod.lineNumber = m.position
                try:
                    studentMethod.returnType = m.return_type.name
                    studentMethod.name = m.name
                    studentMethod.accessibilityLevel = ''.join(m.modifiers)
                except:
                    studentMethod.returnType = "void"
                    studentMethod.name = m.name
                    studentMethod.accessibilityLevel = ''.join(m.modifiers)
                studentParams = []
                for n in m.parameters:
                    studentParams.append(n.type.name)
                studentMethod.params = studentParams
                studentMethods.append(studentMethod)

            for m in kclass.constructors:
                studentConstructor = JavaMethod()
                studentConstructor.lineNumber = m.position
                try:
                    studentConstructor.returnType = m.return_type.name
                    studentConstructor.name = m.name
                    studentConstructor.accessibilityLevel = ''.join(
                        m.modifiers)
                except:
                    studentConstructor.returnType = "void"
                    studentConstructor.name = m.name
                    studentConstructor.accessibilityLevel = "public"
                for n in m.parameters:
                    studentConstructor.params.append(n.type.name)
                studentConstructors.append(studentConstructor)

        studentMethods.extend(studentConstructors)
        trueClassInst.fields = studentFields
        trueClassInst.methods = studentMethods


# compiles a Java file and checks for errors
def compileJava(labDir, filename):
    shouldShowOutput = True
    import os
    import subprocess
    didFailCompilation = False
    if (not filename.lower().endswith(".java")):
        # might be a class name
        filename = filename + ".java"

    proc = subprocess.Popen("cd \"" + labDir + "\"; javac " + filename,
                            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    if (out.strip() is not ""):
        if shouldShowOutput:
            log(out)
        didFailCompilation = True
    if (err.strip() is not ""):
        if shouldShowOutput:
            log(err)
        didFailCompilation = True

    return not didFailCompilation


# allows the user to select an item from a list, and returns
# index of the item from the list that the user has chosen.
def chooseItemFromList(aList, toMatch):
    counter = 1
    print("Choose from the following that matches " + str(toMatch.name) + ":")
    for aFile in aList:
        print(str(counter) + ". " + str(aFile.name))
        counter = counter + 1
    # get int from user
    chosenItem = input("Enter in the item number: ")

    return chosenItem - 1  # the index of the item in the list

# allows the user to select an item from a list, and returns
# index of the item from the list that the user has chosen.


def chooseMethodFromList(aList, toMatch):
    i = 0
    # try to be smart and guess the item so that I don't have to manually choose it
    for aFile in aList:
        if toMatch.getVerboseSig() == aFile.getVerboseSig():
            toMatch.correctReturnType = aFile.returnType
            toMatch.correctAccessibilityLevel = aFile.accessibilityLevel
            return i
        else:
            i = i + 1

    # try to do a fuzzy guess if the previous one failed
    i = 0
    for aFile in aList:
        if toMatch.getSig() == aFile.getSig():
            toMatch.correctReturnType = aFile.returnType
            toMatch.correctAccessibilityLevel = aFile.accessibilityLevel
            return i
        else:
            i = i + 1

    counter = 1
    print("Choose from the following that matches " + str(toMatch.getSig()) + ":")
    for aFile in aList:
        print(str(counter) + ". " + str(aFile.getSig()))
        counter = counter + 1
    # get int from user
    chosenItem = input("Enter in the item number: ")

    if (chosenItem > len(aList)-1):
        toMatch.exists = False
        toMatch.matched = False
    else:
        toMatch.correctReturnType = aList[chosenItem - 1].returnType
        toMatch.correctAccessibilityLevel = aList[chosenItem -
                                                  1].accessibilityLevel
    return chosenItem - 1  # the index of the item in the list


# replaces all <<<class>>> with the actual class name
def rewriteClassDef(classDef, classToChange):
    tmp = classDef[classToChange]
    print(type(tmp))
    classDef[classToChange] = tmp


main()
