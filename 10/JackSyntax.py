# -*- coding: utf-8 -*-

# TOKENS = [
#     {"type": "keyword",
#      "pattern": ["class", "constructor", "function", "method", "field",
#                 "static", "var", "int", "char", "boolean",
#                 "void", "true", "false", "null", "this",
#                 "let", "do", "if", "else", "while", "return"]},
#     {"type": "symbol",
#      "pattern": ["{", "}", "(", ")", "[", "]", ".", ",",
#                  ";", "+", "-", "*", "/", "&", "|", "<",
#                  ">", "=", "~"]},
#     {"type": "integerConstant",
#      "pattern": "[0-9]{1,5}"},
#     {"type": "stringConstant",
#      "pattern": "\"[^\"\n]+\""},
#     {"type": "identifier",
#      "pattern": "[a-zA-Z0-9]+"}
# ]
# SINGLE_TOKENS = TOKENS[0]["pattern"] + TOKENS[1]["pattern"]

RESERVED_TOKENS = {
    "keyword": ["class", "constructor", "function", "method", "field",
                "static", "var", "int", "char", "boolean",
                "void", "true", "false", "null", "this",
                "let", "do", "if", "else", "while", "return"],
    "symbol": ["{", "}", "(", ")", "[", "]", ".", ",",
                 ";", "+", "-", "*", "/", "&", "|", "<",
                 ">", "=", "~"]
}

RESERVED_TOKEN_LIST = RESERVED_TOKENS["keyword"] + RESERVED_TOKENS["symbol"]

USER_TOKENS = {
    "integerConstant": "[0-9]{1,5}",
    "stringConstant": "\"[^\"\n]+\"",
    "identifier": "[a-zA-Z0-9]+"
}

###
### syntax object
###
# {
#     "logic": "and", # enum: [and, or], default: and
#     "multiple": False, # denotes '*', boolean, default: false
#     "binary": False, # denotes '?', boolean, default: false
#     "components": [...], # if logic is and, this type is composed of all of these types [...]
#                         # else, this type is composed of one of these types [...]
#                         # required
#     "wrapped": True # whether the returned list is wrapped by the key named type name, default true  
#                     # This key is valid when the type is not terminal
# }
# NOTE: When the logic is or, components is evaluated in the list order.
#       You must give small index to the 'strict' candidate.

SYNTAX = {
    "class": {
        "logic": "and",
        "components": [
            "class",
            "className",
            "{",
            {"components": ["classVarDec"],
             "multiple": True},
            {"components": ["subroutineDec"],
             "multiple": True},
            "}"
        ]
    },
    "classVarDec": {
        "logic": "and",
        "components": [
            {"logic": "or",
             "components": ["static", "field"]},
             "type",
             "varName",
            {"logic": "and",
             "components": [",", "varName"],
             "multiple": True},
             ";"
        ]
    },
    "type": {
        "logic": "or",
        "wrapped": False,
        "components": [
            "int",
            "char",
            "boolean",
            "className"
        ]
    },
    "subroutineDec": {
        "logic": "and",
        "components":[
            {"logic": "or",
            "components": ["constructor", "function", "method"]},
            {"logic": "or",
            "components": ["void", "type"]},
            "subroutineName",
            "(",
            "parameterList",
            ")",
            "subroutineBody"
        ]
    },
    "parameterList": {
        "logic": "and",
        "binary": True,
        "components": [
            {"logic": "and",
             "components": ["type", "varName"]},
            {"logic": "and",
             "multiple": True,
             "components": [",", "type", "varName"]}
        ]
    },
    "subroutineBody": {
        "logic": "and",
        "components": [
            "{",
            {"components":["varDec"],
             "multiple": True},
            "statements",
            "}"
        ]
    },
    "varDec": {
        "logic": "and",
        "components": [
            "var",
            "type",
            "varName",
            {"logic": "and",
             "components": [",", "varName"],
             "multiple": True},
            ";"
        ]
    },
    "className": {
        "wrapped": False,
        "components": [
            "identifier"
        ]
    },
    "subroutineName": {
        "wrapped": False,
        "components": [
            "identifier"
        ]
    },
    "varName": {
        "wrapped": False,
        "components": [
            "identifier"
        ]
    },
    "statements": {
        "multiple": True,
        "components": [
            "statement"
        ]
    },
    "statement": {
        "wrapped": False,
        "logic": "or",
        "components": [
            "letStatement",
            "ifStatement",
            "whileStatement",
            "doStatement",
            "returnStatement"
        ]
    },
    "letStatement": {
        "logic": "and",
        "components": [
            "let",
            "varName",
            {"logic": "and",
             "components": ["[", "expression", "]"],
             "binary": True},
            "=",
            "expression",
            ";"
        ]
    },
    "ifStatement": {
        "logic": "and",
        "components": [
            "if",
            "(",
            "expression",
            ")",
            "{",
            "statements",
            "}",
            {"logic": "and",
             "components": ["else", "{", "statements", "}"],
             "binary": True}
        ]
    },
    "whileStatement": {
        "logic": "and",
        "components": [
            "while",
            "(",
            "expression",
            ")",
            "{",
            "statements",
            "}"
        ]
    },
    "doStatement": {
        "logic": "and",
        "components": [
            "do",
            "subroutineCall",
            ";"
        ]
    },
    "returnStatement": {
        "logic": "and",
        "components": [
            "return",
            {"components": ["expression"],
             "binary": True},
            ";"
        ]
    },
    "expression": {
        "logic": "and",
        "components": [
            "term",
            {"logic": "and",
             "components": ["op", "term"],
             "multiple": True}
        ]
    },
    "term": {
        "logic": "or",
        "components": [
            "subroutineCall",
            {"logic": "and",
             "components": ["varName", "[", "expression", "]"]},
            {"logic": "and",
             "components": ["(", "expression", ")"]},
            {"logic": "and",
             "components": ["unaryOp", "term"]},
            "keywordConstant",
            "integerConstant",
            "stringConstant",
            "varName"
        ]
    },
    "subroutineCall": {
        "wrapped": False,
        "logic": "or",
        "components": [
            {"logic": "and",
             "components": ["subroutineName", "(", "expressionList", ")"]},
            {"logic": "and",
             "components": [
                 {"logic": "or",
                  "components": ["className", "varName"]},
                ".",
                "subroutineName",
                "(",
                "expressionList",
                ")"
             ]}
        ]
    },
    "expressionList": {
        "logic": "and",
        "binary": True,
        "components": [
            "expression",
            {"logic": "and",
             "components": [",", "expression"],
             "multiple": True}
        ]
    },
    "op": {
        "logic": "or",
        "components": ["+","-","*","/","&","|","<",">","="],
        "wrapped": False
    },
    "unaryOp":{
        "logic": "or",
        "components": ["-", "~"],
        "wrapped": False
    },
    "keywordConstant": {
        "logic": "or",
        "components": ["true", "false", "null", "this"],
        "wrapped": False
    }
}
