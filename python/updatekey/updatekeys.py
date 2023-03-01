# -*- coding: utf-8 -*-

import configparser
import requests
import time
import json
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.header import Header
import updatehtml

RETYR_MAX_COUNT = 3     # 接口失败 最大重试次数
EMAIL_LEFT_COUNT = 2    # key剩余多少时候发邮件


# -----------  每次运行脚本都会重置配置文件中的"是否有效"和"有效时间"两个模块. 然后从第一个key开始操作
print('开始执行脚本')
# 读取配置文件
config = configparser.RawConfigParser()
config.optionxform = str    # 禁用 option 名称的小写转换
config.read('config.ini')

# 重置配置文件
# 删除 "API_KEY_LIMIT_TIME" section, 后面重新生成
config.remove_section('API_KEY_LIMIT_TIME')

# 删除 "API_KEY_VALID" section, 后面重新生成
config.remove_section('API_KEY_VALID')

# write the updated config to file
with open('config.ini', 'w') as f:
    config.write(f)

# 获取所有的API key
api_keys = [key.strip() for key in config.get('API', 'keys').split(',')]

# 初始化有效API Key
valid_keys = {}
limit_time = {}
for key in api_keys:
    valid_keys[key] = True
    limit_time[key] = '0'
config['API_KEY_VALID'] = valid_keys
config['API_KEY_LIMIT_TIME'] = limit_time
with open('config.ini', 'w') as f:
    config.write(f)

print('初始化配置')

# 初始化当前使用的API key和当前使用的key的索引
current_key = api_keys[0]
current_key_index = 0
retry_times = 0
email_send_leftcount = 0

print('初始apikey: '+current_key+'')

updatehtml.push_to_remote('3333')


# 定义函数，用于请求API接口
def request_api():
    current_key = api_keys[current_key_index]
    print('\n⬇  开始请求api\n当前key : '+current_key+'   下标: '+str(current_key_index))
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + current_key
    }
    data = {
        'prompt': '2+3=',
        'temperature': 0.1,
        'max_tokens': 20,
        'model': 'text-davinci-003',
        'top_p': 1,
        'frequency_penalty': 0,
        'presence_penalty': 0,
        'stream': False
    }
    url = 'https://api.openai.com/v1/completions'
    response = requests.post(url, headers=headers, json=data)

    if response.status_code != 200:
        status_code = response.status_code
        data = response.json()
        error_message = data.get('error', {}).get('message', '')
        # error_type = data.get('error', {}).get('type', '')
        
        print('错误码  : {}'.format(status_code))
        print('错误信息: '+ error_message)
        return False, status_code
    else:
        print('接口请求成功')
        return True, 200
    

def sendEmail():
    global email_send_leftcount
    
    unuse_count = len(api_keys)
    for key in api_keys:
        if config['API_KEY_LIMIT_TIME'][key] != '0':
            unuse_count -= 1
    print('剩余个数: '+str(unuse_count))
    if unuse_count > EMAIL_LEFT_COUNT :
        return

    if email_send_leftcount == unuse_count :
        return

    # 发送邮件的账户信息
    smtp_server = "smtp.qq.com"  # QQ 邮箱的 SMTP 服务器地址
    smtp_port = 587  # QQ 邮箱的 SMTP 服务器端口号
    sender = "935688195@qq.com"  # QQ 邮箱地址
    password = "jkieovtorgsqbcig"  # QQ 邮箱授权码

    # 收件人邮箱地址
    recipients = ["18236915549@163.com", "1950896295@qq.com"]

    # 邮件内容
    subject = "剩余API数量不足, 当前剩余:"+str(unuse_count)
    body = "当前剩余"+str(unuse_count)+'个key未使用, 请及时检查并补充'

    # 构造邮件
    message = MIMEMultipart()
    message['From'] = Header(sender, 'utf-8')
    message['To'] = Header(", ".join(recipients), 'utf-8')
    message['Subject'] = Header(subject, 'utf-8')
    message.attach(MIMEText(body, 'plain', 'utf-8'))

    # 发送邮件
    try:
        smtpObj = smtplib.SMTP(smtp_server, smtp_port)
        smtpObj.starttls()  # 开启 TLS 加密传输
        smtpObj.login(sender, password)
        smtpObj.sendmail(sender, recipients, message.as_string())
        email_send_leftcount = unuse_count
        print("邮件发送成功")
    except Exception as e:
        print("邮件发送失败:", e)
        email_send_leftcount = 0
    finally:
        smtpObj.quit()


# 不断循环请求API接口
while True:
    sendEmail()
    success, status_code = request_api()
    if success:
        # 如果请求成功，等待10分钟继续请求
        retry_times = 0
        current_key = api_keys[current_key_index]
        updatehtml.updatehtml(current_key)
        time.sleep(30)
    else:
        # 如果请求失败，重试3次后, 使用下一个API key继续请求
        retry_times += 1
        time.sleep(3)
        if retry_times > RETYR_MAX_COUNT - 1 :

            current_key = api_keys[current_key_index]
           # 设置apikey失效
            valid_keys[current_key] = False
            config['API_KEY_VALID'] = valid_keys

            now = datetime.datetime.now()
            config['API_KEY_LIMIT_TIME'][current_key] = now.strftime("%Y-%m-%d %H:%M:%S")

            with open('config.ini', 'w') as f:
                config.write(f)

            retry_times = 0
            current_key_index += 1
            # 如果已经遍历完所有API key，则重新从第一个API key开始
            if current_key_index == len(api_keys):
                current_key_index = 0
                current_key = api_keys[current_key_index]
                
        else:
            # 重试小与n次, 继续重试
            print('')
