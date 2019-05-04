# -*- coding: utf-8 -*-
import re

class Parser():

    CMD_TYPES = {
        "C_ARITHMETIC": {"regex": "^(add|sub|neg|eq|gt|lt|and|or|not)$",
                         "extraction": {"command": 1}},
        "C_PUSH": {"regex": "^(push)\s(argument|local|static|constant|this|that|pointer|temp)\s([0-9]+)$",
              "extraction": {"command": 1, "segment": 2, "index": 3}},
        "C_POP": {"regex": "^(pop)\s(argument|local|static|constant|this|that|pointer|temp)\s([0-9]+)$",
              "extraction": {"command": 1, "segment": 2, "index": 3}},
        "C_LABEL": {"regex": "^(label)\s([0-9a-zA-Z_\.:]+)$",
              "extraction": {"command": 1, "symbol": 2}},
        "C_GOTO": {"regex": "^(goto)\s([0-9a-zA-Z_\.:]+)$",
              "extraction": {"command": 1, "symbol": 2}},
        "C_IF": {"regex": "^(if-goto)\s([0-9a-zA-Z_\.:]+)$",
              "extraction": {"command": 1, "symbol": 2}},
        "C_FUNCTION": {"regex": "^(function)\s([0-9a-zA-Z_\.:]+)\s([0-9]+)$",
              "extraction": {"command": 1, "functionName": 2, "nLocals":3}},
        "C_CALL": {"regex": "^(call)\s([0-9a-zA-Z_\.:]+)\s([0-9]+)$",
              "extraction": {"command": 1, "functionName": 2, "nArgs":3}},
        "C_RETURN": {"regex": "^(return)$",
              "extraction": {"command": 1}}
    }
    COMMENT = "//"

    def __init__(self, filepath):
        self.asm = []
        with open(filepath, 'r') as fp:
            for line in fp:
                command = line.strip()
                if self.COMMENT in line:
                    comment_idx = command.find(self.COMMENT)
                    command = command[:comment_idx]
                if command:
                    self.asm.append(command)
        
        for key, value in self.CMD_TYPES.items():
            self.CMD_TYPES[key].setdefault("compiled_regex", re.compile(value["regex"]))
        
        self.reset()

    def reset(self):
        self.line_num = None
        self.command = ""
        self.parsed_command = {}
        self.command_type = None

    def hasMoreCommands(self):
        if self.line_num is None:
            return True
        if len(self.asm) <= self.line_num + 1:
            return False
        return True
    
    def advance(self):
        if not self.hasMoreCommands():
            return None
        if self.line_num is None:
            self.line_num = 0
        else:
            self.line_num = self.line_num + 1
        self.command = self.asm[self.line_num]
        (self.command_type, self.parsed_command) = self.parseCommand(self.command)
    
    @classmethod
    def parseCommand(cls, command):
        for cmdtype, cmdspec in cls.CMD_TYPES.items():
            matched = cmdspec["compiled_regex"].match(command)
            if matched:
                parsed_command = {}
                for argname, groupnum in cmdspec["extraction"].items():
                    parsed_command[argname] = matched.group(groupnum)
                return (cmdtype, parsed_command)
        
        raise Exception("Translation failed!: line {}".format(command))
    
    @property
    def commandType(self):
        return self.command_type
    
    @property
    def parsedCommand(self):
        return self.parsed_command