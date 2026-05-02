#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书API FastAPI封装
提供RESTful API接口调用小红书爬虫功能
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
import sys
import os
from pathlib import Path
import json
import asyncio
from datetime import datetime

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.resolve() / "Splider_XHS"
sys.path.insert(0, str(project_root))
print(f"项目根路径已添加到sys.path: {project_root}")

# 导入小红书API
from apis.xhs_pc_apis import XHS_Apis
from apis.xhs_pc_login_apis import XHSLoginApi
from apis.xhs_creator_apis import XHS_Creator_Apis
from apis.xhs_creator_login_apis import XHSCreatorLoginApi

# 创建FastAPI应用
app = FastAPI(
    title="小红书API服务",
    description="提供小红书数据爬取、内容发布、登录认证等功能的RESTful API接口",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 数据模型定义 ====================

class ResponseModel(BaseModel):
    """统一响应模型"""
    success: bool = Field(..., description="操作是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="时间戳")

class LoginRequest(BaseModel):
    """登录请求"""
    login_type: str = Field(..., description="登录类型: qrcode(二维码) 或 phone(手机验证码)")
    phone: Optional[str] = Field(None, description="手机号(手机登录时需要)")
    zone: str = Field(default="86", description="区号，默认86")

class QRCodeResponse(BaseModel):
    """二维码响应"""
    qr_id: str = Field(..., description="二维码ID")
    code: str = Field(..., description="二维码code")
    qr_url: str = Field(..., description="二维码URL")
    cookies: Dict[str, str] = Field(..., description="初始cookies")

class UserInfo(BaseModel):
    """用户信息"""
    user_id: Optional[str] = None
    nickname: Optional[str] = None
    red_id: Optional[str] = None
    desc: Optional[str] = None
    image: Optional[str] = None
    fans_count: Optional[int] = None
    follows_count: Optional[int] = None

class NoteInfo(BaseModel):
    """笔记信息"""
    note_id: Optional[str] = None
    title: Optional[str] = None
    desc: Optional[str] = None
    type: Optional[str] = None
    user: Optional[Dict[str, Any]] = None
    interact_info: Optional[Dict[str, int]] = None

class SearchNoteRequest(BaseModel):
    """搜索笔记请求"""
    query: str = Field(..., description="搜索关键词")
    require_num: int = Field(default=10, description="需要获取的数量")
    sort_type: int = Field(default=0, description="排序方式: 0综合, 1最新, 2最多点赞, 3最多评论, 4最多收藏")
    note_type: int = Field(default=0, description="笔记类型: 0不限, 1视频, 2普通")
    note_time: int = Field(default=0, description="时间范围: 0不限, 1一天内, 2一周内, 3半年内")
    cookies_str: str = Field(..., description="登录cookies字符串")

class SearchUserRequest(BaseModel):
    """搜索用户请求"""
    query: str = Field(..., description="搜索关键词")
    require_num: int = Field(default=10, description="需要获取的数量")
    cookies_str: str = Field(..., description="登录cookies字符串")

class GetNoteRequest(BaseModel):
    """获取笔记详情请求"""
    note_url: str = Field(..., description="笔记URL")
    cookies_str: str = Field(..., description="登录cookies字符串")

class GetUserRequest(BaseModel):
    """获取用户信息请求"""
    user_url: str = Field(..., description="用户URL")
    cookies_str: str = Field(..., description="登录cookies字符串")

class GetCommentsRequest(BaseModel):
    """获取评论请求"""
    note_url: str = Field(..., description="笔记URL")
    cookies_str: str = Field(..., description="登录cookies字符串")

class PublishNoteRequest(BaseModel):
    """发布笔记请求"""
    title: str = Field(..., description="笔记标题")
    desc: str = Field(..., description="笔记描述")
    media_type: str = Field(..., description="媒体类型: image 或 video")
    type: int = Field(default=0, description="可见性: 0公开, 1私密")
    topics: Optional[List[str]] = Field(default=[], description="话题标签列表")
    location: Optional[str] = Field(None, description="地点")
    cookies_str: str = Field(..., description="创作者cookies字符串")

# ==================== 全局状态管理 ====================

class SessionManager:
    """会话管理器"""
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.pc_login_api = XHSLoginApi()
        self.pc_api = XHS_Apis()
        self.creator_login_api = XHSCreatorLoginApi()
        self.creator_api = XHS_Creator_Apis()
        # 存储二维码检测结果 {qr_id: {"status": str, "result": dict, "done": bool}}
        self.qrcode_results: Dict[str, Dict[str, Any]] = {}

    def create_session(self, session_id: str) -> Dict[str, Any]:
        """创建新会话"""
        self.sessions[session_id] = {
            "created_at": datetime.now(),
            "cookies": {},
            "user_info": None
        }
        return self.sessions[session_id]

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话"""
        return self.sessions.get(session_id)

    def update_session(self, session_id: str, data: Dict[str, Any]):
        """更新会话"""
        if session_id in self.sessions:
            self.sessions[session_id].update(data)

    def delete_session(self, session_id: str):
        """删除会话"""
        if session_id in self.sessions:
            del self.sessions[session_id]

# 全局会话管理器
session_manager = SessionManager()

# ==================== API路由 ====================

@app.get("/", response_model=ResponseModel)
async def root():
    """根路径"""
    return ResponseModel(
        success=True,
        message="小红书API服务运行中",
        data={
            "version": "1.0.0",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    )

@app.get("/health", response_model=ResponseModel)
async def health_check():
    """健康检查"""
    return ResponseModel(
        success=True,
        message="服务健康",
        data={"status": "healthy"}
    )

# ==================== 登录认证API ====================

async def _check_qrcode_background(qr_id: str, code: str, cookies: Dict[str, str]):
    """后台任务：持续检测二维码状态，直到确认扫描结果"""
    session_manager.qrcode_results[qr_id] = {"status": "pending", "result": None, "done": False}
    try:
        # 持续检测直到有结果（最多检测120次，间隔5秒，共10分钟）
        for _ in range(120):
            await asyncio.sleep(5)
            success, msg, updated_cookies = session_manager.pc_login_api.check_qrcode_status(
                qr_id, code, cookies
            )

            if success and msg == "二维码已扫描，请确认登录":
                session_manager.qrcode_results[qr_id] = {
                    "status": "scanned",
                    "result": {"cookies": updated_cookies},
                    "done": False
                }
            elif success and msg == "二维码已确认，请稍后":
                # 登录成功
                user_success, user_info, final_cookies = session_manager.pc_login_api.get_user_info(updated_cookies)
                cookies_str = session_manager.pc_login_api.cookies_to_str(final_cookies)
                session_manager.qrcode_results[qr_id] = {
                    "status": "confirmed",
                    "result": {
                        "user_info": user_info if user_success else None,
                        "cookies": final_cookies,
                        "cookies_str": cookies_str
                    },
                    "done": True
                }
                break
            elif msg == "二维码已失效":
                session_manager.qrcode_results[qr_id] = {
                    "status": "expired",
                    "result": None,
                    "done": True
                }
                break
            elif msg == "二维码未失效，请继续等待":
                # 继续等待
                continue
    except Exception as e:
        session_manager.qrcode_results[qr_id] = {
            "status": "error",
            "result": str(e),
            "done": True
        }

@app.post("/auth/qrcode/init", response_model=ResponseModel)
async def init_qrcode_login(background_tasks: BackgroundTasks):
    """
    初始化二维码登录
    生成初始cookies和二维码，启动后台检测
    """
    try:
        # 生成初始cookies
        cookies = session_manager.pc_login_api.generate_init_cookies()

        # 生成二维码
        success, msg, qr_data = session_manager.pc_login_api.generate_qrcode(cookies)

        if success:
            qr_id = qr_data["qr_id"]
            code = qr_data["code"]
            # 启动后台任务检测二维码状态
            background_tasks.add_task(_check_qrcode_background, qr_id, code, qr_data["cookies"])

            return ResponseModel(
                success=True,
                message="二维码生成成功，正在后台检测扫描状态",
                data={
                    "qr_id": qr_id,
                    "code": code,
                    "qr_url": qr_data["qr_url"],
                    "cookies": qr_data["cookies"]
                }
            )
        else:
            return ResponseModel(
                success=False,
                message=f"二维码生成失败: {msg}",
                data=None
            )
    except Exception as e:
        return ResponseModel(
            success=False,
            message=f"初始化二维码登录失败: {str(e)}",
            data=None
        )

@app.post("/auth/qrcode/check", response_model=ResponseModel)
async def check_qrcode_status(
    qr_id: str,
    code: str,
    cookies: Dict[str, str]
):
    """
    检查二维码扫描状态（从后台检测结果获取）
    """
    try:
        # 优先从后台检测结果获取
        if qr_id in session_manager.qrcode_results:
            result = session_manager.qrcode_results[qr_id]
            if result["done"]:
                status = result["status"]
                if status == "confirmed":
                    return ResponseModel(
                        success=True,
                        message="登录成功",
                        data=result["result"]
                    )
                elif status == "expired":
                    return ResponseModel(
                        success=False,
                        message="二维码已失效",
                        data=None
                    )
                elif status == "error":
                    return ResponseModel(
                        success=False,
                        message=f"检测出错: {result['result']}",
                        data=None
                    )
            else:
                # 检测中
                return ResponseModel(
                    success=True,
                    message=result["status"],
                    data=result["result"]
                )

        # 如果没有后台结果，直接检查（兼容旧逻辑）
        success, msg, updated_cookies = session_manager.pc_login_api.check_qrcode_status(
            qr_id, code, cookies
        )

        result_data = {
            "status": msg,
            "cookies": updated_cookies
        }

        # 如果登录成功，获取用户信息
        if success:
            user_success, user_info, final_cookies = session_manager.pc_login_api.get_user_info(updated_cookies)
            if user_success:
                result_data["user_info"] = user_info
                result_data["cookies"] = final_cookies
                result_data["cookies_str"] = session_manager.pc_login_api.cookies_to_str(final_cookies)

        return ResponseModel(
            success=success,
            message=msg,
            data=result_data
        )
    except Exception as e:
        return ResponseModel(
            success=False,
            message=f"检查二维码状态失败: {str(e)}",
            data=None
        )

@app.post("/auth/phone/send-code", response_model=ResponseModel)
async def send_phone_code(
    phone: str,
    cookies: Optional[Dict[str, str]] = None,
    zone: str = "86"
):
    """
    发送手机验证码
    """
    try:
        # 如果没有提供cookies，生成新的
        if not cookies:
            cookies = session_manager.pc_login_api.generate_init_cookies()

        success, msg, res = session_manager.pc_login_api.send_phone_code(phone, cookies, zone)

        return ResponseModel(
            success=success,
            message=msg,
            data={
                "cookies": cookies,
                "response": res
            }
        )
    except Exception as e:
        return ResponseModel(
            success=False,
            message=f"发送验证码失败: {str(e)}",
            data=None
        )

@app.post("/auth/phone/login", response_model=ResponseModel)
async def phone_login(
    phone: str,
    code: str,
    cookies: Dict[str, str],
    zone: str = "86"
):
    """
    手机验证码登录
    """
    try:
        success, msg, result = session_manager.pc_login_api.login_by_phone(phone, code, cookies, zone)

        if success:
            # 获取用户信息
            user_success, user_info, final_cookies = session_manager.pc_login_api.get_user_info(result["cookies"])
            cookies_str = session_manager.pc_login_api.cookies_to_str(final_cookies)

            return ResponseModel(
                success=True,
                message="登录成功",
                data={
                    "user_info": user_info if user_success else None,
                    "cookies": final_cookies,
                    "cookies_str": cookies_str
                }
            )
        else:
            return ResponseModel(
                success=False,
                message=msg,
                data=None
            )
    except Exception as e:
        return ResponseModel(
            success=False,
            message=f"手机登录失败: {str(e)}",
            data=None
        )

# ==================== 数据爬取API ====================

@app.post("/search/notes", response_model=ResponseModel)
async def search_notes(request: SearchNoteRequest):
    """
    搜索笔记
    """
    try:
        success, msg, note_list = session_manager.pc_api.search_some_note(
            query=request.query,
            require_num=request.require_num,
            cookies_str=request.cookies_str,
            sort_type_choice=request.sort_type,
            note_type=request.note_type,
            note_time=request.note_time
        )

        return ResponseModel(
            success=success,
            message=msg,
            data=note_list
        )
    except Exception as e:
        return ResponseModel(
            success=False,
            message=f"搜索笔记失败: {str(e)}",
            data=None
        )

@app.post("/search/users", response_model=ResponseModel)
async def search_users(request: SearchUserRequest):
    """
    搜索用户
    """
    try:
        success, msg, user_list = session_manager.pc_api.search_some_user(
            query=request.query,
            require_num=request.require_num,
            cookies_str=request.cookies_str
        )

        return ResponseModel(
            success=success,
            message=msg,
            data=user_list
        )
    except Exception as e:
        return ResponseModel(
            success=False,
            message=f"搜索用户失败: {str(e)}",
            data=None
        )

@app.post("/note/info", response_model=ResponseModel)
async def get_note_info(request: GetNoteRequest):
    """
    获取笔记详情
    """
    try:
        success, msg, note_info = session_manager.pc_api.get_note_info(
            url=request.note_url,
            cookies_str=request.cookies_str
        )

        return ResponseModel(
            success=success,
            message=msg,
            data=note_info
        )
    except Exception as e:
        return ResponseModel(
            success=False,
            message=f"获取笔记详情失败: {str(e)}",
            data=None
        )

@app.post("/user/info", response_model=ResponseModel)
async def get_user_info(request: GetUserRequest):
    """
    获取用户信息
    """
    try:
        success, msg, user_info = session_manager.pc_api.get_user_info(
            user_id=request.user_url,
            cookies_str=request.cookies_str
        )

        return ResponseModel(
            success=success,
            message=msg,
            data=user_info
        )
    except Exception as e:
        return ResponseModel(
            success=False,
            message=f"获取用户信息失败: {str(e)}",
            data=None
        )

@app.post("/user/notes", response_model=ResponseModel)
async def get_user_notes(request: GetUserRequest):
    """
    获取用户所有笔记
    """
    try:
        success, msg, note_list = session_manager.pc_api.get_user_all_notes(
            user_url=request.user_url,
            cookies_str=request.cookies_str
        )

        return ResponseModel(
            success=success,
            message=msg,
            data=note_list
        )
    except Exception as e:
        return ResponseModel(
            success=False,
            message=f"获取用户笔记失败: {str(e)}",
            data=None
        )

@app.post("/note/comments", response_model=ResponseModel)
async def get_note_comments(request: GetCommentsRequest):
    """
    获取笔记所有评论
    """
    try:
        success, msg, comment_list = session_manager.pc_api.get_note_all_comment(
            url=request.note_url,
            cookies_str=request.cookies_str
        )

        return ResponseModel(
            success=success,
            message=msg,
            data=comment_list
        )
    except Exception as e:
        return ResponseModel(
            success=False,
            message=f"获取评论失败: {str(e)}",
            data=None
        )

@app.get("/note/no-watermark/video", response_model=ResponseModel)
async def get_no_watermark_video(note_id: str):
    """
    获取无水印视频地址
    """
    try:
        success, msg, video_addr = session_manager.pc_api.get_note_no_water_video(note_id)

        return ResponseModel(
            success=success,
            message=msg,
            data={"video_url": video_addr}
        )
    except Exception as e:
        return ResponseModel(
            success=False,
            message=f"获取无水印视频失败: {str(e)}",
            data=None
        )

@app.get("/note/no-watermark/image", response_model=ResponseModel)
async def get_no_watermark_image(img_url: str):
    """
    获取无水印图片地址
    """
    try:
        success, msg, new_url = session_manager.pc_api.get_note_no_water_img(img_url)

        return ResponseModel(
            success=success,
            message=msg,
            data={"image_url": new_url}
        )
    except Exception as e:
        return ResponseModel(
            success=False,
            message=f"获取无水印图片失败: {str(e)}",
            data=None
        )

# ==================== 内容发布API ====================

@app.post("/creator/qrcode/init", response_model=ResponseModel)
async def init_creator_qrcode():
    """
    初始化创作者平台二维码登录
    """
    try:
        cookies = session_manager.creator_login_api.generate_init_cookies()
        success, msg, qr_data = session_manager.creator_login_api.generate_qrcode(cookies)

        if success:
            return ResponseModel(
                success=True,
                message="创作者平台二维码生成成功",
                data=qr_data
            )
        else:
            return ResponseModel(
                success=False,
                message=f"二维码生成失败: {msg}",
                data=None
            )
    except Exception as e:
        return ResponseModel(
            success=False,
            message=f"初始化创作者二维码登录失败: {str(e)}",
            data=None
        )

@app.post("/creator/note/publish", response_model=ResponseModel)
async def publish_note(request: PublishNoteRequest):
    """
    发布笔记（需要先上传媒体文件）
    """
    try:
        # 构建笔记信息
        note_info = {
            "title": request.title,
            "desc": request.desc,
            "type": request.type,
            "media_type": request.media_type,
            "topics": request.topics,
            "location": request.location,
            "images": [],  # 需要先上传图片
            "video": None,  # 需要先上传视频
        }

        success, msg, res = session_manager.creator_api.post_note(
            noteInfo=note_info,
            cookies_str=request.cookies_str
        )

        return ResponseModel(
            success=success,
            message=msg,
            data=res
        )
    except Exception as e:
        return ResponseModel(
            success=False,
            message=f"发布笔记失败: {str(e)}",
            data=None
        )

@app.get("/creator/notes", response_model=ResponseModel)
async def get_creator_notes(
    cookies_str: str,
    page: int = 1
):
    """
    获取已发布的笔记列表
    """
    try:
        success, msg, notes = session_manager.creator_api.get_all_publish_note_info(
            cookies_str=cookies_str
        )

        return ResponseModel(
            success=success,
            message=msg,
            data=notes
        )
    except Exception as e:
        return ResponseModel(
            success=False,
            message=f"获取已发布笔记失败: {str(e)}",
            data=None
        )

# ==================== 启动配置 ====================

if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("小红书API服务启动中...")
    print("=" * 60)
    print("\nAPI文档:")
    print("  - Swagger UI: http://localhost:8300/docs")
    print("  - ReDoc: http://localhost:8300/redoc")
    print("\n按 Ctrl+C 停止服务")
    print("=" * 60)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8300,
        log_level="info"
    )