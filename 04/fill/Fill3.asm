// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.

@8192
D=A
@screensize
M=D
@colorbefore
M=0
@colorafter
M=0

(LOOP)
    // update color
    @colorafter
    D=M
    @colorbefore
    M=D

    // initialize pointer
    @SCREEN
    D=A
    @address
    M=D    
    @i
    M=0

    // detect keyboard input
    @KBD
    D=M

    @BLACKOUT
    D;JNE

    @WHITEOUT
    D;JEQ 

    @LOOP
    0;JMP

(BLACKOUT)
    @colorbefore
    D=M
    @colorafter
    M=-1
    D=D-M

    @CHANGESCREEN
    D;JNE

    @LOOP
    0;JMP

(WHITEOUT)
    @colorbefore
    D=M
    @colorafter
    M=0

    @CHANGESCREEN
    D;JNE

    @LOOP
    0;JMP

(CHANGESCREEN)
    // loop finish if address = SCREEN + screensize
    @screensize
    D=M
    @i
    D=M-D
    @LOOP
    D;JEQ

    // set zero
    @colorafter
    D=M
    @address
    A=M
    M=D

    // update address
    @address
    M=M+1

    // update loop count
    @i
    M=M+1

    // loop
    @CHANGESCREEN
    0;JMP
