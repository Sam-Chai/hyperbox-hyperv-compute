import ast
import json


def trans_str_to_list(string):
    return ast.literal_eval(string)


def trans_dict_to_json(dic):
    return json.dumps(dic)


def trans_json_to_dict(json_str):
    return json.loads(json_str)

