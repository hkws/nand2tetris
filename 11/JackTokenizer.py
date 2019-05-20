# -*- coding: utf-8 -*-
import re
from JackSyntax import SYNTAX, RESERVED_TOKENS, USER_TOKENS


def revealToken(token, type):
    conv = {"<": "&lt;", ">": "&gt;", "&": "&amp;"}
    # if token in conv:
    #     return conv[token]
    if type == "stringConstant":
        return token[1:-1]
    return token

class JackTokenizer():

    COMMENT = r"/\*[\s\S]*?\*/|//.*"

    def __init__(self, filepath):
        with open(filepath, 'r') as fp:
            data = fp.read()
        self.tokens = self._tokenize(data)
        print(self.tokens)
        self.curr_index = None
        self.curr_token = ""
        self.curr_type = ""

    def _shape(self, data):
        # コメントを空白文字にreplace
        data = re.sub(self.COMMENT, ' ', data)
        # 改行を空白文字にreplace
        data = data.replace('\n', ' ')
        # 複数の空白文字を一つにreplace
        data = re.sub('\s+', ' ', data)
        # 前後の空白を除去
        data = data.strip()
        return data
    
    def _tokenize(self, data):
        data = self._shape(data)
        tokens = []
        buf = ""
        for char in data:
            if '"' in buf: # double quoteの内部では予約語とか無視
                buf = buf + char
                if char == '"': # "hoge fuga" のとき 
                    tokens.append(buf)
                    buf = ""
                continue

            # spaceの場合、bufに入っているtokenをtokensに格納
            if char == " ":
                if buf != "":
                    tokens.append(buf)
                    buf = ""
                continue

            # 一文字tokenの場合、bufがあったらそれをtokenに入れた上でcharもtokenに
            if char in RESERVED_TOKENS["symbol"]:
                if buf != "":
                    tokens.append(buf)
                    buf = ""
                tokens.append(char)
                continue
            buf = buf + char
        return tokens

    def hasMoreTokens(self):
        if self.curr_index is None:
            return True
        if len(self.tokens) <= self.curr_index + 1:
            return False
        return True
    
    def advance(self):
        if not self.hasMoreTokens():
            raise NoTokenError()
        if self.curr_index is None:
            self.curr_index = 0
        else:
            self.curr_index = self.curr_index + 1
        self.curr_token = self.tokens[self.curr_index]
        self.curr_type = self._token_type()
    
    def setIndex(self, index):
        self.curr_index = index
        self.curr_token = self.tokens[self.curr_index]
        self.curr_type = self._token_type()

    def _token_type(self):
        for k, v in RESERVED_TOKENS.items():
            if self.curr_token in v:
                return k
        
        for k, v in USER_TOKENS.items():
            if re.match(v, self.curr_token):
                return k
        raise Exception("Unknown token type: {}({})".format(self.curr_token, self.curr_index))
    
    @property
    def tokenType(self):
        return self.curr_type
    
    @property
    def token(self):
        return self.curr_token

    @property
    def keyWord(self):
        if self.curr_type != "keyword":
            raise Exception("The current token is not keyword: {}".format(self.curr_token))
        return self.curr_token
    
    @property
    def symbol(self):
        if self.curr_type != "symbol":
            raise Exception("The current token is not symbol: {}".format(self.curr_token))
        return self.curr_token
    
    @property
    def identifier(self):
        if self.curr_type != "identifier":
            raise Exception("The current token is not identifier: {}".format(self.curr_token))
        return self.curr_token
    
    @property
    def integerConstant(self):
        if self.curr_type != "integerConstant":
            raise Exception("The current token is not integerConstant: {}".format(self.curr_token))
        return self.curr_token
    
    @property
    def stringConstant(self):
        if self.curr_type != "stringConstant":
            raise Exception("The current token is not stringConstant: {}".format(self.curr_token))
        return self.curr_token


class NoTokenError(Exception):
    pass