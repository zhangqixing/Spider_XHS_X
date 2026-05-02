#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书PC登录API测试
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(project_root))

from apis.xhs_pc_login_apis import XHSLoginApi


def test_generate_init_cookies():
    """测试生成初始cookies"""
    print("\n=== 测试 generate_init_cookies ===")
    api = XHSLoginApi()
    cookies = api.generate_init_cookies()
    assert 'a1' in cookies, "缺少 a1"
    assert 'webId' in cookies, "缺少 webId"
    print(f"cookies生成成功: {cookies}")
    return cookies


def test_generate_qrcode(cookies):
    """测试生成二维码"""
    print("\n=== 测试 generate_qrcode ===")
    api = XHSLoginApi()
    success, msg, qr_data = api.generate_qrcode(cookies)
    assert success, f"二维码生成失败: {msg}"
    assert 'qr_id' in qr_data, "缺少 qr_id"
    assert 'code' in qr_data, "缺少 code"
    assert 'qr_url' in qr_data, "缺少 qr_url"
    print(f"二维码生成成功:")
    print(f"  qr_id: {qr_data['qr_id']}")
    print(f"  code: {qr_data['code']}")
    print(f"  qr_url: {qr_data['qr_url']}")
    api.show_qrcode_terminal(qr_data['qr_url'])
    return qr_data


def test_check_qrcode_status(qr_data, cookies):
    """测试检查二维码状态"""
    print("\n=== 测试 check_qrcode_status ===")
    api = XHSLoginApi()
    success, msg, updated_cookies = api.check_qrcode_status(
        qr_data['qr_id'], qr_data['code'], cookies
    )
    print(f"状态: {msg}")
    print(f"success: {success}")
    return success, msg, updated_cookies


def test_cookies_to_str(cookies):
    """测试cookies转字符串"""
    print("\n=== 测试 cookies_to_str ===")
    api = XHSLoginApi()
    cookies_str = api.cookies_to_str(cookies)
    print(f"cookies字符串: {cookies_str[:100]}...")
    return cookies_str


def test_get_user_info(cookies):
    """测试获取用户信息"""
    print("\n=== 测试 get_user_info ===")
    api = XHSLoginApi()
    success, user_info, updated_cookies = api.get_user_info(cookies)
    print(f"success: {success}")
    if success:
        print(f"用户昵称: {user_info.get('nickname')}")
        print(f"RedID: {user_info.get('red_id')}")
    return success, user_info, updated_cookies


def test_send_phone_code(cookies):
    """测试发送手机验证码"""
    print("\n=== 测试 send_phone_code ===")
    api = XHSLoginApi()
    phone = input("请输入手机号: ") or "13800138000"
    success, msg, res = api.send_phone_code(phone, cookies)
    print(f"success: {success}, msg: {msg}")
    return success, msg, res


def test_login_by_phone(phone, code, cookies):
    """测试手机验证码登录"""
    print("\n=== 测试 login_by_phone ===")
    api = XHSLoginApi()
    success, msg, result = api.login_by_phone(phone, code, cookies)
    print(f"success: {success}, msg: {msg}")
    return success, msg, result


if __name__ == '__main__':
    api = XHSLoginApi()

    print("=" * 50)
    print("小红书PC登录API测试")
    print("=" * 50)

    # 测试1: 生成初始cookies
    cookies = test_generate_init_cookies()

    # 测试2: 生成二维码
    qr_data = test_generate_qrcode(cookies)

    # 测试3: 检查二维码状态
    test_check_qrcode_status(qr_data, cookies)

    # 测试4: cookies转字符串
    test_cookies_to_str(cookies)

    # 测试5: 获取用户信息
    test_get_user_info(cookies)

    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)
