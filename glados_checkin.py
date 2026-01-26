import requests
import json
import os
from datetime import datetime

# ===================== 配置区（无需修改，Cookie从环境变量读取） =====================
# 从GitHub Secrets读取Cookie，本地测试可手动设置环境变量
GLADOS_COOKIE = os.getenv("GLADOS_COOKIE", "")
# 你Postman验证过的签到接口
CHECKIN_URL = "https://glados.cloud/api/user/checkin"
# 用户信息验证接口（确认Cookie有效）
USER_INFO_URL = "https://glados.cloud/api/user/status"
# 请求超时时间
TIMEOUT = 15
# ===================== 配置结束 =====================

# 校验Cookie是否配置
if not GLADOS_COOKIE:
    print("❌ 未配置GLADOS_COOKIE环境变量！")
    exit(1)

# 完全复刻Postman的请求头（一字不差）
headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9",
    "content-type": "application/json;charset=UTF-8",
    "origin": "https://glados.cloud",
    "priority": "u=1, i",
    "sec-ch-ua": "\"Google Chrome\";v=\"143\", \"Chromium\";v=\"143\", \"Not A(Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    "cookie": GLADOS_COOKIE  # 替换为环境变量中的Cookie
}

# Postman验证过的请求体（token已更新为glados.cloud）
checkin_data = {
    "token": "glados.cloud"
}

def check_cookie_valid():
    """验证Cookie是否有效（复用相同请求头）"""
    try:
        response = requests.get(
            USER_INFO_URL,
            headers=headers,
            timeout=TIMEOUT
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                print(f"✅ Cookie有效，当前用户: {data['data']['email']}")
                return True
            else:
                print(f"❌ Cookie无效: {data.get('message')}")
                return False
        else:
            print(f"❌ 验证Cookie失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 验证Cookie时出错: {str(e)}")
        return False

def glados_checkin():
    """执行签到（完全复刻Postman的POST请求）"""
    # 先验证Cookie
    if not check_cookie_valid():
        return
    
    try:
        # 发送和Postman完全一致的POST请求
        response = requests.post(
            CHECKIN_URL,
            headers=headers,
            data=json.dumps(checkin_data),  # 序列化请求体
            timeout=TIMEOUT
        )
        
        # 打印原始响应（方便排查）
        print(f"📝 签到请求响应状态码: {response.status_code}")
        print(f"📝 签到请求原始响应: {response.text}")
        
        # 解析响应结果
        result = response.json()
        if result.get("code") == 0:
            print(f"🎉 签到成功！{result.get('message')}")
            # 打印签到奖励（如果有）
            if "list" in result.get("data", {}):
                rewards = result["data"]["list"]
                for reward in rewards:
                    print(f"🎁 获得: {reward.get('name')} x {reward.get('count')}")
        else:
            print(f"❌ 签到失败: {result.get('message')}")
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时，请检查网络")
    except requests.exceptions.ConnectionError:
        print("❌ 网络连接失败，请检查网络")
    except json.JSONDecodeError:
        print(f"❌ 响应解析失败，原始响应: {response.text}")
    except Exception as e:
        print(f"❌ 签到过程出错: {str(e)}")

if __name__ == "__main__":
    print(f"📅 开始执行GlaDOS签到 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    glados_checkin()
    print("🔚 签到脚本执行完毕")
