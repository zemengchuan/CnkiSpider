import requests
import re
import os
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from CnkiSpider.para import *
from CnkiSpider.function import *
from lxml import etree
import time


class CnkiSpider:
    """
    search_mode：搜索的模式，包括：[
        'SU'：主题, 
        'TKA'：篇关摘, 
        'KY'：关键词, 
        'TI'：篇名, 
        'FT'：全文, 
        'FU'：基金, 
        'AB'：摘要, 
        'CO'：小标题, 
        'RF'：参考文献, 
        'CLC'：分类号, 
        'LY'：文献来源, 
        'DOI'：DOI, 
        'AU'：作者, 
        'FI'：第一作者, 
        'RP'：通讯作者
        ]
    search_content：搜索内容
    author_code：作者代码
    institution：作者机构
    session：方便获取cookies
    __headers：请求头，可在para文件中设置default_headers
    __dic：对照表，可在para文件中设置para_dic
    path：文件保存路径设置，默认为当前工作目录下的搜索内容-搜索模式
    """
    def __init__(self, search_mode, search_content,author_code='', institution=''):
        self.__search_mode = search_mode
        self.__search_content = search_content
        self.session = requests.Session()
        self.__headers = default_headers
        self.__dic = para_dic
        self.path = f'./{self.__search_content}-{self.__search_mode}/'
        self.__SearchSql = ''
        self.__df = pd.DataFrame(data=None)
        self.__df_list = []
        self.__total_page = 0
        self.__check_para()
        self.__Item = search_mode_list[search_mode]
        if search_mode in ['AU','FI','RP']:
            if (author_code=='') | (institution==''):
                self.__author_recommend()
            else:
                self.__author_code = author_code
                self.__institution = institution
            self.__QueryJson = QueryJson_choice(
                mode=self.__search_mode, 
                search_content=self.__search_content,
                Item=self.__Item,
                code=self.__author_code,
                institution=self.__institution
            )
            self.info = {
                "search_content":self.__search_content,
                "search_mode":self.__search_mode,
                "file_path":self.path,
                "author_code":self.__author_code,
                "institution":self.__institution
            }
        else:
            self.__QueryJson = QueryJson_choice(
                mode=self.__search_mode, 
                search_content=self.__search_content,
                Item=self.__Item,
            )

    # 检查参数是否正确
    def __check_para(self):
        if not self.__search_mode in search_mode_list:
            raise Exception(f'The search mode is wrong, the correct mode include :{[i for i in search_mode_list]}')
    
    # 创建存放路径path
    def __creatpath(self):
        # self.path = f'./{self.__search_content}-{self.__search_mode}/'
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    """
    提供概览的功能
    """

    # 获取返回的json文件
    def __getjson(self):
        url = 'https://kns.cnki.net/kns8/Group/ResGroup'
        data = {
            'queryJson':
            self.__QueryJson,
            'handleid':
            "0"
        }
        text = self.session.post(url=url, data=data, headers=self.__headers)
        with open('json.txt','w',encoding='utf-8')as f:
            f.write(str(data))
        return text.json()

    # 概览
    def get_overview(self, save=True):
        text = self.__get_cookies()
        with open('info.txt','w',encoding='utf-8')as f:
            f.write(text)
        js = self.__getjson()
        dic = {'项目': [], '数量': []}
        for i in js:
            if i in self.__dic:
                dic['项目'].append(self.__dic[i])
                dic['数量'].append(js[i])
        df = pd.DataFrame(dic, columns=['项目', '数量'])
        if save:
            self.__creatpath()
            df.to_csv(f"{self.path}overview.csv")
        print(f"\"{self.__search_content}\"在知网上共有记录{dic['数量'][0]}条，详细情况如下：")
        for num in range(len(dic['数量'])):
            print(f"{dic['项目'][num]}:{dic['数量'][num]}篇")
        return dic

    """
    利用线程池的方式快速获取相关作者列表，顺序同知网上输入作者名称时出现的推荐
    """

    # 获取相关作者列表
    def __authorlist(self):
        AuthorName = []  # 作者名称
        AuthorCode = []  # 作者代码
        FirstInstitution = []  # 第一机构
        futures = []  # 存放线程池运行结果
        url = "https://kns.cnki.net/kns8/AdvSearch/AuthorRecommend"
        data = {'pageIndex': 1, 'authorName': self.__search_content}
        text = requests.post(url=url, data=data,
                                 headers=self.__headers).text
        page_pattern = r'"maxPageIndex":(\d+)'
        max_page = re.findall(page_pattern, text)[0]
        # 通过线程池快速获取作者列表的
        with ThreadPoolExecutor(10) as t:
            for page in range(0, int(max_page)):
                future = t.submit(self.__threadauthor,
                                  url=url,
                                  data=data,
                                  page=page + 1)
                futures.append(future)

        # 提取线程池运行结果
        for future in futures:
            result = future.result()
            AuthorName.extend(result[0])
            AuthorCode.extend(result[1])
            FirstInstitution.extend(result[2])
        return (AuthorName, AuthorCode, FirstInstitution)

    # 线程池
    def __threadauthor(self, url, data, page):
        data['pageIndex'] = page,
        text = requests.post(url=url, data=data).text
        AuthorName_pattern = r'"AuthorName":"(.*?)"'
        AuthorCode_pattern = r'"AuthorCode":"(.*?)"'
        FirstInstitution_pattern = r'"FirstInstitution":"(.*?)"'
        authorName = re.findall(AuthorName_pattern, text)
        authorCode = re.findall(AuthorCode_pattern, text)
        firstInstitution = re.findall(FirstInstitution_pattern, text)
        return authorName, authorCode, firstInstitution

    # 接收选择的函数
    def __choose(self, AuthorName, AuthorCode, FirstInstitution):
        #chose = '0'
        for i in range(10):
            chose = input("请选择需要查询的作者序号(输入exit退出，输入re再次获取)：")
            if chose.isdigit():
                chose = int(chose)
                if chose >= 0 and chose < len(AuthorName):
                    self.__author_code = str(AuthorCode[chose])
                    self.__institution = str(FirstInstitution[chose])
                    break
            elif chose == "exit":
                break
            elif chose == "re":
                AuthorName, AuthorCode, FirstInstitution = self.__authorlist()
                df = pd.DataFrame({"作者": AuthorName, "机构": FirstInstitution})
                pd.set_option('display.max_rows', None)
                print(df)
                continue
            else:
                pass
            if i == 9:
                print("错误次数过多，请再次运行程序")
            else:
                chose = input("您输入的内容不正确，请检查后再次输入：")

    # 整合相关作者信息输出，并接收用户的选择
    def __author_recommend(self):
        AuthorName, AuthorCode, FirstInstitution = self.__authorlist()
        df = pd.DataFrame({"作者": AuthorName, "机构": FirstInstitution})
        pd.set_option('display.max_rows', None)
        print(df)
        self.__choose(AuthorName, AuthorCode, FirstInstitution)
        return (self.__search_content, self.__author_code, self.__institution)


    """
    根据第一页的信息，多线程获取每一页的内容
    """

    def __get_cookies(self):
        url = "https://kns.cnki.net/kns8/Brief/GetGridTableHtml"
        data = {
            'IsSearch':
            'true',
            'QueryJson':
            self.__QueryJson,
            'PageName':
            'defaultresult',
            'DBCode':
            'CFLS',
            'KuaKuCodes':
            'CJFQ,CDMD,CIPD,CCND,CISD,SNAD,BDZK,CCJD,CCVD,CJFN',
            'CurPage':
            '1',
            'RecordsCntPerPage':
            '50',
            'CurDisplayMode':
            'listmode',
            'CurrSortField':
            'PT',
            'CurrSortFieldType':
            'desc',
            'IsSentenceSearch':
            'false',
            'CnkiSpider':
            ''
        }
        text = self.session.post(url=url, data=data,
                                 headers=self.__headers).text
        return text

    def __get_first_page(self):
        text = self.__get_cookies()
        self.__SearchSql = get_SearchSql(text)
        self.__get_total_page(text)
        self.check_list = list(range(self.__total_page))
        self.__df = self.__get_msg(text)
        self.__creatpath()
        self.__df.to_csv(f"{self.path}result.csv",index=False)

    # 获取总页数的函数
    def __get_total_page(self, text):
        result_pattern = r'共找到<em>(.*?)</em>条结果'
        total_result = re.findall(result_pattern, text)[0].replace(",","")
        print(f"一共有文章{total_result}篇")
        page_pattern = r"<span class='countPageMark'>1/(\d+)</span>"
        total_page = re.findall(page_pattern,text)[0]
        self.__total_page = int(total_page)

    # 获取标题、作者、日期和来源
    def __get_msg(self, text):
        html = etree.HTML(text)
        tr_list = html.xpath('//*[@id="gridTable"]/table/tr')
        titles = []
        authors = []
        dates = []
        sources = []
        links = []
        for tr in tr_list:
            title = tr.xpath('./td[@class="name"]')[0].xpath('string(.)').strip()
            link = 'https://kns.cnki.net' + tr.xpath(
                './td[@class="name"]/a/@href')[0].strip()
            author = tr.xpath('./td[@class="author"]')[0].xpath('string(.)').strip()
            date = tr.xpath('./td[@class="date"]/text()')[0].strip()
            source = tr.xpath('./td[@class="source"]')[0].xpath('string(.)').strip()
            titles.append(title)
            links.append(link)
            authors.append(author)
            dates.append(date)
            sources.append(source)
        dic = {
            "标题": self.__clean(titles),
            "作者": self.__clean(authors),
            "发表时间": self.__clean(dates),
            "来源": self.__clean(sources),
            "链接": self.__clean(links)
        }
        df = pd.DataFrame(dic)
        return df

    # 数据清洗，，去掉\r\n和tag
    def __clean(self, data_list):
        pattern = re.compile(r"(<.*?>)", re.S)
        for num in range(len(data_list)):
            data_list[num] = data_list[num].replace("\r",
                                                    "").replace("\n",
                                                                "").strip()
            if "<" in data_list[num]:
                tags = re.findall(pattern, data_list[num])
                for tag in tags:
                    data_list[num] = data_list[num].replace(tag, "")
        return data_list

    # 获取其他页面信息
    def __get_other_page_text(self, url, data, page):
        print(f"正在爬取第{page}页……")
        count = 3
        for i in range(count):
            if i==(count-1):
                print(f"第{page}页爬取失败，已跳过")
            text = requests.post(url=url,
                                data=data,
                                headers=self.__headers,
                                timeout=10).text
            try:
                other_df = self.__get_msg(text)
                if (page < self.__total_page) and (len(other_df) < 20):
                    with open('log_wrong.html','w',encoding='utf-8')as f:
                        f.write(text)
                    time.sleep(20)
                    # other_df.to_csv(f'./{page}.csv')
                    print(f"第{page}页数据有误，只有{len(other_df)}条，正在重新爬取……")
                    continue
                self.__df_list.append((page, other_df))
                # other_df.to_csv(f'{page}.csv')
                print(f'第{page}页爬取成功！第{page}页有{len(other_df)}条数据')
                break
            except:
                print(f"第{page}页爬取出错，正在重新爬取……")
                with open('log_mistake.html','w',encoding='utf-8')as f:
                    f.write(text)
                time.sleep(2)
                continue
            

    def __get_other_page(self, page):
        url = "https://kns.cnki.net/kns8/Brief/GetGridTableHtml"
        data = {
            'IsSearch':
            'false',
            'QueryJson':
            QueryJson_choice(mode=self.__search_mode,
                             search_content=self.__search_content,
                             Item=self.__Item),
            'SearchSql':
            self.__SearchSql,
            'HandlerId':
            '12',
            'PageName':
            'defaultresult',
            'DBCode':
            'CFLS',
            'KuaKuCodes':
            'CJFQ,CDMD,CIPD,CCND,CISD,SNAD,BDZK,CCJD,CCVD,CJFN',
            'CurPage':
            page,
            'RecordsCntPerPage':
            '50',
            'CurDisplayMode':
            'listmode',
            'CurrSortField':
            'PT',
            'CurrSortFieldType':
            'desc',
            'IsSortSearch':
            'false',
            'IsSentenceSearch':
            'false',
            'CnkiSpider':
            ''
        }
        self.__get_other_page_text(url=url, data=data, page=page)

    # 线程池爬取页面
    def get_result(self):
        self.__get_first_page()
        print(f'共需要爬取{self.__total_page}页')
        print('=' * 100)
        with ThreadPoolExecutor(20) as t:
            for page in range(2, self.__total_page + 1):
                t.submit(self.__get_other_page, page=page)
        # self.__creatpath()
        self.__df_list = sorted(self.__df_list)
        # print(len(self.df_list))
        for df in self.__df_list:
            df[1].to_csv(f"{self.path}result.csv",
                         mode='a',
                         header=False,
                         index=False)
        # self.df.to_csv(f"{self.path}result.csv")
        print("=" * 100)
        print(f"爬取完成，已将结果保存至{self.path}")
        # print(self.check_list)
        return self.__df


if __name__ == '__main__':
    search_mode = 'RP'
    author_code = '000039348927'
    institution = '四川大学'
    search_content = '王红宁'
    cs = CnkiSpider(search_mode=search_mode, search_content=search_content)
    # cs = CnkiSpider(
    #     search_mode=search_mode, 
    #     search_content=search_content,
    #     author_code=author_code,
    #     institution=institution)
    # print(f"作者代码是{cs.author_code}，作者机构是{cs.institution}")
    # cs.get_result()
    cs.get_overview()
