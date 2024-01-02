import asyncio  # 异步编程库
import os
import random  # 随机数生成库
import csv  # CSV文件处理库
from pyppeteer import launch  # 网页自动化测试库
from lxml import etree  # XML和HTML解析库
import re


class LaGou(object):
    def __init__(self):
        self.data_list = list()  # 数据列表

    def screen_size(self):
        """使用tkinter获取屏幕大小"""
        import tkinter  # GUI工具库
        tk = tkinter.Tk()  # 创建窗口
        width = tk.winfo_screenwidth()  # 获取屏幕宽度
        height = tk.winfo_screenheight()  # 获取屏幕高度
        tk.quit()  # 关闭窗口
        return width, height  # 返回屏幕宽度和高度

    async def main(self,jobname,city,filename):
        browser = None
        try:
            browser = await launch(
                headless=False,  # 是否无头模式（可见/不可见浏览器）
                userDataDir="./config",  # 用户数据目录（用于保持浏览器会话）
                args=['--disable-infobars', '--window-size=1366,768', '--no-sandbox']  # 启动参数
            )

            page = await browser.newPage()  # 创建新页面
            width, height = self.screen_size()  # 获取屏幕大小
            await page.setViewport({'width': width, 'height': height})  # 设置页面视口大小

            await page.goto(
                'https://www.lagou.com/wn/zhaopin')  # 打开目标网页
            await page.evaluateOnNewDocument(
                '''() =>{ Object.defineProperties(navigator, { webdriver: { get: () => false } }) }'''
            )  # 修改浏览器环境，防止被检测为自动化测试工具
            await asyncio.sleep(3)  # 等待页面加载

            i = 1
            flag = True
            while flag:
                print(i, '页', filename)
                await page.goto(
                    'https://www.lagou.com/wn/zhaopin?kd='+ jobname +'&pn='+str(i)+'&city='+city)  # 打开目标网页
                await page.evaluateOnNewDocument(
                    '''() =>{ Object.defineProperties(navigator, { webdriver: { get: () => false } }) }'''
                )  # 修改浏览器环境，防止被检测为自动化测试工具
                await asyncio.sleep(2)  # 等待页面加载
                content = await page.content()  # 获取页面内容
                html = etree.HTML(content)  # 解析页面内容
                self.parse_html(html, filename)  # 解析内容
                await asyncio.sleep(3)  # 等待页面加载
                i += 1

                # boss直聘限制翻页为10页，分省分批次抓取
                if i > 10:
                    flag = False
        except Exception as e:
            print(f"An error occurred: {e}")

        finally:
            if browser:
                await browser.close()  # Ensure the browser is closed.

    def input_time_random(self):
        return random.randint(100, 151)  # 生成随机的输入延迟时间

    def parse_html(self, html,filename):
        li_list = html.xpath('//*[@id="jobList"]/div[1]/div')  # 获取职位列表
        for li in li_list:
            job_name = li.xpath('div//div[@class="p-top__1F7CL"]/a/text()')[0].split("[")[0].strip()  # 工作名称
            experiences = li.xpath('div//div[@class="p-bom__JlNur"]/text()')[0]  # 工作经验
            experience = experiences.split("/")[0].strip()  # 工作经验
            education = experiences.split("/")[1].strip()  # 学历
            salary = li.xpath('div//span[@class="money__3Lkgq"]/text()')[0]  # 薪资待遇
            other = ''
            detail_url = ''
            company_name = li.xpath('div//div[@class="company-name__2-SjF"]/a/text()')[0]  # 公司名称
            info = li.xpath('//*[@id="jobList"]/div[1]/div[1]/div[1]/div[2]/div[2]/text()')[0].split('/')
            type = info[1] # 公司类型
            numbers = info[-1]    # 公司人数
            job_address = li.xpath('//*[@id="openWinPostion"]/text()')[0].split('[')
            location = job_address[1].replace(']','') # 工作地点
            welfare = li.xpath('div//div[@class="il__3lk85"]/text()')[0]  # 福利待遇
            words = li.xpath('//*[@id="jobList"]/div[1]/div[1]/div[2]/div[1]//text()')  # 词
            words = ','.join(words)

            with open(filename, encoding='utf-8', mode='a', newline='') as f:
                csv_writer = csv.writer(f)
                csv_writer.writerow([job_name,experience,education,salary,other,detail_url,company_name,type,numbers,location,words])  # 保存数据



import asyncio

keywords = ['python', 'java', '数据分析', '人工智能']
cityname = ['北京', '上海', '深圳', '杭州', '大连']

async def scrape_job_listings():
    boss_instance = LaGou()

    for city in cityname:
        for keyword in keywords:
            if not os.path.exists('data'):
                os.makedirs('data')
            filename = f'data/{city}_{keyword}相关.csv'
            if os.path.exists(filename):  # 存在此文件，爬过了，跳过
                print(filename + "存在此文件,爬过了，跳过")
                continue
            await boss_instance.main(keyword, city, filename)

loop = asyncio.get_event_loop()
loop.run_until_complete(scrape_job_listings())