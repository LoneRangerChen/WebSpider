#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# driver: WebDriver
#chrome模拟器
import logging
import os
import random
import sys

import requests
from requests_toolbelt import MultipartEncoder


def UpLoad_File_SENDKEYS_CHROME(driver, input_html, filePath, check_Input = None):
    """
    解决页面中存在input标签但是被隐藏，需要使用js才能赋值 才能完成上传文件的操作
    :param driver:  WebDriver
    :param input_html: WebElement
    :param filePath: str：检查服务器返回的图片地址，还是本地上传文件的地址，需要自行确认
    :param check_Input: WebElement
    :Exception: 如果此元素实在是无法生效则抛出异常
    :return: 检查结果

    """
    if input_html.tag_name.lower() != 'input':
        raise Exception("这个元素不是 input 标签，你还是想想其他办法吧！")
    if not input_html.is_displayed():  # 如果元素是无效的，而且还是//input[@type = 'hidden' ] 的标签
        if input_html.get_attribute("type") == 'hidden':
            # 使用js 将他 type 修改为 text，让他生效。
            js = 'arguments[0].setAttribute("type","text")'
            driver.execute_script(js, input_html)
    if not input_html.is_displayed():  # 如果不是 //input[@type = 'hidden' ] 使用 display = none 或者 class 隐藏
        # 使用js让他显示
        js = 'arguments[0].style.display = \'block\';'
        driver.execute_script(js, input_html)
    if input_html.is_displayed():
        if input_html.get_attribute('readonly') =='true':
            js = 'arguments[0].removeAttribute("readonly")'
            driver.execute_script(js, input_html)
        input_html.clear()
        input_html.send_keys(filePath)
    else:
        input_html.clear()
        input_html.send_keys(filePath)
    if check_Input is None:
        return "没有进行结果认证"
    else:
        return check_Input.get_attribute("value")
    pass


#原生html方式上传提交
def UpLoad_File_POST(url,headers,jsonData,file_field,file_value):
    file=(os.path.basename(file_value), open(file_value, 'rb'), 'application/octet-stream')
    if not file_field or not file_value:
        logging.error("上传文件标识字段或上传文件路径为空，请检查")
        return
    jsonData[file_field]=file
    multipart_encoder = MultipartEncoder(
        fields=jsonData, # file为路径
        boundary='-----------------------------' + str(random.randint(1e28, 1e29 - 1))
    )

    headers['Content-Type'] = multipart_encoder.content_type
    # 请求头必须包含一个特殊的头信息，类似于Content-Type: multipart/form-data; boundary=${bound}
    r = requests.post(url, data=multipart_encoder, headers=headers)
    return r.text
