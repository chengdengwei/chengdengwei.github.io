from bs4 import BeautifulSoup
import base64
import json
import git
from git import Repo, GitCommandError

# 本地仓库路径
local_repo_path = '../../'

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
            if new_base64ApiKey == base64ApiKey :
                print('已是最新key, 不需要更新')
                return False
            base64ApiKey_vip = data.get('base64ApiKey_vip')    
            base64ApiKey_new = data.get('base64ApiKey_new')    
            base64ApiKey_vip_new = data.get('base64ApiKey_vip_new')    
            base64ApiKey_paid = data.get('base64ApiKey_paid')    
            data['base64ApiKey'] = new_base64ApiKey
            data['base64ApiKey_vip'] = base64ApiKey_vip
            data['base64ApiKey_new'] = base64ApiKey_new
            data['base64ApiKey_vip_new'] = base64ApiKey_vip_new
            data['base64ApiKey_paid'] = base64ApiKey_paid
        if bundle_id == 'com.HalChatAI.tool' :
            base64ApiKey = data.get('base64ApiKey')   
            if new_base64ApiKey == base64ApiKey :
                print('已是最新key, 不需要更新')
                return False
            data['base64ApiKey'] = new_base64ApiKey
        
        # 将字典转换为JSON字符串
        new_data = json.dumps(data, indent=4, ensure_ascii=False)
        # 用新的JSON字符串替换旧的字符串
        div_tag.string.replace_with(new_data)

    # 将修改后的HTML保存到文件中
    with open('../../test.html', 'w') as f:
        f.write(str(soup))
    
    print('写入html成功, 写入key:'+new_api_key)
    return True



def push_to_remote(new_api_key) :

    # 初始化 Git 仓库
    repo = git.Repo(local_repo_path)

    # 恢复本地修改
    repo.git.reset('--hard')

    # 拉取最新代码
    repo.remotes.origin.pull()

    success = updatehtml(new_api_key)
    if success == False :
        return

    # 添加文件到 Git 暂存区
    repo.git.add('.')

    # 提交代码到本地 Git 仓库
    repo.git.commit('-m', 'Update API Key')

    # 推送代码到远程 Git 仓库
    # repo.remotes.origin.push()

    try:
        repo.remotes.origin.push()
        print("Push success!")
    except GitCommandError as e:
        print("Push failed:", e)
