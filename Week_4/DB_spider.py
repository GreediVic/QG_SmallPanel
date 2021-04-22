# -*- coding:utf-8 -*-
# Author:        Greed_Vic(PL Z)
# Product_name:  PyCharm
# File_name:     DB_spider.py

"""
    业务分析：
        爬取豆瓣电影 Top 250 并存入 MySQL。
    1、首先获得250个url(利用主页面的多次next来获取)并存入列表
    2、再列表逐个url访问
    3、进入每一个电影的url 保存以下内容
        (其中)
      0电影排名      //div[@class="top250"]/span[@class="top250-no"]/text()
      ①电影标题     //span[@property="v:itemreviewed"]/text()
      ②导演        //span[@class='attrs']/a[@rel='v:directedBy']/text()
      ③上映年份     //span[@class="year"]/text()
      ④豆瓣评星     //div[@class="item"]/span[@class]/text()
      ⑤评价人数     //span[@property="v:votes"]/text()
      ⑥剧情介绍     //span[@property="v:summary"][position()<=1]/text()
      ⑥每个电影的url //div[@id="content"]//div[@class="hd"]/a/@href
      ⑦下一页       //link[@rel="next"]/@href
"""
# 首先导入必要的库
import os
import csv
import pymysql
import pandas as pd
import numpy as np
import requests
import time
from lxml import etree

base_url = "https://movie.douban.com/top250"

headers = {
    'Host': "movie.douban.com",
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36 Edg/89.0.774.77"
}


def get_in_info(all_url, in_headers):
    """
    这是手动操作的函数
    当访问缺失时能够补充信息的函数
    主要功能跟下方获取信息相同，只是需要输入访问失败的urls
    """
    # with open('movies_info', 'a+', encoding='utf-8') as file:
    all_info = []
    loss = []

    # 这是字典的keys 和 values
    list_keys = ['No.', 'title', 'director', 'year', 'type', 'stars', 'eval_people_num', 'summary']
    list_values = ['string(//div[@class="top250"]/span[@class="top250-no"])',
                   'string(//span[@property="v:itemreviewed"])',
                   'string(//span[@class="attrs"]/a[@rel="v:directedBy"])',
                   '//span[@class="year"]/text()',
                   '//span[@property="v:genre"]/text()',
                   '//div[@class="item"]/span[@class]/text()',
                   'string(//span[@property="v:votes"])',
                   '//span[@property="v:summary"]/text()']

    for x, i in enumerate(all_url):
        dic = {}  # 每一部电影的信息用一个字典存放，再放入列表中
        try:
            cur_re = requests.get(i, headers=in_headers).text  # 访问当前一部电影
            cur_html = etree.HTML(cur_re)  # 解析
            for n, m in enumerate(list_values):  # 准备写入字典
                if n == 5:
                    # 评星内容  删除前后空白并且设计一定的格式在融合例如 : 5星:98% 4星:1%...
                    dic[list_keys[n]] = ''.join([y.strip() + ' ' if t % 2 != 0 else y.strip() + ':'
                                                 for t, y in enumerate(cur_html.xpath(m))])
                elif n == 7:
                    # 剧情介绍
                    dic[list_keys[n]] = ''.join([y.strip() for y in cur_html.xpath(m)])

                elif n == 3 or 4:
                    # 年份和类型
                    dic[list_keys[n]] = str(''.join(cur_html.xpath(m)) + ')').strip('()')

                else:
                    # 其他直接获取，因为在values中设置成了string()获取，直接是字符串
                    dic[list_keys[n]] = cur_html.xpath(m)

                if n == 0:
                    dic[list_keys[n]] = int(cur_html.xpath(m)[3:])

            print(f"第{x + 1}次获取信息成功！")
        except Exception as reason:
            print(f"第{x + 1}次获取信息失败:原因:{reason.args}")
            print(f"获取信息失败url:{i}")
            loss.append(i)  # 保存 访问失败的网页
        freeze(0, 3)  # "冷却时间"
        all_info.append(dic)  # 每一次都存入一个列表当中
    return all_info, loss  # 返回访问成功的所有电影信息和失败的url列表

def cal_time():
    """
    显示开始和结束时间(无聊用来看看时间的)
    """
    return time.strftime('%Y/%m/%d %H:%M:%S',
                         time.localtime(time.time()))

