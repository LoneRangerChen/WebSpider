# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import logging
import os
import sys
import time
from argparse import Action

from scrapy.http import HtmlResponse
from selenium.common.exceptions import TimeoutException, ElementNotVisibleException
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

from WebSpider.spiderutils.uploadutils import UpLoad_File_SENDKEYS_CHROME, UpLoad_File_POST
from WebSpider.spiderutils.useragentutils import User_Agent
from WebSpider.task.TaskChainService import converParams
from config import CHROME_PATH, CHROME_DRIVER_PATH, USER_AGENT_PATH, DOWNLOAD_PATH


#谷歌CHROME模拟器提供渲染功能并下载页面
from dao.TaskLogDao import TaskLogDao


class ChromeDownloaderMiddleware(object):
    '''
    selenium+Headless Chrome渲染模拟
    '''
    def __init__(self):
        options = webdriver.ChromeOptions()
        if sys.platform == 'linux':
            options.add_argument('--headless')  # 设置无界面
            options.add_argument('--disable-images')#禁止加载图片
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('blink-settings=imagesEnabled=false')
            options.add_argument('--disable-gpu')
        
        options.add_argument('--user-agent={}'.format(User_Agent(json_file=os.path.join(sys.path[0],USER_AGENT_PATH)).chrome()))#伪装头部信息
        #设置下载路径
        options.add_experimental_option("prefs",{
         'profile.default_content_settings.popups': 0,
         "download.default_directory" : DOWNLOAD_PATH,
         "download.prompt_for_download" : False#禁止下载对话框
        })
        if CHROME_PATH:
            options.binary_location = CHROME_PATH
        if CHROME_DRIVER_PATH:
            self.driver = webdriver.Chrome(chrome_options=options, executable_path=CHROME_DRIVER_PATH)  # 初始化Chrome驱动
        else:
            self.driver = webdriver.Chrome(chrome_options=options)  # 初始化Chrome驱动
        if sys.platform != 'linux':
            self.driver.maximize_window();#设置界面最大化
            self.driver.implicitly_wait(3)#渲染等待时间3s
        self.driver.set_page_load_timeout(15)  # 加载页面超时设置15s
        self.on_download_model()
        
    #开启下载模式
    def on_download_model(self):
        self.driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
        params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': DOWNLOAD_PATH}}
        command_result = self.driver.execute("send_command", params)
        
    def __del__(self):
        print('chrome-webdriver:正常退出并销毁进程')
        self.driver.stop_client();
        self.driver.quit();

    def process_exception(self):
        print('chrome-webdriver:异常退出并销毁进程')
        self.driver.stop_client();
        self.driver.quit();
        
    def process_request(self, request, spider):
        if spider.browse != 'CHROME' or 'login' in request.meta:
            return
        try:
            time.sleep(1)
            if request.meta :
                tasklog = TaskLogDao()
                try:
                    if  'logintask' in request.meta:
                        self.spiderlogin(self.driver,spider,request)
                        return HtmlResponse(url=self.driver.current_url, body=self.driver.page_source, request=request,
                                            encoding='utf-8',
                                            status=200)  # 返回HTML数据
                    elif 'next' in request.meta:
                        if not self.next_query(request.meta):
                            return HtmlResponse(url=request.url, body='', request=request, encoding='utf-8',
                                    status=200)
                        else:
                            return HtmlResponse(url=request.url, body=self.driver.page_source, request=request,
                                                encoding='utf-8',status=200)
                    else:
                        self.spider_auto_action(spider,request)
                        return HtmlResponse(url=request.url, body=self.driver.page_source, request=request, encoding='utf-8',
                                    status=200)
                except Exception as e:
                    message = '任务号【%s】出错：%s。' % (request.meta['taskCode'], e.__str__())
                    tasklog.recodeLog(spider.chainCode, 'fail', message)
                    return HtmlResponse(url=request.url, body='', request=request, encoding='utf-8',
                                    status=200)
            self.driver.get(request.url)  # 获取网页链接内容
            return HtmlResponse(url=request.url, body=self.driver.page_source, request=request, encoding='utf-8',
                                status=200)  # 返回HTML数据
        except TimeoutException:
            logging.error("Chrome driver TimeoutException...")
            return HtmlResponse(url=request.url, request=request, encoding='utf-8', status=500)
        except:
            logging.error('Chrome driver Exception...')
        finally:
            logging.info("Chrome driver end...")
    
    
    #自动动作模拟执行
    def spider_auto_action(self,spider,request):
        if not request.meta['isRefresh']:
            self.driver.get(request.url)
        else:
            self.driver.refresh()
            time.sleep(3)
        # 自动填写和模拟点击事件
        for param in spider.input:
            if param.get("TASK_CODE") == request.meta['taskCode']:
                # 剔除翻页操作
                flag = param.get("MAPPING_CODE")
                if flag in ('start', 'end'):
                    continue
                if param.get("INPUT_TYPE") == 'in':
                    self.spidersend(param)
                elif param.get("INPUT_TYPE") == 'click':
                    self.spiderclick(param)
                if flag == 'upload':
                    time.sleep(int(param.get('MAPPING_NAME')))
    #模拟登录chrome
    def spiderlogin(self, browser, spider,request):
        try:
            self.driver.get(request.url)  # 获取网页链接内容
            inputLoginParams = []
            for param in spider.input:
                if param.get("TASK_CODE") == spider.logintask.get("TASK_CODE"):
                    inputLoginParams.append(param)
            submitPath = '//*[@id="submit"]'
            for param in inputLoginParams:
                flag=param.get('MAPPING_NAME')
                selector=param.get('MAPPING_CODE')
                value = param.get('MAPPING_VALUE')
                if flag in ('username','password'):
                    un = browser.find_element_by_name(selector)
                    if un and un.get_attribute('type') !='hidden':
                        un.clear()
                        un.send_keys(value)
                        del un
                elif flag == 'submit':
                    submitPath=value
            lg = browser.find_element_by_xpath(submitPath)
            lg.click()
            logging.debug('模拟登录执行。。')
            time.sleep(1)
        except Exception as e:
            logging.error("没有找到对应的节点："+e.__str__())
            raise Exception(e)

    def spiderclick(self,param):
        try:
            value = param.get('MAPPING_VALUE')
            paramtype=param.get('MAPPING_TYPE')
            un = None
            text=''
            if paramtype =='xpath':
                un = self.driver.find_element_by_xpath(value)
                text=self.driver.find_element_by_xpath(value).text
            elif paramtype =='css':
                un = self.driver.find_element_by_css_selector(value)
                text =self.driver.find_element_by_css_selector(value).text
            else:
                un = self.driver.find_element_by_name(value)
                text =self.driver.find_element_by_name(value).text
            if un and un.get_attribute('type') != 'hidden':
                logging.debug('点击元素：%s【内容：%s】'%(un.tag_name,text))
                self.driver.execute_script("arguments[0].click();", un)
                if param.get('MAPPING_CODE') == 'download':#下载
                    logging.debug('动作【下载】：模拟点击事件，等待时间【%s】' % param.get('MAPPING_NAME'))
                    time.sleep(int(param.get('MAPPING_NAME')))
                else:
                    logging.debug('动作【%s】：模拟点击事件。。'%param.get('MAPPING_NAME'))
                    time.sleep(1)
            del un
        except Exception as e:
            logging.error("没有找到对应的节点："+e.__str__())
            raise Exception(e)

    def spidersend(self,param):
        try:
            flag = param.get('MAPPING_CODE')
            selector = param.get('MAPPING_VALUE')
            paramtype=param.get('MAPPING_TYPE')
            value = param.get('MAPPING_NAME')
            un = None
            if paramtype =='xpath':
                un = self.driver.find_element_by_xpath(selector)
            elif paramtype =='css':
                un = self.driver.find_element_by_css_selector(selector)
            else:
                un = self.driver.find_element_by_name(selector)
            if flag == 'file':#文件上传-文件路径
                UpLoad_File_SENDKEYS_CHROME(self.driver,un,value)
                logging.debug('动作【UPLOAD】：上传地址=>%s' % value)
                del un
                time.sleep(1)
                return True
            elif un and un.get_attribute('type') != 'hidden':
                un.clear()
                un.send_keys(value)
                logging.debug('动作【%s】：模拟查找(%s)后输入值=>%s' % (paramtype,selector,value))
                time.sleep(1)
            del un
            return False
        except Exception as e:
            logging.error("没有找到对应的节点："+e.__str__())
            raise Exception(e)

    def next_query(self,meta):
        #分页结束标识判断（分页结束标识通过样式查找方式匹配）
        nextBut = None
        endButt =None
        try:
             endButt=self.driver.find_element_by_css_selector(meta['end'])
        except Exception as e:
            logging.warning(e.__str__())
        finally:
            time.sleep(1)
            nextBut = self.driver.find_element_by_xpath(meta['start'])
            if nextBut != endButt:
                self.driver.execute_script("arguments[0].click();", nextBut)
                return True
            return False


#原生HTML方式下载页面
class HTMLDownloaderMiddleware(object):
    def __init__(self):
        pass

    def __del__(self):
        pass

    def process_request(self, request, spider):
        if spider.browse != 'HTML':
            return
        if request.meta and request.meta['tasktype']=='upload':#上传
            inputLoginParams = []
            file_field=None
            file_value=None
            for param in self.input:
                if param.get("TASK_CODE") ==request.meta['taskCode']:
                    if param.get('MAPPING_NAME')=='file':
                        file_field = param.get('MAPPING_CODE')
                        file_value = param.get('MAPPING_VALUE')
                    else:
                        inputLoginParams.append(param)
                
            text = UpLoad_File_POST(request.url, request.hearders, converParams(inputLoginParams,'formdata'), file_field, file_value)
            return HtmlResponse(url=request.url, body=text, request=request,
                         encoding='utf-8', status=200)
        pass

