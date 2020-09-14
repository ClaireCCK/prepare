# -*- coding: utf-8 -*-
"""
Created on Mon Sep  7 09:36:54 2020

@author: 寇灿灿
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Sep  3 14:38:28 2020

@author: 寇灿灿
"""
# 解析网页数据

import requests
from lxml import etree

import pandas as pd
from sqlalchemy import create_engine
import  re
import math
from urllib import parse
import datetime
from pymysql import *
import pymysql


class Govement(object):
    def __init__(self):
        self.base_url = 'https://zjyc.tobacco.gov.cn/zwfw/permit/list_publish.do'
        self.headers = {'User-Agent':
                       'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36(KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
                        'Cookie': 'JSESSIONID=23B02C240B0B463747B9CBA9FBBE624F; aliyungf_tc=AQAAAEsbw0JxOwkAZunremi0z1tkr6vo; getArea=%7B%22name%22%3A%22%u676D%u5DDE%u5E02%u5C40%28%u672C%u7EA7%29%22%2C%22adcode%22%3A%22330101%22%7D; tipbox=close; acw_tc=76b20ffd15991151930954025e5ef5784da1694eea4d27aeff15a12744fdf2; SERVERID=bd520ca05692b7b4829ba9a4184c7522|1599115496|1599113266'
                   }

    #获取网页数据2019-01-01——20200904
    def Get_html(self,page,name,adcode,startDate,endDate):
        formdata={'startDate':startDate,'endDate':endDate,'current':page,'name':name,'adcode':adcode,'publishType':2}
        i=0;
        while i<3:
            try:
                requests.adapters.DEFAULT_RETRIES = 5
                html = requests.post(self.base_url, data=formdata,headers=self.headers,timeout=5).text
                parse_html = etree.HTML(html)
                return parse_html
            except Exception as ee:
                i+=1
                print(ee)
                print(name)
                print("connection failed")

    #获取网页总页数
    def Get_page_number(self,parse_html):
        script = parse_html.xpath("/html/script[1]/text()")
        group=re.search("\tcount = \\'(.*)\\' \* 1;",script[0])
        if group:
            total_num=group.group(1)
            page_num=math.ceil(int(total_num)/10)
            return page_num
        else:
            print("NO match")
    
    #获取一页的数据
    def Get_data(self,parse_html):
        title = {}
        title['license_num']=parse_html.xpath("//table/tr/td[2]/text()")
        title['handle_item']=parse_html.xpath("//table/tr/td[3]/text()")
        title['company']=parse_html.xpath("//table/tr/td[4]/text()")
        title['address']=parse_html.xpath("//table/tr/td[5]/text()")
        title['holder']=parse_html.xpath("//table/tr/td[6]/text()")
        title['result']=parse_html.xpath("//table/tr/td[7]/text()")
        title['date']=parse_html.xpath("//table/tr/td[8]/text()")
        return title
    
    def Store_data(self,name0,name,adcode,startDate,endDate):
        page=1
        tmp_html=Govement.Get_html(self,page,name,adcode,startDate,endDate)
        p=Govement.Get_page_number(self,tmp_html)
        
        while page<=p:
            print("*******")
            print("开始爬第"+str(page)+"页")
            parse_html=Govement.Get_html(self,page,name,adcode,startDate,endDate)
            
            flag=False#标识该市无数据
            if(page==1):
                html=Govement.Get_data(self,parse_html)
                print("html长度"+str(len(html)))
                l=list(html.values())[0]
                if len(l)==0:
                    flag=True       
                    break
                location=[name0 for x in range(0,len(l))]
                location=pd.DataFrame(location)
                sublocation=[name for x in range(0,len(l))]
                sublocation=pd.DataFrame(sublocation)
                result=pd.DataFrame(html)
                print("第一页"+str(result.shape))
                result=pd.concat([result,location,sublocation],axis=1,join_axes=[result.index])
            else:
                html=Govement.Get_data(self,parse_html)
                print("html长度"+str(len(html)))
                l=list(html.values())[0]
                if len(l)==0:
                    break
                location=[name0 for x in range(0,len(l))]
                location=pd.DataFrame(location)
                sublocation=[name for x in range(0,len(l))]
                sublocation=pd.DataFrame(sublocation)
                data=pd.DataFrame(html)
                print("拼接前"+str(data.shape))
                data=pd.concat([data,location,sublocation],axis=1,join_axes=[data.index])
                print("拼接后"+str(data.shape))
                result=pd.concat([result,data]).reset_index(drop=True)#将第一页数据与之后的进行连接，重置索引
            print("成功爬第" + str(page) + "页，已有数据条数："+str(result.shape[0])+"。每条有"+str(result.shape[1])+"列")
            page=page+1
        if flag==False:
            print(result.shape)
            result.columns=['license_num','handle_item','company','address','holder','result','date','location','sublocation']
            result.to_csv('D:/spyder_py3/yancao/yczf.csv',encoding='gb18030')
            '''
            #数据存储进数据库
            engine = create_engine('mysql+pymysql://root:Aa123456@172.81.250.56:11006/spider_yancao?charset=utf8')
            result.to_sql('zhiquan', engine, index=False, if_exists='append')
            '''

    # 从数据库查询上一次爬取到的最新日期
    def getLastDate(self):
    
        # conn = connect(host='localhost', port=3306, user='root', password='123456', database='jzt', charset='utf8')
        conn = connect(host='172.81.250.56', port=11006, user='root', password='Aa123456', database='spider_yancao', charset='utf8')
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        cursor.execute('SELECT date from zhiquan order BY date DESC LIMIT 1')
        last_date = cursor.fetchone()['date']
        date = datetime.datetime.strptime(last_date.split(" ")[0],'%Y-%m-%d')
        need_date = date + datetime.timedelta(days=1)
    
        cursor.close()
        conn.close()
        return str(need_date).split(" ")[0]   
    
    # 获取当前日期
    def getNowDate(self):
        now = datetime.datetime.now()
        now_date = now.strftime('%Y-%m-%d')
        return now_date

