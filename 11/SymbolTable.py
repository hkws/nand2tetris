import copy, json

class SymbolTable():

    def __init__(self):
        self.table = []
        self.indices = []
    
    def startScope(self, key, *args, **kwargs):
        self.table.append({})
        self.indices.append({"static": 0,
                             "field": 0,
                             "argument": 0,
                             "local": 0})
        return key
    
    def endScope(self, bodies, key, *args, **kwargs):
        self.table.pop()
        self.indices.pop()
        return bodies
    
    def define(self, name, typename, kind, scopeIdx=-1):
        record = {name: {"type": typename,
                         "kind": kind,
                         "index": self.indices[scopeIdx][kind]}}
        self.table[scopeIdx].update(record)
        self.indices[scopeIdx][kind] += 1
    
    def isDefined(self, name, scopeIdx=-1):
        try: 
            if name in self.table[scopeIdx]:
                return True
            else:
                return self.kindOf(name, scopeIdx-1)
        except IndexError as e:
            return False        

    def varCount(self, kind, scopeIdx=-1):
        return self.indices[scopeIdx][kind]
    
    def kindOf(self, name, scopeIdx=-1):
        if name in self.table[scopeIdx]:
            return self.table[scopeIdx][name]["kind"]
        else:
            return self.kindOf(name, scopeIdx-1)
    
    def typeOf(self, name, scopeIdx=-1):
        if name in self.table[scopeIdx]:
            return self.table[scopeIdx][name]["type"]
        else:
            return self.typeOf(name, scopeIdx-1)
    
    def indexOf(self, name, scopeIdx=-1):
        if name in self.table[scopeIdx]:
            return self.table[scopeIdx][name]["index"]
        else:
            return self.indexOf(name, scopeIdx-1)
    
    def addClassVar(self, bodies, **kwargs):
        kind = bodies[0]["keyword"]
        typ = bodies[1]["identifier"]["name"] if "identifier" in bodies[1] else bodies[1]["keyword"]
        idx = 2
        while(idx < len(bodies)):
            sname = bodies[idx]["identifier"]["name"]
            self.define(sname, typ, kind)
            bodies[idx]["identifier"] = self._getEntryByName(sname)
            idx = idx + 2
        return bodies
    
    def addVar(self, bodies, **kwargs):
        kind = "local"
        typ = bodies[1]["identifier"]["name"] if "identifier" in bodies[1] else bodies[1]["keyword"]
        sname = bodies[2]["identifier"]["name"]
        self.define(sname, typ, kind)
        bodies[2]["identifier"] = self._getEntryByName(sname)
        idx = 4
        while (idx < len(bodies)):
            sname = bodies[idx]["identifier"]["name"]
            self.define(sname, typ, kind)
            bodies[idx]["identifier"] = self._getEntryByName(sname)
            idx = idx + 2
        return bodies
    
    def addParameter(self, bodies, **kwargs):
        # print("### add parameter ###")
        # print(bodies)
        # input()
        for i, v in enumerate(bodies):
            if ("identifier" not in v) or ("identifier" in v and "type" in v["identifier"] and v["identifier"]["type"] == "className"):
                continue
            sname = v["identifier"]["name"]
            typ = bodies[i-1]["identifier"]["name"] if "identifier" in bodies[i-1] else bodies[i-1]["keyword"]
            kind = "argument"
            self.define(sname, typ, kind)
            v["identifier"] = self._getEntryByName(sname)
        return bodies

    def _getEntryByName(self, sname):
        kind = self.kindOf(sname)
        typ = self.typeOf(sname)
        idx = self.indexOf(sname)
        #return "name: {}, kind: {}, type: {}, index: {}".format(sname, kind, typ, idx)
        return {
            "name": sname,
            "type": typ,
            "index": idx,
            "kind": kind
        }

    def referSymbolInTerm(self, bodies, **kwargs):
        # varName
        if len(bodies) == 1 and "identifier" in bodies[0]:
            bodies[0]["identifier"] = self._getEntryByName(bodies[0]["identifier"]["name"])
        # varName [ expression ]
        elif len(bodies) > 2 and "identifier" in bodies[0] and \
            ("symbol" in bodies[1] and bodies[1]["symbol"] == "[") and \
            ("symbol" in bodies[-1] and bodies[-1]["symbol"] == "]"):
            bodies[0]["identifier"] = self._getEntryByName(bodies[0]["identifier"]["name"])
        return bodies
    
    def referSymbolInLetStatement(self, bodies, **kwargs):
        if not ("identifier" in bodies[1]):
            raise Exception("letStatement parse Error")
        bodies[1]["identifier"] = self._getEntryByName(bodies[1]["identifier"]["name"])
        return bodies

    def referSymbolInSubroutineCall(self, bodies, **kwargs):
        # (className | varName) . subroutineName ( expression )
        if "identifier" in bodies[0] and "symbol" in bodies[1] and bodies[1]["symbol"] == ".":
            if self.isDefined(bodies[0]["identifier"]["name"]):
                bodies[0]["identifier"] = self._getEntryByName(bodies[0]["identifier"]["name"])
        return bodies
    
    def editClassNameObj(self, bodies, **kwargs):
        # bodies[0]["identifier"] = "{} (className)".format(bodies[0]["identifier"])
        print(bodies)
        bodies[0]["identifier"] = {
            "name": bodies[0]["identifier"]["name"],
            "type": "className"
        }
        return bodies
    
    def editSubroutineNameObj(self, bodies, **kwargs):
        #bodies[0]["identifier"] = "{} (subroutineName)".format(bodies[0]["identifier"])
        bodies[0]["identifier"] = {
            "name": bodies[0]["identifier"]["name"],
            "type": "subroutineName"
        }
        return bodies

    def editClassObj(self, bodies, **kwargs):
        bodies[1]["identifier"].update({"fieldCount": self.varCount("field")})
        return bodies
    
    def editSubroutineDecObj(self, bodies, **kwargs):
        bodies[2]["identifier"].update({"localCount": self.varCount("local")})
        # if bodies[0]["keyword"] == "method" and bodies[4]["parameterList"]:
        #     for o in bodies[4]["parameterList"]:
        #         if "identifier" in o:
        #             o["identifier"]["index"] += 1
        #     for v in self.table[-1].values():
        #         if isinstance(v, dict) and "kind" in v and v["kind"] == "argument":
        #             v["index"] += 1
        return bodies
    
    def addDummyArgumentForMethod(self, bodies, **kwargs):
        self.define("dummy", "boolean", "argument")
        return bodies
    
            
