import requests
import re
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# 配置
SIGN_IN_URL = "https://www.lgych.com/wp-content/themes/modown/action/user.php"  # 签到接口
USER_PAGE_URL = "https://www.lgych.com/user"  # 用户信息页面
cookies = {
    "wordpress_logged_in_c31b215c0db6cdb6478d719de4022ec2": ""  # 从浏览器中获取
}
headers = {
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "x-requested-with": "XMLHttpRequest"
}
data = {"action": "user.checkin"}

def get_user_info():
    """获取用户信息（积分和金币余额）"""
    try:
        response = requests.get(USER_PAGE_URL, headers=headers, cookies=cookies)
        if response.status_code == 200:
            html_content = response.text
            # 提取可用积分
            points_match = re.search(r"可用积分：(\d+)", html_content)
            points = points_match.group(1) if points_match else "无法获取"
            # 提取金币余额
            gold_match = re.search(r'<b class="color">(\d+\.\d{2})</b>\s*金币', html_content)
            gold = gold_match.group(1) if gold_match else "无法获取"
            return points, gold
        else:
            print(f"获取用户信息页面失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"获取用户信息异常: {e}")
    return "无法获取", "无法获取"

def create_session():
    """创建带有重试机制的请求会话"""
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))
    return session

def sign_in():
    """执行签到操作"""
    try:
        session = create_session()
        # 执行签到请求
        response = session.post(SIGN_IN_URL, headers=headers, cookies=cookies, data=data)
        if response.status_code == 200:
            result_text = response.text.encode().decode('unicode_escape')
            print("签到接口返回内容:", result_text)

            # 尝试访问用户页面获取额外奖励
            user_page_response = session.get(USER_PAGE_URL, headers=headers, cookies=cookies)
            extra_reward_status = "成功访问用户页面，获取额外奖励。" if user_page_response.status_code == 200 else f"访问用户页面失败，状态码: {user_page_response.status_code}"

            # 获取积分和金币余额
            points, gold = get_user_info()

            # 根据签到结果输出信息
            if "金币" in result_text:
                print(f"签到成功！当前可用积分：{points}，金币余额：{gold}金币。{extra_reward_status}")
            elif "已经" in result_text:
                print(f"已签到过。当前可用积分：{points}，金币余额：{gold}金币。{extra_reward_status}")
            else:
                print(f"签到失败：未知原因。返回内容: {result_text}")
        else:
            print(f"签到请求失败，状态码: {response.status_code}")
    except Exception as error:
        print(f"签到或访问用户页面请求异常: {error}")

if __name__ == "__main__":
    sign_in()