def freeze(low=4, high=20):
    """
    这是用来随机停歇
    减缓爬取的速率
    但是时而还是会 返回网页433
    """
    n = -1
    while n < low or n > high:
        n = np.random.randint(5, 23) / np.random.randn()
    print(f"随机停歇时间:{n}秒")
    time.sleep(n)

class DbSpider(object):
    """
    这是一个爬取豆瓣的网络爬虫类
    """
    def __init__(self, base_url, headers, tosave):
        self.base_url = base_url
        self.headers = headers
        self.all_url = []
        self.all_info = []
        self.key = []
        self.values = []
        self.file = tosave
        self.loss_page = None
        self.loss_movies = None

    def get_movies_url(self):
        """
        获得250个电影的url
        """
        movies_url = []
        url = self.base_url  # 这是最开始的网页
        loss = []
        for i in range(1, 12):

            try:
                print(f"正在访问:{url}")
                respond = requests.get(url, headers=self.headers).text  # 取得源代码
                re_html = etree.HTML(respond)  # 解析网页

                # 获得当前页面的25个电影的url(是一个列表，最后会成为10*25的列表)
                movies_url.append(re_html.xpath('//div[@id="content"]//div[@class="hd"]/a/@href'))
                print(f"第{i}次访问成功！")

                # 准备模仿点击下一页(其实就是获得next url)
                next_url = re_html.xpath('string(//link[@rel="next"]/@href)')
                url = self.base_url + next_url  # 拼接
                print(f"即将访问:{url}")

                # 提示错误，并且将访问失败的url写入列表 方便后来重新访问
            except Exception as reason:
                print(f"第{i}次访问失败原因:{reason.args}")
                print(f"访问失败url:{url}")
                loss.append(url)

            if url == self.base_url:  # 到最后会没有next url 所以拼接后可能是最开头那一页
                print("访问结束")
                break  # 这样就退出去
            # freeze(1, 3)  # 随机暂停
            if i == 3:  # 用来代码预跑的，可以快点看看结果
                break  # 如果要完整请注释这两行代码
        self.all_url = [x for i in movies_url for x in i]  # 展开 维度2->1

        if loss:
            print("有访问失败的页面,已经返回")
            self.loss_page = loss

    def get_in_info(self):
        """
        进入每一个url进行解析
        每一个电影各种属性都存放在一个字典中
        然后写入列表
        最后得到的是列表中有多个字典
        每个字典存着每个电影的属性
        """
        assert (self.all_url is not None)
        if not (self.all_url is not None):
            raise AssertionError('You have to get movies urls first')
        # with open('movies_info', 'a+', encoding='utf-8') as file:
        all_info = []
        loss = []

        # 这是字典的keys 和 values
        list_keys = ['No.', 'title', 'director', 'year', 'type', 'stars', 'eval_people_num', 'summary']
        list_values = ['string(//div[@class="top250"]/span[@class="top250-no"])',
                       'string(//span[@property="v:itemreviewed"])',
                       'string(//span[@class="attrs"]/a[@rel="v:directedBy"])',
                       '//span[@class="year"]/text()',
                       '//span[@property="v:genre"]/text()',
                       '//div[@class="item"]/span[@class]/text()',
                       'string(//span[@property="v:votes"])',
                       '//span[@property="v:summary"]/text()']
        self.key = list_keys
        self.values = list_values

        for x, i in enumerate(self.all_url):
            dic = {}  # 每一部电影的信息用一个字典存放，再放入列表中
            try:
                cur_re = requests.get(i, headers=self.headers).text  # 访问当前一部电影
                cur_html = etree.HTML(cur_re)  # 解析
                for n, m in enumerate(list_values):  # 准备写入字典
                    if n == 5:
                        # 评星内容  删除前后空白并且设计一定的格式在融合例如 : 5星:98% 4星:1%...
                        dic[list_keys[n]] = ''.join([y.strip() + ' ' if t % 2 != 0 else y.strip() + ':'
                                                     for t, y in enumerate(cur_html.xpath(m))])
                    elif n == 7:
                        # 剧情介绍
                        dic[list_keys[n]] = ''.join([y.strip() for y in cur_html.xpath(m)])

                    elif n == 3 or 4:
                        # 年份和类型
                        dic[list_keys[n]] = str(''.join(cur_html.xpath(m)) + ')').strip('()')

                    else:
                        # 其他直接获取，因为在values中设置成了string()获取，直接是字符串
                        dic[list_keys[n]] = cur_html.xpath(m)

                    if n == 0:
                        # 排名，将其设置为int类型方便数据库中排序
                        dic[list_keys[n]] = int(cur_html.xpath(m)[3:])
                        # print(dic[list_keys[n]])

                print(f"第{x + 1}次获取信息成功！")
            except Exception as reason:
                print(f"第{x + 1}次获取信息失败:原因:{reason.args}")
                print(f"获取信息失败url:{i}")
                loss.append(i)  # 保存 访问失败的网页
            # freeze(0, 3)  # "冷却时间"
            all_info.append(dic)  # 每一次都存入一个列表当中
            self.all_info = all_info

        if loss:
            print(f"有访问失败电影网页\n已经返回")
        self.loss_movies = loss

    def write_in_csv(self):
        assert (self.all_info is not None)
        if not (self.all_info is not None):
            raise AssertionError('You have to get movies infos first')
        data = pd.DataFrame(self.all_info)
        data.to_csv(self.file, mode='a+', encoding='utf_8_sig')  # 防止乱码的编码方式
        os.system(self.file)
        print("Work Done!")

    def write_in_database(self):
        db_config = {
                   'host': 'localhost',  # 需要连接ip
                   'port': 3306,  # 默认端口3306
                   'user': 'root',  # 用户名.
                   'password': '3120005313',  # 用户密码
                   'db': 'douban_top250',  # 进入的数据库名.
                   'charset': 'utf8'  # 编码方式.
        }

        # 建立连接
        mq = pymysql.connect(**db_config)

        # 创建游标对象
        cursor = mq.cursor()

        # 读取csv文件
        # 若是用utf-8则出现
        # 报错'utf-8' codec can't decode byte 0xc9 in position 67: invalid continuation byte
        with open(self.file, 'r', encoding='gbk') as f:  # 打开文件
            read = csv.reader(f)  # 返回可迭代对象，转换成列表方便操作
            for i in list(read)[1:]:  # 第一行（0行）是columns 数据库中已经创建,不入
                x = tuple(i[1:])  # 第一列（0列）是自动形成的从0开始的有序数列，我们有排名能够对应电影，不写进数据库
                sql = "INSERT INTO db_250 VALUES" + str(x)  # * INSERT INTO * - 向数据库表中插入数据
                cursor.execute(sql)  # 执行SQL语句

            mq.commit()  # 提交数据
            cursor.close()  # 关闭游标
            mq.close()  # 关闭数据库


