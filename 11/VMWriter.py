import json
from JackSyntax import SYNTAX

class VMWriter():
    def __init__(self, output):
        self.output = output
        self.fp = open(output, 'w')
        self.boolCount = 0
        self.currentClassName = ""
    
    def close(self):
        self.fp.close()
    
    def write(self, command):
        print("### FILE WRITE: {}".format(command))
        self.fp.write(command+'\n')
    
    def writePush(self, segment, index):
        self.write("push {} {}".format(segment, index))
    
    def writePop(self, segment, index):
        self.write("pop {} {}".format(segment, index))
    
    def writeArithmetic(self, command):
        self.write(command)
    
    def writeLabel(self, label):
        self.write("label {}".format(label))
    
    def writeGoto(self, label):
        self.write("goto {}".format(label))
    
    def writeIf(self, label):
        self.write("if-goto {}".format(label))
    
    def writeCall(self, name, nArgs):
        self.write("call {} {}".format(name, nArgs))
    
    def writeFunction(self, name, nLocals):
        self.write("function {} {}".format(name, nLocals))
    
    def writeReturn(self):
        self.write("return")
    
    def _getBody(self, obj, typ):
        if isinstance(obj, dict) and typ in obj:
            return obj[typ]
        if isinstance(obj, list) and len(obj) == 1 and typ in obj[0]:
            return obj[0][typ]
        return obj

    # class definitions
    def convertClass(self, classDec):
        classDec = self._getBody(classDec, "class")
        className = classDec[1]["identifier"]["name"]
        self.currentClassName = className
        nFields = classDec[1]["identifier"]["fieldCount"]
        print("START CONVERT CLASS")
        print(len(classDec))
        print(json.dumps(classDec, indent=2))
        for item in classDec:
            print("### Convert for {}".format(item))
            if "classVarDec" in item:
                self.convertVarDec(item)
            elif "subroutineDec" in item:
                self.convertSubroutineDec(item, className, nFields) 
        print("END CONVERT CLASS")

    def convertVarDec(self, varDec):
        varDec = self._getBody(varDec, "varDec")
        return
    
    def convertSubroutineDec(self, subroutineDec, className, nFields):
        subroutineDec = self._getBody(subroutineDec, "subroutineDec")
        print("$$$ subroutine dec $$$")
        print(subroutineDec)
        subroutineType = subroutineDec[0]["keyword"]
        if "keyword" in subroutineDec[1]:
            returnType = subroutineDec[1]["keyword"]
        else:
            returnType = subroutineDec[1]["identifier"]["name"]
        subroutineIdentifier = "{}.{}".format(className, subroutineDec[2]["identifier"]["name"])
        subroutineArgsNum = subroutineDec[2]["identifier"]["localCount"]
        subroutineBody = subroutineDec[6]
        self.writeFunction(subroutineIdentifier, subroutineArgsNum)
        if subroutineType == "method":
            self.writePush('argument', 0)
            self.writePop('pointer', 0)
        elif subroutineType == "constructor":
            self.writePush('constant', nFields)
            self.writeCall('Memory.alloc', 1)
            self.writePop('pointer', 0)
        self.convertSubroutineBody(subroutineBody)

    def convertSubroutineBody(self, subroutineBody):
        subroutineBody = self._getBody(subroutineBody, "subroutineBody")
        print("### SUBROUTINE BODY ###")
        print(subroutineBody)
        for body in subroutineBody:
            if "varDec" in body:
                self.convertVarDec(body)
            elif "statements" in body:
                self.convertStatements(body)    
        return

    # sentences
    # 入力：componentのbodyもしくは{"xxx": [<componentのbody>]}
    def convertStatements(self, statements):
        print("$$$ statements $$$")
        print(statements)
        statements = self._getBody(statements, "statements")
        for statement in statements:
            self.convertStatement(statement)
    
    def convertStatement(self, statement):
        statement = self._getBody(statement, "statement")
        statementType = list(statement.keys())[0]
        statementTypeUpper = statementType[0].upper() + statementType[1:]
        getattr(self, 'convert'+statementTypeUpper)(statement[statementType])
    
    def convertLetStatement(self, let):
        let = self._getBody(let, "letStatement")
        print("$$$ LET $$$")
        print(let)

        self.convertExpression(let[-2])
        var = let[1]["identifier"]
        kind = "this" if var["kind"] == "field" else var["kind"]
        # let varName[expression] = expression;
        if len(let) == 8:
            self.convertExpression(let[3])
            self.writePush(kind, var["index"])
            self.writeArithmetic('add')
            self.writePop('pointer', 1)
            self.writePop('that', 0)   
            return
        # let varName = expression;
        if len(let) == 5:
            self.writePop(kind, var["index"])
            return 
        
        print(let)
        raise Exception("invalid let statement")
    
    def convertIfStatement(self, ifStatement):
        ifStatement = self._getBody(ifStatement, "ifStatement")
        print("$$$ if $$$")
        print(json.dumps(ifStatement, indent=2))

        cond = ifStatement[2]
        trueStatements = ifStatement[5]
        falseStatements = ifStatement[9] if len(ifStatement) == 11 else None
        endLabel = "END{}".format(self.boolCount)
        falseLabel = "FALSE{}".format(self.boolCount)
        self.boolCount += 1

        self.convertExpression(cond)
        self.writeArithmetic('not')
        self.writeIf(falseLabel)
        self.convertStatements(trueStatements)
        self.writeGoto(endLabel)
        self.writeLabel(falseLabel)
        if falseStatements is not None:
            self.convertStatements(falseStatements)
        self.writeLabel(endLabel)

    def convertWhileStatement(self, whileStatement):
        whileStatement = self._getBody(whileStatement, "whileStatement")
        print("$$$ while $$$")
        print(whileStatement)

        cond = whileStatement[2]
        statements = whileStatement[5]
        startLabel = "STARTWHILE{}".format(self.boolCount)
        endLabel = "ENDWHILE{}".format(self.boolCount)
        self.boolCount += 1

        self.writeLabel(startLabel)
        self.convertExpression(cond)
        self.writeArithmetic('not')
        self.writeIf(endLabel)
        self.convertStatements(statements)
        self.writeGoto(startLabel)
        self.writeLabel(endLabel)
    
    def convertDoStatement(self, doStatement):
        doStatement = self._getBody(doStatement, "doStatement")
        print("$$$ do $$$")
        print(doStatement)

        subroutineCall = doStatement[1:-1]
        self.convertSubroutineCall(subroutineCall)
        self.writePop('temp', 0)
    
    def convertReturnStatement(self, returnStatement):
        returnStatement = self._getBody(returnStatement, "returnStatement")

        if len(returnStatement) == 3:
            self.convertExpression(returnStatement[1])
        else: # for void function
            self.writePush('constant', 0)
        self.writeReturn()

    # expressions
    # 入力：componentのbodyもしくは{"xxx": [<componentのbody>]}
    # 結果：その式の結果がstackの一番上にくることを保証すること
    def convertExpression(self, exp):
        exp = self._getBody(exp, "expression")
        print("$$$ EXPRESSION $$$")
        print(json.dumps(exp, indent=2))
        print(len(exp))

        self.convertTerm(exp[0])
        idx = 0
        while (idx+2 < len(exp)):
            self.convertTerm(exp[idx+2])
            self.convertOp(exp[idx+1])
            idx += 2

    def convertTerm(self, term):
        term = self._getBody(term, "term")
        print("$$$ TERM $$$")
        print(term)

        if len(term) == 6: # (className | varName) . subroutineName ( expressionList )
            self.convertSubroutineCall(term)
        elif len(term) == 4:
            if "symbol" in term[-1] and term[-1]["symbol"] == "]": # varName[expression]
                var = term[0]["identifier"]
                kind = "this" if var["kind"] == "field" else var["kind"]
                self.writePush(kind, var["index"])
                self.convertExpression(term[2])
                self.writeArithmetic('add')
                self.writePop('pointer', 1)
                self.writePush('that', 0)
            else: # subroutineName ( expressionList )
                self.convertSubroutineCall(term)
        elif len(term) == 3: # (expression)
            self.convertExpression(term[1]) 
        elif len(term) == 2: # unaryOp term
            self.convertTerm(term[1])
            self.convertUnaryOp(term[0])
        elif len(term) == 1:   # (integerConstant|stringConstant|keywordConstant|varName(=identifier))
            key = list(term[0].keys())[0]
            upperKey = key[0].upper() + key[1:] # ex) integerConstant -> IntegerConstant
            value = term[0][key]
            getattr(self, 'convert'+upperKey)(value)
        else:
            print(term)
            raise Exception("invalid term")
    
    def convertSubroutineCall(self, subroutineCall):
        subroutineCall = self._getBody(subroutineCall, "subroutineCall")
        print("$$$ subroutineCall $$$")
        print(subroutineCall)
        
        if len(subroutineCall) == 4:
            subroutineName = subroutineCall[0]["identifier"]["name"]
            expressionList = subroutineCall[2]
            self.writePush('pointer', 0)
            nArgs = self.convertExpressionList(expressionList)
            self.writeCall(self.currentClassName+'.'+subroutineName, nArgs+1)
            return

        if len(subroutineCall) == 6:
            subj = subroutineCall[0]["identifier"]
            expressionList = subroutineCall[4]
            subroutineName = subroutineCall[2]["identifier"]["name"]
            if subj["type"] == "className":
                nArgs = self.convertExpressionList(expressionList)
                self.writeCall("{}.{}".format(subj["name"], subroutineName), nArgs)
            else:
                kind = "this" if subj["kind"] == "field" else subj["kind"]
                self.writePush(kind, subj["index"])
                nArgs = self.convertExpressionList(expressionList)
                self.writeCall("{}.{}".format(subj["type"], subroutineName), nArgs+1)
            return
           
        print(subroutineCall)
        raise Exception("invalid subroutineCall")
    
    def convertExpressionList(self, expList):
        expList = self._getBody(expList, "expressionList")
        print("$$$ EXPRESSION LIST $$$")
        print(json.dumps(expList, indent=2))
        print(len(expList))

        
        if len(expList) == 0:
            return 0
        self.convertExpression(expList[0])
        idx = 0
        nExp = 1
        while (idx+2 < len(expList)):
            self.convertExpression(expList[idx+2])
            idx += 2
            nExp += 1
        return nExp
    
    # constants/reserved words
    # 入力：string or integer, （dictならunwrapされる）
    # 結果：その式の結果がstackの一番上にくることを保証すること
    def convertOp(self, op):
        if isinstance(op, dict):
            op = op["symbol"]
        if op == '*':
            self.writeCall("Math.multiply", 2)
        elif op == '/':
            self.writeCall("Math.divide", 2)
        else:
            opMap = {
                '+': 'add',
                '-': 'sub',
                '&': 'and',
                '|': 'or',
                '<': 'lt',
                '>': 'gt',
                '=': 'eq'
            }
            self.writeArithmetic(opMap[op])
        return

    def convertUnaryOp(self, unaryOp):
        if isinstance(unaryOp, dict):
            unaryOp = unaryOp["symbol"]
        opMap = {
            "-": 'neg',
            "~": 'not'
        }
        self.writeArithmetic(opMap[unaryOp])
        return
    
    def convertKeyword(self, keywordConstant):
        if isinstance(keywordConstant, dict):
            keywordConstant = keywordConstant["keywordConstant"]
        if keywordConstant == 'true':
            self.writePush('constant', 1)
            self.writeArithmetic('neg')
        elif keywordConstant in ['false', 'null']:
            self.writePush('constant', 0)
        elif keywordConstant == 'this':
            self.writePush('pointer', 0)
        else:
            raise Exception("invalid keyword constant")
        return
    
    def convertIntegerConstant(self, integerConstant):
        if isinstance(integerConstant, dict):
            integerConstant = integerConstant["integerConstant"]
        self.writePush('constant', integerConstant)
    
    def convertStringConstant(self, stringConstant):
        if isinstance(stringConstant, dict):
            stringConstant = stringConstant["stringConstant"]
        length = len(stringConstant)
        self.writePush('constant', length)
        self.writeCall('String.new', 1) # x = String.new(length)
        for ch in stringConstant:
            self.writePush('constant', ord(ch))
            self.writeCall('String.appendChar', 2) # String.appendChar(nextchar)
        
    def convertIdentifier(self, identifier):
        if "identifier" in identifier:
            identifier = identifier["identifier"]
        kind = "this" if identifier["kind"] == "field" else identifier["kind"]
        self.writePush(kind, identifier["index"])
    