@17
D=A
@SP
A=M
M=D
@SP
M=M+1
@17
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
D=M-D
M=0
@BOOL0
D;JEQ
@ENDBOOL0
0;JMP
(BOOL0)
@SP
A=M
A=A-1
A=A-1
M=-1
@ENDBOOL0
0;JMP
(ENDBOOL0)
@SP
M=M-1
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
@16
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
D=M-D
M=0
@BOOL1
D;JEQ
@ENDBOOL1
0;JMP
(BOOL1)
@SP
A=M
A=A-1
A=A-1
M=-1
@ENDBOOL1
0;JMP
(ENDBOOL1)
@SP
M=M-1
@16
D=A
@SP
A=M
M=D
@SP
M=M+1
@17
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
D=M-D
M=0
@BOOL2
D;JEQ
@ENDBOOL2
0;JMP
(BOOL2)
@SP
A=M
A=A-1
A=A-1
M=-1
@ENDBOOL2
0;JMP
(ENDBOOL2)
@SP
M=M-1
@892
D=A
@SP
A=M
M=D
@SP
M=M+1
@891
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
D=M-D
M=0
@BOOL3
D;JLT
@ENDBOOL3
0;JMP
(BOOL3)
@SP
A=M
A=A-1
A=A-1
M=-1
@ENDBOOL3
0;JMP
(ENDBOOL3)
@SP
M=M-1
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
@892
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
D=M-D
M=0
@BOOL4
D;JLT
@ENDBOOL4
0;JMP
(BOOL4)
@SP
A=M
A=A-1
A=A-1
M=-1
@ENDBOOL4
0;JMP
(ENDBOOL4)
@SP
M=M-1
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
@891
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
D=M-D
M=0
@BOOL5
D;JLT
@ENDBOOL5
0;JMP
(BOOL5)
@SP
A=M
A=A-1
A=A-1
M=-1
@ENDBOOL5
0;JMP
(ENDBOOL5)
@SP
M=M-1
@32767
D=A
@SP
A=M
M=D
@SP
M=M+1
@32766
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
D=M-D
M=0
@BOOL6
D;JGT
@ENDBOOL6
0;JMP
(BOOL6)
@SP
A=M
A=A-1
A=A-1
M=-1
@ENDBOOL6
0;JMP
(ENDBOOL6)
@SP
M=M-1
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
@32767
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
D=M-D
M=0
@BOOL7
D;JGT
@ENDBOOL7
0;JMP
(BOOL7)
@SP
A=M
A=A-1
A=A-1
M=-1
@ENDBOOL7
0;JMP
(ENDBOOL7)
@SP
M=M-1
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
@32766
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
D=M-D
M=0
@BOOL8
D;JGT
@ENDBOOL8
0;JMP
(BOOL8)
@SP
A=M
A=A-1
A=A-1
M=-1
@ENDBOOL8
0;JMP
(ENDBOOL8)
@SP
M=M-1
@57
D=A
@SP
A=M
M=D
@SP
M=M+1
@31
D=A
@SP
A=M
M=D
@SP
M=M+1
@53
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
M=M+D
@SP
M=M-1
@112
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
@SP
A=M
A=A-1
M=-M
@SP
A=M
A=A-1
D=M
A=A-1
M=D&M
@SP
M=M-1
@82
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
M=D|M
@SP
M=M-1
@SP
A=M
A=A-1
M=!M
