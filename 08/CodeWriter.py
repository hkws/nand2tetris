# -*- coding: utf-8 -*-
class CodeWriter():

    def __init__(self, output):
        self.outputFilePath = output
        self.table = SymbolTable(16)
        self.bool_count = 0
        self.filename = None
        self.call_count = 0
    
    def __enter__(self):
        self.fp = open(self.outputFilePath, 'w')
        self.write_init()
        return self
    
    def __exit__(self, ex_type, ex_value, trace):
        self.fp.close()
    
    def setFileName(self, name):
        self.filename = name
    
    def _write(self, words):
        if not isinstance(words, list):
            words = [words]
        self.fp.write("\n".join(words)+"\n")
        
    def write_init(self):
        words = ["@256",
                 "D=A",
                 "@SP",
                 "M=D"]
        self._write(words)
        self.write_C_CALL('call', 'Sys.init', 0)

    def write_C_ARITHMETIC(self, command):
        if command in ["add"]:
            words = self.get_arith_binary_words("M=D+M")
        elif command in ["sub"]:
            words = self.get_arith_binary_words("M=M-D")
        elif command in ["neg"]:
            words = self.get_arith_unary_words("M=-M")
        elif command in ["eq", "gt", "lt"]:
            words = self.get_arith_binary_words(["D=M-D",
                                                "@BOOL{}".format(self.bool_count),
                                                "D;J{}".format(command.upper()),
                                                
                                                "@SP",
                                                "A=M",
                                                "M=0",
                                                "@ENDBOOL{}".format(self.bool_count), # M=true処理を飛ばしてその次の命令に
                                                "0;JMP",
                                                
                                                "(BOOL{})".format(self.bool_count), # D==Mならここに到達しM=trueに変更
                                                "@SP",
                                                "A=M",
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
        binwords = [*self.pop_to_D_and_update_SP(),
                    "@SP",
                    "M=M-1",
                    "A=M",
                    *words,
                    "@SP",
                    "M=M+1"]
        return binwords
    
    def get_arith_unary_words(self, words):
        # M is *(sp-1), The result must be stored in M
        if not isinstance(words, list):
            words = [words]
        unarywords = ["@SP",
                      "M=M-1",
                      "A=M",
                      *words,
                      "@SP",
                      "M=M+1"]
        return unarywords

    def write_C_PUSH(self, command, segment, index):
        if segment in ["constant"]:
            words = ["@{}".format(index),
                     "D=A",
                     *self.push_D_and_update_SP()]
        elif segment in ["local", "argument", "this", "that", "pointer", "temp"]:
            addr = {"local": 1, "argument": 2, "this": 3, "that": 4, "pointer": 3, "temp": 5}[segment]
            words = ["@R"+str(addr),
                     "D=M",
                     "@"+str(index),
                     "A=D+A", # ここでAはsegment[index]のアドレス
                     "D=M",
                     *self.push_D_and_update_SP()]
        elif segment in ["pointer", "temp"]:
            addr = {"pointer": 3, "temp": 5}[segment]
            words = ["@R"+str(addr + int(index)), # ここでAはsegment[index]のアドレス
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
            addr = {"local": 1, "argument": 2, "this": 3, "that": 4}[segment]
            words = ["@R"+str(addr),
                     "D=M",
                     "@"+str(index),
                     "A=D+A",
                     "D=A",
                     "@R13", # R13にアドレスregname[index]のアドレスを記録
                     "M=D",
                     *self.pop_to_D_and_update_SP(),
                     "@R13", 
                     "A=M",
                     "M=D"]
        if segment in ["pointer", "temp"]:
            addr = {"pointer": 3, "temp": 5}[segment]
            words = ["@R"+str(addr + int(index)),
                     "D=A",
                     "@R13", # R13にアドレスregname[index]のアドレスを記録
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
                "M=M-1",
                "A=M",
                "D=M"]
    
    def write_C_LABEL(self, command, symbol):
        words = ["({}${})".format(self.filename, symbol)]
        self._write(words)
    
    def write_C_GOTO(self, command, symbol):
        words = ["@{}${}".format(self.filename, symbol),
                 "0;JMP"]
        self._write(words)
    
    def write_C_IF(self, command, symbol):
        words = self.pop_to_D_and_update_SP()
        words.extend(["@{}${}".format(self.filename, symbol),
                      "D;JNE"])
        self._write(words)
    
    def write_C_FUNCTION(self, command, functionName, nLocals):
        words = ["({})".format(functionName)]
        for i in range(int(nLocals)):
            words.append("D=0")
            words.extend(self.push_D_and_update_SP())
        self._write(words)
    
    def write_C_RETURN(self, command):
        FRAME = 'R14'
        RET = 'R13'

        def _restore(symbol, idx):
            return ["@"+FRAME, # THATの指し先を戻す
                    "D=M",
                    "@"+str(idx),
                    "D=D-A",
                    "A=D",
                    "D=M",
                    "@"+symbol,
                    "M=D"]

        words = ["@LCL",  # FRAME = LCL 
                 "D=M",
                 "@"+FRAME,
                 "M=D",

                 "@"+FRAME, # RET=*(FRAME-5)
                 "D=M",
                 "@5",
                 "D=D-A",
                 "A=D",
                 "D=M",
                 "@"+RET, # 戻り先命令アドレスを保存
                 "M=D",

                 *self.pop_to_D_and_update_SP(), # stackの一番上には戻り値が入っているので取得
                 "@ARG", # 戻り値はARG[0]に格納
                 "A=M",
                 "M=D",

                 "@ARG", # SPをARG[1]に
                 "D=M",
                 "@SP",
                 "M=D+1",
                 
                 *_restore('THAT', 1),
                 *_restore('THIS', 2),
                 *_restore('ARG', 3),
                 *_restore('LCL', 4),

                 "@"+RET, # R13に格納しておいた戻り先命令アドレスにjump
                 "A=M",
                 "0;JMP"
                ]
        self._write(words)
    
    def write_C_CALL(self, command, functionName, nArgs):
        def _save(symbol):
            return ["@"+symbol,
                    "D=M",
                    *self.push_D_and_update_SP()]

        RET = 'RET_{}_{}'.format(functionName, self.call_count)
        words = ["@"+RET,
                 "D=A",
                 *self.push_D_and_update_SP(),
                 *_save('LCL'),
                 *_save('ARG'),
                 *_save('THIS'),
                 *_save('THAT'),
                 "@SP", # 関数呼び出し側のTHATの次から呼ばれる関数用LCL領域(LCL=SP)
                 "D=M",
                 "@LCL",
                 "M=D",
                 "@SP", # ARGの値を呼ばれる関数のために変更(ARG=SP-n-5)
                 "D=M",
                 "@{}".format(int(nArgs)+5),
                 "D=D-A",
                 "@ARG",
                 "M=D",
                 "@"+functionName,
                 "0;JMP",
                 "({})".format(RET)]
        self._write(words)
        self.call_count = self.call_count + 1
        

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
