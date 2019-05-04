# -*- coding: utf-8 -*-
from Parser import Parser
from CodeWriter import CodeWriter
import sys, re, json, glob
import pathlib

def main():
    if len(sys.argv) != 2:
        print(".vm file directory is required.")
        return
    
    sourcePath = str(pathlib.Path(sys.argv[1]).resolve())
    dirname = sys.argv[1].split('/')[-1]
    destinationPath = sourcePath+'/'+dirname+'.asm'
    sourceFiles = glob.glob(sourcePath+'/*.vm')

    with CodeWriter(destinationPath) as writer:
        for sfile in sourceFiles:
            filename = sfile.split('/')[-1].split('.')[0]
            parser = Parser(sfile)
            writer.setFileName(filename)
            while(parser.hasMoreCommands()):
                parser.advance()
                cmdType = parser.commandType
                cmds = parser.parsedCommand
                getattr(writer, 'write_'+cmdType)(**cmds)

    return


if __name__ == '__main__':
    main()