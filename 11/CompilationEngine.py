# -*- coding: utf-8 -*-
import re, sys, copy, json
from inspect import isfunction
from JackTokenizer import NoTokenError, revealToken
from JackSyntax import SYNTAX, SYMBOL, RESERVED_TOKENS, USER_TOKENS, RESERVED_TOKEN_LIST
from SymbolTable import SymbolTable
from VMWriter import VMWriter
import xml.dom.minidom

TOKENXML = True

def tokenForXml(token, type):
    conv = {"<": "&lt;", ">": "&gt;", "&": "&amp;"}
    if token in conv:
        return conv[token]
    return token

def dict2xml(d):
    elements = []
    for k, v in d.items():
        if isinstance(v, list):
            v = list2xml(v)
        elif isinstance(v, dict):
            v = dict2xml(v)
        else:
            v = tokenForXml(v, k)
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

    def __init__(self, tokenizer, xml_output, vm_output):
        self.tokenizer = tokenizer
        self.xml_output = xml_output
        self.vmw = VMWriter(vm_output)
        self.symbolTable = SymbolTable()
    
    def compile(self):
        codes = self._compile('class') # Jackは必ずclassからはじまる
        if TOKENXML:
            self.fp = open(self.xml_output, 'w')
            xml = self._convert_to_xml(codes)
            self.fp.write(xml)
            self.fp.close()
        self.vmw.convertClass(codes)
        self.vmw.close()

    def _convert_to_xml(self, parsed_list):
        sfied = list2xml(parsed_list).encode('utf-8')
        # print(sfied)
        dom = xml.dom.minidom.parseString(sfied)
        pretty_xml_str = dom.toprettyxml()
        cleaned = []
        # TextComparer.shのための微修正
        # 1行目のxmlversionの記述を除去
        # 空行を除去
        # expressionList, parameterListは中に改行を入れる
        for line in pretty_xml_str.split("\n"):
            if '?xml' in line:
                continue
            if line.strip() == "":
                continue
            if ("expressionList" in line or "parameterList" in line) and ">  <" in line:
                tag = "expressionList" if "expressionList" in line else "parameterList"
                idx = line.find("<")
                cleaned.append(line[:idx] + "<{}>".format(tag))
                cleaned.append(line[:idx] + "</{}>".format(tag))
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
    
    def _copy_symbol_table(self):
        return copy.deepcopy(self.symbolTable)
    
    def _restore_symbol_table(self, target):
        self.symbolTable = target
                    
    def _compile_reserved(self, component):
        checkpoint = self.tokenizer.curr_index if self.tokenizer.curr_index is not None else 0
        token = self._load_token()
        for tokentype, resv_tokens in RESERVED_TOKENS.items():
            if component in resv_tokens and component == token:
                print("### compiled reserved word!!!")
                print([{tokentype: token}])
                # input()
                return [{tokentype: revealToken(token, tokentype)}]
        print("!!!reserved word compile failed!!!")
        print(component)
        print("token: "+token)
        self.tokenizer.setIndex(checkpoint)
        raise TokenUnmatchError() 

    def _compile_user_token(self, component):
        checkpoint = self.tokenizer.curr_index if self.tokenizer.curr_index is not None else 0
        token = self._load_token()
        for tokentype, regex in USER_TOKENS.items():
            if component == tokentype and re.match(regex, token):
                print("### compiled user token!!!")
                print([{tokentype: token}])
                # input()
                if tokentype == "identifier":
                    return [{tokentype: {"name": revealToken(token, tokentype)}}]
                return [{tokentype: revealToken(token, tokentype)}]
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
        
        if key is not None and key in SYMBOL["preprocess_targets"]:
            for proc in SYMBOL["preprocess"]:
                if key != proc["target"]:
                    continue
                try:
                    getattr(self.symbolTable, proc["func"])(key)
                except Exception as e:
                    print("##################################")
                    print("######## preprocess error ########")
                    print("##################################")
                    print("key: {}".format(key))
                    raise e

        bodies = []
        isMulti = "multiple" in component and component["multiple"]
        isBinary = "binary" in component and component["binary"]
        try:             
            if isMulti:
                while(True):
                    checkpoint = self._set_checkpoint()
                    savedSymbolTable = self._copy_symbol_table()
                    body = _exec_compile(component)
                    bodies.extend(body)
            elif isBinary:
                checkpoint = self._set_checkpoint()
                savedSymbolTable = self._copy_symbol_table()
                body = _exec_compile(component) # returns [] when _exec_compile raise TokenUnmatchError
                bodies = body
            else:
                checkpoint = self._set_checkpoint()
                savedSymbolTable = self._copy_symbol_table()
                bodies = _exec_compile(component)
        except (NoTokenError, TokenUnmatchError) as e:
            print("############################")
            print("SET INDEX")
            print("from {} to {}".format(self.tokenizer.curr_token, self.tokenizer.tokens[checkpoint]))
            self.tokenizer.setIndex(checkpoint)
            self._restore_symbol_table(savedSymbolTable)
            if not (isMulti or isBinary):
                raise e

        # ここまできたら、bodiesの中身についてはcomponent通りparseできたことを意味する
        # なので、symbolTableを更新して良い
        print("### finished compiling {} ###".format(str(component)))
        print(bodies)

        #if key is not None and key in SYMBOL["postprocess_targets"]:
        for proc in SYMBOL["postprocess"]:
            if isfunction(proc["target"]):
                if not proc["target"](bodies): continue
            elif isinstance(proc["target"], str):
                if key != proc["target"]: continue
            try:
                bodies = getattr(self.symbolTable, proc["func"])(bodies=bodies, key=proc["target"])
            except Exception as e:
                print("##################################")
                print("####### postprocess error ########")
                print("##################################")
                print("key: {}".format(key))
                print("bodies: {}".format(json.dumps(bodies, indent=2)))
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
