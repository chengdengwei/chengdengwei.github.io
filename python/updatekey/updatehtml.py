from bs4 import BeautifulSoup
import base64
import json
import git


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
            data['base64ApiKey'] = new_base64ApiKey
        if bundle_id == 'com.HalChatAI.tool' :
            base64ApiKey = data.get('base64ApiKey')   
            data['base64ApiKey'] = new_base64ApiKey
        
        # 将字典转换为JSON字符串
        new_data = json.dumps(data, indent=4, ensure_ascii=False)
        # 用新的JSON字符串替换旧的字符串
        div_tag.string.replace_with(new_data)


    # 将修改后的HTML保存到文件中
    with open('../../test.html', 'w') as f:
        f.write(str(soup))
    
    print('写入html成功, 写入key:'+new_api_key)

    push_remote()



def push_to_remote(new_api_key) :
    # 本地仓库路径
    local_repo_path = '../../'

    # Git仓库URL
    remote_repo_url = 'git@github.com:chengdengwei/chengdengwei.github.io.git'

    # 获取仓库对象
    repo = git.Repo(local_repo_path)



    # 拉取最新的代码
    repo.remotes.origin.pull()

    # 修改HTML文件

    # 添加修改后的文件到Git暂存区
    repo.git.add('path/to/modified/file')

    # 提交更改
    repo.index.commit('Commit message')

    # 推送更改到远程仓库
    repo.remotes.origin.push()