if __name__ == '__main__':
    start = DbSpider(base_url, headers, 'DB_250.csv')
    start.get_movies_url()
    start.get_in_info()
    start.write_in_csv()

    if start.loss_movies:
        print("请先关闭文件后，重新操作执行下方注释内容")
        """
        若大网页访问失败需要中途停止重新来过
        小网页（每个电影网页）访问失败则进行下面的命令行
        
        loss = start.loss_movies
        while loss:
            print("正重新访问之前失败的电影url:")
            all_info, loss = get_in_info(loss, headers)
            data = pd.DataFrame(all_info)
            data.to_csv(start.file, mode='a+', encoding='utf_8_sig')
            这样执行后需要手动调整（删除部分新的columns）
        然后再执行写入入数据库的方法
        start.write_in_database()
        """
        loss = start.loss_movies
        while loss:
            print("正重新访问之前失败的电影url:")
            all_info, loss = get_in_info(loss, headers)
            data = pd.DataFrame(all_info)
            data.to_csv(start.file, mode='a+', encoding='utf_8_sig')
    else:
        """
        倘若报错：
        由于编码有问题，无论在to_csv的时候使用的是"utf_8"还是"utf_8_sig"都会导致在打开文件准备写入
        数据库的时候出错，只能通过手动将文件改成gbk（或UTF-8，修改时要同时改写入数据库的打码）
        的方式编码（这里手动利用的是notepad++）
        最后再从控制台中输入start.write_in_csv()的方式进行写入数据库
        """
        start.write_in_database()

