"""
这里存放一些重复使用较多的函数
"""
import re


def QueryJson_choice(mode, search_content,Item,code='',institution=''):
    if mode in ['AU','FI','RP']:
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
                        Item[0],
                        "Logic":
                        1,
                        "Items": [{
                            "Key":
                            "",
                            "Title":
                            "{}（{}）".format(search_content, institution),
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
                            "{}（{}）".format(search_content, institution),
                            "Logic":
                            1,
                            "Name":
                            Item[1],
                            "Operate":
                            "=",
                            "Value":
                            "{}".format(search_content),
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
        QueryJson = {
            "Platform": "",
            "DBCode": "CFLS",
            "KuaKuCode": "CJFQ,CDMD,CIPD,CCND,CISD,SNAD,BDZK,CCJD,CCVD,CJFN",
            "QNode": {
                "QGroup": [{
                    "Key":
                    "Subject",
                    "Title":
                    "",
                    "Logic":
                    1,
                    "Items": [{
                        "Title": Item[0],
                        "Name": Item[1],
                        "Value": "{}".format(search_content),
                        "Operate": Item[2],
                        "BlurType": Item[3]
                    }],
                    "ChildItems": []
                }]
            },
            "CodeLang": "ch"
        }
    return str(QueryJson)


def get_SearchSql(text):
    pattern = r'<input id="sqlVal" type="hidden" value="(.*?)" />'
    result = re.findall(pattern, text)
    return str(result[0])
