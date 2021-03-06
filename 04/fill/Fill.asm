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

(LOOP)
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

(WHITEOUT)
    // break if address = SCREEN + screensize
    @screensize
    D=M
    @i
    D=M-D
    @LOOP
    D;JEQ

    // set zero
    @address
    D=M
    A=D
    M=0

    // update address
    @address
    M=M+1

    // update loop count
    @i
    M=M+1

    // loop
    @WHITEOUT
    0;JMP

(BLACKOUT)
    // break if address = SCREEN + screensize
    @screensize
    D=M
    @i
    D=M-D
    @LOOP
    D;JEQ

    // set one
    @address
    D=M
    A=D
    M=!M

    // update address
    @address
    M=M+1

    // update loop count
    @i
    M=M+1

    // loop
    @BLACKOUT
    0;JMP