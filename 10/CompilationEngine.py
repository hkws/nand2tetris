# -*- coding: utf-8 -*-
import re, sys
from JackTokenizer import NoTokenError, tokenForXml
from JackSyntax import SYNTAX, RESERVED_TOKENS, USER_TOKENS, RESERVED_TOKEN_LIST
import xml.dom.minidom

def dict2xml(d):
    elements = []
    for k, v in d.items():
        if isinstance(v, list):
            v = list2xml(v)
        elif isinstance(v, dict):
            v = dict2xml(v)
        elements.append("<{key}> {value} </{key}>".format(key=k, value=v))
    return "".join(elements)


def list2xml(l):
    elements = []
    for i in l:
        if not isinstance(i, dict):
            raise Exception("Invalid data structure")
        parsed = dict2xml(i)
        elements.extend(parsed)
    return "".join(elements)


class CompilationEngine():

    def __init__(self, tokenizer, output):
        self.tokenizer = tokenizer
        self.output = output
    
    def compile(self):
        self.fp = open(self.output, 'w')
        codes = self._compile('class') # Jackは必ずclassからはじまる
        xml = self._convert_to_xml(codes)
        self.fp.write(xml)
        self.fp.close()

    def _convert_to_xml(self, parsed_list):
        sfied = list2xml(parsed_list).encode('utf-8')
        # print(sfied)
        dom = xml.dom.minidom.parseString(sfied)
        pretty_xml_str = dom.toprettyxml()
        cleaned = []
        # 1行目のxmlversionの記述を除去
        # 空行を除去
        for line in pretty_xml_str.split("\n"):
            if '?xml' in line:
                continue
            if line.strip() == "":
                continue
            cleaned.append(line)
        return "\n".join(cleaned)

    def _load_token(self):
        self.tokenizer.advance()
        return self.tokenizer.token

    def _set_checkpoint(self):
        checkpoint = self.tokenizer.curr_index if self.tokenizer.curr_index is not None else 0
        print("new checkpoint is {}".format(checkpoint))
        return checkpoint
                    
    def _compile_reserved(self, component):
        checkpoint = self.tokenizer.curr_index if self.tokenizer.curr_index is not None else 0
        token = self._load_token()
        for tokentype, resv_tokens in RESERVED_TOKENS.items():
            if component in resv_tokens and component == token:
                print("### compiled reserved word!!!")
                print([{tokentype: token}])
                # input()
                return [{tokentype: tokenForXml(token, tokentype)}]
        print("!!!reserved word compile failed!!!")
        print(component)
        print("token: "+token)
        self.tokenizer.setIndex(checkpoint)
        raise TokenUnmatchError() 

    def _compile_user_token(self, component):
        checkpoint = self.tokenizer.curr_index if self.tokenizer.curr_index is not None else 0
        token = self._load_token()
        for tokentype, regex in USER_TOKENS.items():
            if re.match(regex, token):
                print("### compiled user token!!!")
                print([{tokentype: token}])
                # input()
                return [{tokentype: tokenForXml(token, tokentype)}]
        print("!!!user token compile failed!!!")
        print(component)
        print("token: "+token)
        self.tokenizer.setIndex(checkpoint)
        raise TokenUnmatchError()

    def _compile(self, component):
        print("### start compiling ###")
        print(component)
        def _exec_compile(component):
            logic = component["logic"] if "logic" in component else "and"
            if logic == "and":
                return self._and(component["components"])
            elif logic == "or":
                return self._or(component["components"])
            else:
                raise Exception("Invalid logic: {}".format(logic))

        key = None
        if isinstance(component, str):
            key = component
            component = SYNTAX[component]

        bodies = []
        isMulti = "multiple" in component and component["multiple"]
        isBinary = "binary" in component and component["binary"]
        try:             
            if isMulti:
                while(True):
                    checkpoint = self._set_checkpoint()
                    body = _exec_compile(component)
                    bodies.extend(body)
            elif isBinary:
                checkpoint = self._set_checkpoint()
                body = _exec_compile(component) # returns [] when _exec_compile raise TokenUnmatchError
                bodies = body
            else:
                checkpoint = self._set_checkpoint()
                bodies = _exec_compile(component)
        except (NoTokenError, TokenUnmatchError) as e:
            print("############################")
            print("SET INDEX")
            print("from {} to {}".format(self.tokenizer.curr_token, self.tokenizer.tokens[checkpoint]))
            self.tokenizer.setIndex(checkpoint)
            if not (isMulti or isBinary):
                raise e

        wrap = component["wrapped"] if "wrapped" in component else True
        return [{key: bodies}] if (key is not None) and wrap else bodies

    def _compile_token(self, component):
        body = []
        if component in RESERVED_TOKEN_LIST:
            body = self._compile_reserved(component)
        elif isinstance(component, dict) or component in SYNTAX.keys():
            body = self._compile(component)
        elif component in USER_TOKENS.keys():
            body = self._compile_user_token(component)
        else:
            raise Exception("Invalid component: {} ".format(component))
        return body

    def _and(self, components):
        bodies = []
        # componentsの順番通りにtokenがpopできるはず
        # componentsすべてに渡ってcompileが成功するはず
        # 一度でも失敗したらraise
        for component in components:
            body = self._compile_token(component)
            bodies.extend(body)
        return bodies

    def _or(self, components):
        # componentsのうちのいずれかがtokenを満たすはず
        # compileに失敗した場合、catchして次の候補をcompileしにいく
        # すべてのcomponentで失敗したら raise
        for component in components:
            try:
                body = self._compile_token(component)
                if body:
                    return body
            except TokenUnmatchError as e:
                pass
        raise TokenUnmatchError()


class TokenUnmatchError(Exception):
    pass

    # def compileClass(self):
    #     """
    #     logic: andのとき
    #         componentsをloopしてそれぞれcompile
    #         compileしたものすべてをlistにしてreturn
    #     logic: orのとき
    #         まずtokenをload
    #         componentsのいずれかにtokenがmatchすることを確認
    #         matchしたtokenをreturn
    #     multiple: trueのとき
    #         logicに応じて、上記and/orのときの処理を実行
    #         戻り値はlistにどんどん連結
    #         matchしなくなったら終了、listをreturn
    #     binary: trueのとき
    #         logicに応じて、上記and/orのときの処理を実行
    #         returnがあれば返却、なくてもよい
    #     codes = {"class": []}
    #     tokenを読み込む
    #     token_typeを判別する
    #     if type is keyword or symbol -> compileしてcodes["class"].append()
    #     戻り値：dict
    #     """
    #     syntax = SYNTAX["class"]
    #     logic = syntax["logic"] if "logic" in syntax else "and"
    #     codes = {"class": []}
    #     if logic == "and":

    #     elif logic == "or":

    #     return codes
