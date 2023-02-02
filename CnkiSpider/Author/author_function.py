"""
这里存放一些重复使用较多的函数
"""
import re

def QueryJson_choice(mode,name,code,institution):
    if mode == 0:
        QueryJson = {
            "Platform": "",
            "DBCode": "CFLS",
            "KuaKuCode":
            "CJFQ,CCND,CIPD,CDMD,BDZK,CISD,SNAD,CCJD,GXDB_SECTION,CJFN,CCVD",
            "QNode": {
                "QGroup": [{
                    "Key":
                    "Subject",
                    "Title":
                    "",
                    "Logic":
                    1,
                    "Items": [],
                    "ChildItems": [{
                        "Key":
                        "",
                        "Title":
                        "作者",
                        "Logic":
                        1,
                        "Items": [{
                            "Key":
                            "",
                            "Title":
                            "{}（{}）".format(name, institution),
                            "Logic":
                            1,
                            "Name":
                            "AUC",
                            "Operate":
                            "=",
                            "Value":
                            "{}".format(code),
                            "ExtendType":
                            13,
                            "ExtendValue":
                            "",
                            "Value2":
                            "",
                            "BlurType":
                            ""
                        }, {
                            "Key":
                            "",
                            "Title":
                            "{}（{}）".format(name, institution),
                            "Logic":
                            1,
                            "Name":
                            "AU",
                            "Operate":
                            "=",
                            "Value":
                            "{}".format(name),
                            "ExtendType":
                            13,
                            "ExtendValue":
                            "",
                            "Value2":
                            "",
                            "BlurType":
                            ""
                        }],
                        "ChildItems": []
                    }]
                }]
            },
            "CodeLang": "ch"
        }
    elif mode == 1:
        QueryJson = {
            "Platform": "",
            "DBCode": "CFLS",
            "KuaKuCode":
            "CJFQ,CDMD,CIPD,CCND,CISD,SNAD,BDZK,CCJD,CCVD,CJFN",
            "QNode": {
                "QGroup": [{
                    "Key":
                    "Subject",
                    "Title":
                    "",
                    "Logic":
                    1,
                    "Items": [],
                    "ChildItems": [{
                        "Key":
                        "",
                        "Title":
                        "作者",
                        "Logic":
                        1,
                        "Items": [{
                            "Key":
                            "",
                            "Title":
                            "{}（{}）".format(name, institution),
                            "Logic":
                            1,
                            "Name":
                            "AUC",
                            "Operate":
                            "=",
                            "Value":
                            "{}".format(code),
                            "ExtendType":
                            13,
                            "ExtendValue":
                            "",
                            "Value2":
                            "",
                            "BlurType":
                            ""
                        }, {
                            "Key":
                            "",
                            "Title":
                            "{}（{}）".format(name, institution),
                            "Logic":
                            1,
                            "Name":
                            "AU",
                            "Operate":
                            "=",
                            "Value":
                            "{}".format(name),
                            "ExtendType":
                            13,
                            "ExtendValue":
                            "",
                            "Value2":
                            "",
                            "BlurType":
                            ""
                        }],
                        "ChildItems": []
                    }]
                }]
            },
            "CodeLang": "ch"
        }
    else:
        print('模式错误')
        QueryJson = ''
    return str(QueryJson)

def get_SearchSql(text):
    pattern = r'<input id="sqlVal" type="hidden" value="(.*?)" />'
    result = re.findall(pattern, text)
    return str(result[0])