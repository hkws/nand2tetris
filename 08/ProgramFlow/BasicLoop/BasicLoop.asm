@0
D=A
@SP
A=M
M=D
@SP
M=M+1
@0
D=A
@LCL
D=D+M
@R13
M=D
@SP
A=M
A=A-1
D=M
@SP
M=M-1
@R13
A=M
M=D
(LOOP_START)
@0
D=A
@ARG
D=D+M
A=D
D=M
@SP
A=M
M=D
@SP
M=M+1
@0
D=A
@LCL
D=D+M
A=D
D=M
@SP
A=M
M=D
@SP
M=M+1
@SP
A=M
A=A-1
D=M
A=A-1
M=M+D
@SP
M=M-1
@0
D=A
@LCL
D=D+M
@R13
M=D
@SP
A=M
A=A-1
D=M
@SP
M=M-1
@R13
A=M
M=D
@0
D=A
@ARG
D=D+M
A=D
D=M
@SP
A=M
M=D
@SP
M=M+1
@1
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
A=M
A=A-1
D=M
A=A-1
M=M-D
@SP
M=M-1
@0
D=A
@ARG
D=D+M
@R13
M=D
@SP
A=M
A=A-1
D=M
@SP
M=M-1
@R13
A=M
M=D
@0
D=A
@ARG
D=D+M
A=D
D=M
@SP
A=M
M=D
@SP
M=M+1
@SP
A=M
A=A-1
D=M
@SP
M=M-1
@end_LOOP_START
D;JEQ
@LOOP_START
0;JMP
(end_LOOP_START)
@0
D=A
@LCL
D=D+M
A=D
D=M
@SP
A=M
M=D
@SP
M=M+1
