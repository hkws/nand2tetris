# -*- coding: utf-8 -*-
class CodeWriter():

    def __init__(self, output):
        self.outputFilePath = output
        self.table = SymbolTable(16)
        self.bool_count = 0
        self.filename = None
    
    def __enter__(self):
        self.fp = open(self.outputFilePath, 'w')
        self.write_init()
        return self
    
    def __exit__(self, ex_type, ex_value, trace):
        self.fp.close()
    
    def setFileName(self, name):
        self.filename = name
    
    def _write(self, word):
        if not isinstance(word, list):
            word = [word]
        self.fp.write("\n".join(word)+"\n")

    def write_init(self):
        pass

    def write_C_ARITHMETIC(self, command):
        if command in ["add"]:
            words = self.get_arith_binary_words("M=M+D")
        elif command in ["sub"]:
            words = self.get_arith_binary_words("M=M-D")
        elif command in ["neg"]:
            words = self.get_arith_unary_words("M=-M")
        elif command in ["eq", "gt", "lt"]:
            words = self.get_arith_binary_words(["D=M-D",
                                                "M=0",    # ひとまずfalseを代入 
                                                
                                                "@BOOL{}".format(self.bool_count),
                                                "D;J{}".format(command.upper()),
                                                
                                                "@ENDBOOL{}".format(self.bool_count), # M=true処理を飛ばしてその次の命令に
                                                "0;JMP",
                                                
                                                "(BOOL{})".format(self.bool_count), # D==Mならここに到達しM=trueに変更
                                                "@SP",
                                                "A=M",
                                                "A=A-1",
                                                "A=A-1",
                                                "M=-1",
                                                "@ENDBOOL{}".format(self.bool_count),
                                                "0;JMP",
                                                
                                                "(ENDBOOL{})".format(self.bool_count), # つづき
                                                ])
            self.bool_count = self.bool_count + 1
        elif command in ["and"]:
            words = self.get_arith_binary_words("M=D&M")
        elif command in ["or"]:
            words = self.get_arith_binary_words("M=D|M")
        elif command in ["not"]:
            words = self.get_arith_unary_words("M=!M")
        else:
            raise Exception("Translation failed!: line {}".format(command))
        self._write(words)

    def get_arith_binary_words(self, words):
        # D is *(sp-1), M is *(sp-2), The result must be stored in M
        if not isinstance(words, list):
            words = [words]
        binwords = ["@SP",
                    "A=M",
                    "A=A-1",
                    "D=M",
                    "A=A-1",
                    *words,
                    "@SP",
                    "M=M-1"]
        return binwords
    
    def get_arith_unary_words(self, words):
        # M is *(sp-1), The result must be stored in M
        if not isinstance(words, list):
            words = [words]
        unarywords = ["@SP",
                      "A=M",
                      "A=A-1",
                      *words]
        return unarywords

    def write_C_PUSH(self, command, segment, index):
        if segment in ["constant"]:
            words = ["@{}".format(index),
                     "D=A",
                     *self.push_D_and_update_SP()]
        elif segment in ["local", "argument", "this", "that"]:
            regname = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT"}[segment]
            words = ["@{}".format(index),
                     "D=A",
                     "@{}".format(regname),
                     "D=D+M",
                     "A=D",
                     "D=M",
                     *self.push_D_and_update_SP()]
        elif segment in ["pointer", "temp"]:
            regname = {"pointer": "THIS", "temp": "R5"}[segment]
            words = ["@{}".format(index),
                     "D=A",
                     "@{}".format(regname),
                     "D=D+A",
                     "A=D",
                     "D=M",
                     *self.push_D_and_update_SP()]
        elif segment in ["static"]:
            words = ["@{}.{}".format(self.filename, index),
                     "D=M",
                     *self.push_D_and_update_SP()]
        self._write(words)
    
    def push_D_and_update_SP(self):
        # push value in D register to stack
        return ["@SP",
                "A=M",
                "M=D",
                "@SP",
                "M=M+1"]
    
    def write_C_POP(self, command, segment, index):
        if segment in ["local", "argument", "this", "that"]:
            regname = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT"}[segment]
            words = ["@{}".format(index),
                     "D=A",
                     "@{}".format(regname),
                     "D=D+M",
                     "@R13", # R13にアドレスregname[index]のアドレスを記録
                     "M=D",
                     *self.pop_to_D_and_update_SP(),
                     "@R13", 
                     "A=M",
                     "M=D"]
        elif segment in ["pointer", "temp"]:
            regname = {"pointer": "THIS", "temp": "R5"}[segment]
            words = ["@{}".format(index),
                     "D=A",
                     "@{}".format(regname),
                     "D=D+A",
                     "@R13",
                     "M=D",
                     *self.pop_to_D_and_update_SP(),
                     "@R13",
                     "A=M",
                     "M=D"]
        elif segment in ["static"]:
            words = [*self.pop_to_D_and_update_SP(),
                     "@{}.{}".format(self.filename, index),
                     "M=D"]
        self._write(words)

    def pop_to_D_and_update_SP(self):
        # push value in D register to stack
        return ["@SP",
                "A=M",
                "A=A-1",
                "D=M",
                "@SP",
                "M=M-1"]
    
    def write_C_Label(self, command, symbol):
        words = ["({})".format(symbol)]
        self._write(words)
    
    def write_C_GOTO(self, command, symbol):
        words = ["@{}".format(symbol),
                 "0;JMP"]
        self._write(words)
    
    def write_C_IF(self, command, symbol):
        words = self.pop_to_D_and_update_SP()
        words.extend(["@end_{}".format(symbol),
                      "D;JEQ",
                      "@{}".format(symbol),
                      "0;JMP",
                      "(end_{})".format(symbol)
                    ])
        self._write(words)
    
    def write_C_FUNCTION(self):
        pass
    
    def write_C_RETURN(self):
        pass
    
    def write_C_CALL(self):
        pass


class SymbolTable():

    DEFAULT = {
        "SP": 0,
        "LCL": 1,
        "ARG": 2,
        "POINTER_START": 3,
        "POINTER_END": 4,
        "THIS": 3,
        "THAT": 4,
        "TEMP_START": 5,
        "TEMP_END": 12,
        "STATIC_START": 16,
        "STATIC_END": 255,
        "STACK_START": 256,
        "STACK_END": 2047,
        "HEAP_START": 2048,
        "HEAP_END": 16383,
        "SCREEN": 16384,
        "KBD": 24576
    }

    def __init__(self, reserved_register_num):
        self.table = self.DEFAULT
        for i in range(reserved_register_num):
            self.table.setdefault("R"+str(i), i)
        self.next_allocated_addr = reserved_register_num
    
    def addVariableSymbolEntry(self, symbol):
        addr = self.next_allocated_addr
        self.addEntry(symbol, addr)
        self.next_allocated_addr = self.next_allocated_addr + 1
        if self.DEFAULT["HEAP_END"] <= self.next_allocated_addr:
            raise MemoryError("Could not allocate memory.")
        return addr
    
    def addEntry(self, symbol, address):
        self.table.setdefault(symbol, address)
    
    def contains(self, symbol):
        return symbol in self.table
    
    def getAddress(self, symbol):
        return self.table.get(symbol, None)
