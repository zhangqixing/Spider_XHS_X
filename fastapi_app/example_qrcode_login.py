#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书二维码登录调用示例
演示如何调用 spider_xhs/apis/xhs_pc_login_apis.py 中的二维码登录函数
"""

import sys
import os
from pathlib import Path



# 添加项目路径到系统路径
project_root = Path(__file__).parent.parent.parent.resolve() / "Splider_XHS"
sys.path.insert(0, str(project_root))
print(f"项目根路径已添加到sys.path: {project_root}")

from apis.xhs_pc_login_apis import XHSLoginApi

# 导入登录API1

def example_1_simple_qrcode_login():
    """示例1: 最简单的二维码登录"""
    print("示例1: 最简单的二维码登录")
    print("-" * 40)
    
    # 创建登录API实例
    login_api = XHSLoginApi()
    
    # 执行二维码登录
    cookies_str = login_api.qrcode_login(show_in_terminal=True)
    
    if cookies_str:
        print(f"\n登录成功! Cookies:\n{cookies_str}")
        return cookies_str
    else:
        print("\n登录失败")
        return None

def example_2_qrcode_login_with_image():
    """示例2: 使用图片显示二维码（需要图形界面）"""
    print("\n示例2: 使用图片显示二维码")
    print("-" * 40)
    
    # 创建登录API实例
    login_api = XHSLoginApi()
    
    # 执行二维码登录，使用图片显示
    cookies_str = login_api.qrcode_login(show_in_terminal=False)
    
    if cookies_str:
        print(f"\n登录成功! Cookies:\n{cookies_str}")
        return cookies_str
    else:
        print("\n登录失败")
        return None

def example_3_step_by_step_qrcode():
    """示例3: 分步执行二维码登录"""
    print("\n示例3: 分步执行二维码登录")
    print("-" * 40)
    
    # 创建登录API实例
    login_api = XHSLoginApi()
    
    # 步骤1: 生成初始cookies
    print("步骤1: 生成初始cookies...")
    cookies = login_api.generate_init_cookies()
    print(f"初始cookies: {cookies}")
    
    # 步骤2: 获取二维码
    print("\n步骤2: 获取二维码...")
    success, msg, qr_data = login_api.generate_qrcode(cookies)
    
    if not success:
        print(f"获取二维码失败: {msg}")
        return None
    
    cookies = qr_data['cookies']
    qr_id = qr_data['qr_id']
    code = qr_data['code']
    qr_url = qr_data['qr_url']
    
    print(f"二维码ID: {qr_id}")
    print(f"二维码code: {code}")
    print(f"二维码URL: {qr_url}")
    
    # 显示二维码
    print("\n请使用小红书APP扫描以下二维码:")
    login_api.show_qrcode_terminal(qr_url)
    
    # 步骤3: 检查二维码状态
    print("\n步骤3: 等待扫码...")
    import time
    
    while True:
        success, msg, cookies = login_api.check_qrcode_status(qr_id, code, cookies)
        
        if success:
            print(f"扫码状态: {msg}")
            break
        elif msg == '二维码已过期':
            print("二维码已过期，请重新获取")
            return None
        else:
            print(f"等待扫码... ({msg})")
            time.sleep(2)  # 每2秒检查一次
    
    # 步骤4: 获取用户信息
    print("\n步骤4: 获取用户信息...")
    success, user_info, cookies = login_api.get_user_info(cookies)
    
    if success:
        print(f"登录成功! 用户: {user_info.get('nickname', '未知')}")
    else:
        print("获取用户信息失败，但cookies可能仍有效")
    
    # 转换cookies为字符串
    cookies_str = login_api.cookies_to_str(cookies)
    print(f"\n最终cookies:\n{cookies_str}")
    
    return cookies_str

def example_4_use_cookies_for_api():
    """示例4: 使用登录后的cookies调用其他API"""
    print("\n示例4: 使用登录后的cookies调用其他API")
    print("-" * 40)
    
    # 首先登录获取cookies
    cookies_str = example_1_simple_qrcode_login()
    
    if not cookies_str:
        print("登录失败，无法继续")
        return
    
    # 导入其他API
    from apis.xhs_pc_apis import XHS_Apis
    
    # 创建API实例
    xhs_api = XHS_Apis()
    
    # 示例：搜索笔记
    print("\n使用cookies搜索笔记...")
    success, msg, result = xhs_api.search_note("小红书", cookies_str)
    
    if success:
        print(f"搜索成功! 找到 {len(result)} 条结果")
        if result:
            # 显示前3条结果
            for i, note in enumerate(result[:3]):
                print(f"\n结果 {i+1}:")
                print(f"  标题: {note.get('title', '无标题')}")
                print(f"  作者: {note.get('user', {}).get('nickname', '未知')}")
                print(f"  点赞: {note.get('likes', 0)}")
    else:
        print(f"搜索失败: {msg}")

def example_5_save_and_load_cookies():
    """示例5: 保存和加载cookies"""
    print("\n示例5: 保存和加载cookies")
    print("-" * 40)
    
    # 首先登录获取cookies
    login_api = XHSLoginApi()
    cookies_str = login_api.qrcode_login(show_in_terminal=True)
    
    if not cookies_str:
        print("登录失败，无法继续")
        return
    
    # 保存cookies到文件
    save_path = "xhs_cookies_saved.txt"
    with open(save_path, 'w', encoding='utf-8') as f:
        f.write(cookies_str)
    print(f"\nCookies已保存到: {os.path.abspath(save_path)}")
    
    # 从文件加载cookies
    print("\n从文件加载cookies...")
    with open(save_path, 'r', encoding='utf-8') as f:
        loaded_cookies = f.read().strip()
    
    print(f"加载的cookies: {loaded_cookies[:50]}...")
    
    # 测试加载的cookies
    cookies_dict = {}
    for item in loaded_cookies.split('; '):
        if '=' in item:
            key, value = item.split('=', 1)
            cookies_dict[key.strip()] = value.strip()
    
    success, user_info, _ = login_api.get_user_info(cookies_dict)
    if success:
        print(f"Cookies有效! 用户: {user_info.get('nickname', '未知')}")
    else:
        print("Cookies无效或已过期")

def main():
    """主函数 - 运行所有示例"""
    print("=" * 60)
    print("小红书二维码登录调用示例")
    print("=" * 60)
    
    print("\n选择要运行的示例:")
    print("1. 最简单的二维码登录")
    print("2. 使用图片显示二维码")
    print("3. 分步执行二维码登录")
    print("4. 使用登录后的cookies调用其他API")
    print("5. 保存和加载cookies")
    print("6. 运行所有示例")
    print("0. 退出")
    
    while True:
        choice = input("\n请输入选择 (0-6): ").strip()
        
        if choice == "0":
            print("退出程序")
            break
        elif choice == "1":
            example_1_simple_qrcode_login()
        elif choice == "2":
            example_2_qrcode_login_with_image()
        elif choice == "3":
            example_3_step_by_step_qrcode()
        elif choice == "4":
            example_4_use_cookies_for_api()
        elif choice == "5":
            example_5_save_and_load_cookies()
        elif choice == "6":
            print("\n运行所有示例...")
            example_1_simple_qrcode_login()
            example_2_qrcode_login_with_image()
            example_3_step_by_step_qrcode()
            example_4_use_cookies_for_api()
            example_5_save_and_load_cookies()
            print("\n所有示例运行完成!")
        else:
            print("无效选择，请重新输入")
        
        print("\n" + "=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"\n程序运行出错: {e}")
        import traceback
        traceback.print_exc()