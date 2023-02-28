from bs4 import BeautifulSoup
import base64
import json


def updatehtml(new_api_key) :
    # 读取 HTML 文件
    with open('../../test.html', 'r') as f:
        html = f.read()

    # 使用 BeautifulSoup 解析 HTML 文档
    soup = BeautifulSoup(html, 'html.parser')
    
    # 找到指定 bundleId 的 <div hidden> 元素
    target_div = soup.find('div', attrs={'bundleId': 'com.HalChatAI.tool'})


    new_base64ApiKey = base64.b64encode(new_api_key.encode()).decode()
    div_tags = soup.find_all('div', {'hidden': True})
    for div_tag in div_tags:
        data = json.loads(div_tag.string.strip())
        bundle_id = data.get('bundleId')
        if bundle_id == 'com.chatGPT.tool' :
            base64ApiKey = data.get('base64ApiKey')    
            base64ApiKey_vip = data.get('base64ApiKey_vip')    
            base64ApiKey_new = data.get('base64ApiKey_new')    
            base64ApiKey_vip_new = data.get('base64ApiKey_vip_new')    
            base64ApiKey_paid = data.get('base64ApiKey_paid')    
            data['base64ApiKey'] = 'ffsfsfs'
        if bundle_id == 'com.HalChatAI.tool' :
            base64ApiKey = data.get('base64ApiKey')   
            data['base64ApiKey'] = '1111222'
        
        # 将字典转换为JSON字符串
        new_data = json.dumps(data)
        print('转化为json: ' + new_data)
        # 用新的JSON字符串替换旧的字符串
        div_tag.string.replace_with(new_data)


    # 将修改后的HTML保存到文件中
    with open('new_file.html', 'w') as f:
        f.write(str(soup))
    
    print('写入html文件, 写入key:'+new_api_key)