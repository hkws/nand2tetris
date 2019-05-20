# -*- coding: utf-8 -*-
from JackTokenizer import JackTokenizer
from CompilationEngine import CompilationEngine
import sys, re, json, glob
import pathlib

def main():
    if len(sys.argv) != 2:
        print(".vm file directory is required.")
        return
    
    sourcePath = str(pathlib.Path(sys.argv[1]).resolve())
    dirname = sys.argv[1].split('/')[-1]
    sourceFiles = glob.glob(sourcePath+'/*.jack')
    destinationFiles = sourcePath+''

    for sFile in sourceFiles:
        destinationFileName = sFile.split('/')[-1].split('.')[0]
        dxmlFile = sourcePath+'/'+destinationFileName+'_compiled11.xml'
        dvmFile = sourcePath+'/'+destinationFileName+'.vm'
        tokenizer = JackTokenizer(sFile)
        input()
        compiler = CompilationEngine(tokenizer, dxmlFile, dvmFile)
        compiler.compile()

    return

"""
        with open(dFile, 'w') as df:
            df.write('<tokens>\n')
            while(tokenizer.hasMoreTokens()):
                tokenizer.advance()
                token = tokenizer.tokenForXml
                typ = tokenizer.tokenType
                df.write('<{}> {} </{}>\n'.format(typ, token, typ))
            df.write('</tokens>')
"""


if __name__ == '__main__':
    main()