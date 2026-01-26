import requests
import json
import time
import os  # 新增：用于读取环境变量
from datetime import datetime

# ===================== 配置区（无需修改） =====================
# 从环境变量读取Cookie（本地测试可手动设置，GitHub Actions自动注入）
GLADOS_COOKIE = os.getenv("GLADOS_COOKIE", "")  # 优先读环境变量，无则为空
# 签到接口（适配新版页面）
CHECKIN_URL = "https://glados.rocks/api/user/checkin"
# 用户信息接口（用于验证Cookie有效性）
USER_INFO_URL = "https://glados.rocks/api/user/status"
# 请求超时时间
TIMEOUT = 10
# ===================== 配置结束 =====================

# 校验Cookie是否存在
if not GLADOS_COOKIE:
    print("❌ 未找到GLADOS_COOKIE环境变量，请先配置！")
    exit(1)

# 请求头配置（模拟浏览器）
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://glados.rocks/console/checkin",
    "Origin": "https://glados.rocks",
    "Cookie": GLADOS_COOKIE,
    "Content-Type": "application/json;charset=UTF-8"
}

def check_cookie_valid():
    """验证Cookie是否有效"""
    try:
        response = requests.get(USER_INFO_URL, headers=headers, timeout=TIMEOUT)
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
    """执行GlaDOS签到"""
    # 先验证Cookie
    if not check_cookie_valid():
        return
    
    # 构造签到请求数据（适配新版接口）
    checkin_data = {
        "token": "glados.network"
    }
    
    try:
        # 发送签到请求
        response = requests.post(
            CHECKIN_URL,
            headers=headers,
            data=json.dumps(checkin_data),
            timeout=TIMEOUT
        )
        
        # 解析响应结果
        result = response.json()
        if result.get("code") == 0:
            print(f"🎉 签到成功！{result.get('message')}")
            # 打印签到奖励
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
