from CnkiSpider import AuthorSpider

cas = AuthorSpider("钟南山")
author_name, author_code, institution = cas.author_recommend()
print(cas.name,cas.code,cas.institution)
cas.get_all_article()

# author_name = '王红宁'
# author_code = '000039348927'
# institution = '四川大学'

# cas = AuthorSpider(author_name, author_code, institution)
# cas.get_all_article()