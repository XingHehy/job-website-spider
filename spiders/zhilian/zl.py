import os
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
header = {
            'Cookie':'x-zp-client-id=-ee3a-42ca-8757-a7f071566b54; sajssdk_2015_cross_new_user=1; 1703508222; selectCity_search=530'
        }
data = []
citys = ['530','538','765','653','600']
keywords = ['python','java','数据分析','人工智能']
cityname = ['北京','上海','深圳','杭州', '大连']
for city in citys:
    for keyword in keywords:
        filename = (cityname[citys.index(city)] + '_' + keyword + '相关.csv').replace('/', '_')
        file_path = 'data/' + filename  # 文件路径
        if os.path.exists(file_path):  # 存在此文件，爬过了，跳过
            print(filename+"存在此文件,爬过了，跳过")
            continue
        flag = True
        for i in range(1,11): # 只爬前10页
            if flag:
                try:
                    url = 'https://sou.zhaopin.com/?jl='+city+'&kw='+keyword+'&p='+str(i)
                    html = requests.get(url,headers = header).text
                except Exception as e:
                    print(e)
                    exit(0)
                soup = BeautifulSoup(html, "html.parser")
                # print(soup.prettify())

                print(city+'_'+keyword+' 第',i,'页开始')
                joblist = soup.select(".joblist-box__item")
                for info in joblist:
                    # 详细信息链接
                    detail_url = info.find('a').get('href')
                    # 工作信息
                    job = info.select(".iteminfo__line1")[0]
                    job_name = job.select(".iteminfo__line1__jobname__name")[0].text
                    company_name = job.select(".iteminfo__line1__compname__name")[0].text

                    jobdesc = info.select(".iteminfo__line2")[0]
                    salary = jobdesc.select('.iteminfo__line2__jobdesc__salary')[0].text.strip().split('·')
                    # salary = jobdesc.select('.iteminfo__line2__jobdesc__salary')
                    # print(len(salary),'    ',salary[0].text,'\n')
                    # salary = salary[0].text.split('·')
                    demand = jobdesc.select('.iteminfo__line2__jobdesc__demand')[0].text.strip().split(' ')
                    location = demand[0]
                    experience = demand[1]
                    education = demand[2]

                    # 公司信息
                    compdesc = info.select(".iteminfo__line2__compdesc")[0]
                    spans = compdesc.findAll("span")
                    # print('\n',spans)
                    if len(spans)>1:
                        type = spans[0].text.strip()
                        numbers = spans[1].text.strip()
                    elif len(spans) == 1:
                        if '人' in spans[0]:
                            type = '暂无信息'
                            numbers = spans[0].text.strip()
                        else:
                            type = spans[0].text.strip()
                            numbers = '暂无信息'
                    else:
                        type = '暂无信息'
                        numbers = '暂无信息'
                    type = type if type != '' else '暂无信息'
                    numbers = numbers if numbers != ''  else '暂无信息'

                    # 词
                    words = info.select(".iteminfo__line3")[0]
                    words = words.findAll("div","iteminfo__line3__welfare__item")
                    words = [word.text.strip() for word in words]
                    data.append({
                        'job_name':job_name,
                        'experience':experience,
                        'education':education,
                        'salary':salary[0].strip(),
                        'other':salary[1].strip() if len(salary) > 1 else '暂无信息',
                        'detail_url':detail_url,
                        'company_name':company_name,
                        'type':type,
                        'numbers':numbers,
                        'location':location,
                        'words': ','.join(words)
                    })

                btns = soup.select(".pagination__pages .soupager")[0]
                nextBtn = btns.select("button")[-2]
                button = btns.findAll('button', {'disabled': 'disabled'})
                print(city+'_'+keyword+'第',i,'页结束，5s后继续')
                time.sleep(5)
                if button:
                    endBtn = button[-1].text
                    if endBtn == '下一页':
                        flag = False
            else:
                print(city+'_'+keyword+'相关 爬取结束')
                break
        # print(boss原始数据)
        df = pd.DataFrame(data)
        if not os.path.exists('data'):
            os.makedirs('data')
        df.to_csv('data/' + filename, index = False, encoding = 'utf-8')
        print('-----------',filename+' 爬取结束-----------')