if __name__ == '__main__':
    spider=Govement()
    page=1
    lastDate=spider.getLastDate()
    curDate=spider.getNowDate()
    print("日期区间"+lastDate+"——"+curDate)
    print("*******") 
    
    names=['杭州市','宁波市','温州市','湖州市','嘉兴市','绍兴市','金华市','衢州市','舟山市','台州市','丽水市']
    ns=[['杭州市局(本级)','萧山区局','余杭区局','临安区局','桐庐县局','淳安县局','建德市局','富阳区局'],
         ['宁波市局(本级)','余姚市局','慈溪市局','奉化区局','宁海县局','象山县局','鄞州区局','镇海区局','北仑区局'],
         ['温州市局(本级)','洞头区局','乐清区局','瑞安区局','永嘉县局','平阳县局','泰顺县局','苍南县局','文成县局','龙港市局'],
         ['湖州市局(本级)','德清县局','安吉县局','长兴县局'],
         ['嘉兴市局(本级)','平湖市局','海宁市局','桐乡市局','嘉善县局','海盐县局'],
         ['绍兴市局(本级)','上虞区局','诸暨市局','嵊州市局','新昌县局'],
         ['金华市局(本级)','兰溪市局','东阳市局','义乌市局','永康市局','浦江县局','武义县局','磐安县局'],
         ['衢州市局(本级)','江山市局','龙游县局','常山县局','开化县局'],
         ['舟山市局(本级)','普陀区局','岱山县局','嵊泗县局'],
         ['台州市局(本级)','黄岩区局','温岭市局','临海市局','玉环市局','三门县局','天台县局','仙居县局'],
         ['丽水市局(本级)','龙泉市局','青田县局','云和县局','庆元县局','缙云县局','遂昌县局','松阳县局','景宁县局']]
    
    acs=[['330101','330109','330110', '330185', '330122', '330127' ,'330182', '330183'],
         ['330201' ,'330281', '330282', '330283', '330226', '330225', '330212' ,'330211', '330206'],
         [330301, 330322 ,330382 ,330381, 330324, 330326 ,330329, 330327, 330328 ,330383],
         [330501 ,330521 ,330523 ,330522],
         [330401,330482  ,330481 ,330483 ,330421 ,330424],
         [330601, 330604 ,330681 ,330683 ,330624],
         [330701, 330781, 330783, 330782, 330784, 330726,  330723, 330727],
         [330801 ,330881, 330825, 330822, 330824],
         [330901, 330903, 330921, 330922],
         [331001, 331003 ,331081, 331082 ,331021 ,331022, 331023 ,331024],
         [331101, 331181, 331121, 331125, 331126, 331122, 331123, 331124, 331127]]
    for k in range(len(names)):
        name0=names[k]
        n=ns[k]
        ac=acs[k]
        
        for i in range(len(n)):
            spider.Store_data(name0,n[i],ac[i],lastDate,curDate)
            
    