# -*- coding: utf-8 -*-
import sys, re, json
import pathlib

class Parser():

    CMD_TYPES = {
        "A": {"regex": "^@([a-zA-Z0-9_\.\$:]+)$",
              "extraction": {"symbol": 1}},
        "C": {"regex": "^(([ADM]{1,3})=)?([^=;\(\)]+)(;(JGT|JEQ|JGE|JLT|JNE|JLE|JMP))?$",
              "extraction": {"dest": 2, "comp": 3, "jump": 5}},
        "L": {"regex": "^\(([a-zA-Z0-9_\.\$:]+)\)$",
              "extraction": {"label": 1}}
    }
    COMMENT = "//"

    def __init__(self, filepath):
        self.asm = []
        with open(filepath, 'r') as fp:
            for line in fp:
                command = line.replace(" ", "").replace("\n", "")
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
    
    def _getMnemonic(self, mnemoType):
        if mnemoType in self.parsed_command:
            return self.parsed_command[mnemoType]
        else:
            return None

    @property
    def symbol(self):
        return self._getMnemonic('symbol')
    
    @property
    def dest(self):
        return self._getMnemonic('dest')
    
    @property
    def comp(self):
        return self._getMnemonic('comp')

    @property
    def jump(self):
        return self._getMnemonic('jump')


class Code():

    @classmethod
    def binaryToDecimal(cls, binary):
        if not isinstance(binary, str):
            binary = str(binary)
        return int(binary, 2)

    @classmethod
    def decimalToBinary(cls, decimal, ndigits):
        if isinstance(decimal, str):
            decimal = int(decimal)
        return format(decimal, "0{}b".format(ndigits))

    @classmethod
    def dest(cls, dest):
        if dest is None:
            return "000"
        bins = ['0'] * 3
        if "A" in dest:
            bins[0] = '1'
        if "D" in dest:
            bins[1] = '1'
        if "M" in dest:
            bins[2] = '1'
        return "".join(bins)
    
    @classmethod
    def comp(cls, comp):
        compMap = {"0": "0101010",
                   "1": "0111111",
                   "-1": "0111010",
                   "D": "0001100",
                   "A": "0110000",
                   "!D": "0001101",
                   "!A": "0110001",
                   "-D": "0001111",
                   "-A": "0110011",
                   "D+1": "0011111",
                   "A+1": "0110111",
                   "D-1": "0001110",
                   "A-1": "0110010",
                   "D+A": "0000010",
                   "D-A": "0010011",
                   "A-D": "0000111",
                   "D&A": "0000000",
                   "D|A": "0010101",
                   "M": "1110000",
                   "!M": "1110001",
                   "-M": "1110011",
                   "M+1": "1110111",
                   "M-1": "1110010",
                   "D+M": "1000010",
                   "D-M": "1010011",
                   "M-D": "1000111",
                   "D&M": "1000000",
                   "D|M": "1010101"}
        if not comp in compMap:
            raise AttributeError("Comp mnemonic {} not found".format(comp))
        return compMap[comp]
    
    @classmethod
    def jump(cls, jump):
        if jump == "JGT":
            return "001"
        elif jump == "JEQ":
            return "010"
        elif jump == "JGE":
            return "011"
        elif jump == "JLT":
            return "100"
        elif jump == "JNE":
            return "101"
        elif jump == "JLE":
            return "110"
        elif jump == "JMP":
            return "111"
        else:
            return "000"


class SymbolTable():

    DEFAULT = {
        "SP": 0,
        "LCL": 1,
        "ARG": 2,
        "THIS": 3,
        "THAT": 4,
        "SCREEN": 16384,
        "KBD": 24576
    }
    ADDRESS_MAX = 16383

    def __init__(self, reserved_register_num):
        self.table = self.DEFAULT
        for i in range(reserved_register_num):
            self.table.setdefault("R"+str(i), i)
        self.next_allocated_addr = reserved_register_num
    
    def addVariableSymbolEntry(self, symbol):
        addr = self.next_allocated_addr
        self.addEntry(symbol, addr)
        self.next_allocated_addr = self.next_allocated_addr + 1
        if self.ADDRESS_MAX <= self.next_allocated_addr:
            raise MemoryError("Could not allocate memory.")
        return addr
    
    def addEntry(self, symbol, address):
        self.table.setdefault(symbol, address)
    
    def contains(self, symbol):
        return symbol in self.table
    
    def getAddress(self, symbol):
        return self.table.get(symbol, None)


def main():
    if len(sys.argv) != 2:
        print(".asm file path is required.")
        return
    
    sourcePath = pathlib.Path(sys.argv[1]).resolve()
    filename = sys.argv[1].split('/')[-1].split('.')[0]
    destinationPath = '/'.join(str(sourcePath).split('/')[:-1])+'/'+filename+'.hack'

    parser = Parser(sourcePath)
    print("INPUT: {}".format(json.dumps(parser.asm, indent=2)))
    sTable = SymbolTable(16)
    line_count = 0

    # add label entry to symbol label
    while(parser.hasMoreCommands()):
        parser.advance()
        print("--------------------")
        print("COMMAND: {}".format(parser.command))
        print("TYPE: {}".format(parser.command_type))
        print("ARGS: {}".format(json.dumps(parser.parsed_command, indent=2)))
        if parser.command_type in ["C", "A"]:
            line_count = line_count + 1
        elif parser.command_type in ["L"]:
            sTable.addEntry(parser.parsed_command["label"], line_count)

    print("CREATED SYMBOL TABLE: {}".format(json.dumps(sTable.table, indent=2)))

    # convert to binary codes
    parser.reset()
    binaryCodes = []

    while(parser.hasMoreCommands()):
        parser.advance()

        if parser.command_type in ["A"]:
            symbol = parser.parsed_command["symbol"]
            if sTable.contains(symbol):
                addr = sTable.getAddress(symbol)
            elif symbol.isdecimal():
                addr = int(symbol)
            else:
                addr = sTable.addVariableSymbolEntry(symbol)    
            code = Code.decimalToBinary(addr, 15)
            binaryCodes.append("0{}".format(code))
        
        if parser.command_type in ["C"]:
            print(parser.parsed_command)
            comp = Code.comp(parser.parsed_command["comp"])
            dest = Code.dest(parser.parsed_command["dest"])
            jump = Code.jump(parser.parsed_command["jump"])
            binaryCodes.append("111{}{}{}".format(comp, dest, jump))
    
    with open(destinationPath, 'w') as fp:
        fp.write('\n'.join(binaryCodes))

    return


if __name__ == '__main__':
    main()