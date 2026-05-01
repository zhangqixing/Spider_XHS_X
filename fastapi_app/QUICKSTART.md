# 快速启动指南

## 一、启动FastAPI服务

### Windows用户

```bash
# 方法1: 双击启动脚本
Spider_XHS/fastapi_app/start_server.bat

# 方法2: 命令行启动
cd Spider_XHS
python -m fastapi_app.main
```

### Linux/Mac用户

```bash
cd Spider_XHS
python -m fastapi_app.main
```

### 看到以下输出表示启动成功

```
============================================================
小红书API服务启动中...
============================================================

API文档:
  - Swagger UI: http://localhost:8000/docs
  - ReDoc: http://localhost:8000/redoc

按 Ctrl+C 停止服务
============================================================
```

## 二、访问API文档

打开浏览器访问：
- http://localhost:8300/docs (Swagger UI)
- http://localhost:8300/redoc (ReDoc)

## 三、测试API

### 使用Swagger UI测试

1. 打开 http://localhost:8300/docs
2. 点击任意API接口
3. 点击 "Try it out"
4. 填写参数
5. 点击 "Execute"
6. 查看响应结果

### 使用curl测试

```bash
# 健康检查
curl http://localhost:8300/health

# 初始化二维码登录
curl -X POST http://localhost:8300/auth/qrcode/init
```

## 四、使用C#客户端

### 1. 编译项目

```bash
cd Spider_XHS/csharp_client
dotnet build
```

### 2. 运行示例

```bash
dotnet run
```

### 3. 预期输出

```
========================================
小红书API客户端使用示例
========================================

1. 健康检查...
   状态: 健康
   消息: 服务健康

2. 二维码登录示例...
   二维码ID: qr_1234567890
   二维码URL: https://www.xiaohongshu.com/qrcode/qr_1234567890
   请使用小红书APP扫描二维码

   等待扫码...
   [1] 状态: 请扫描二维码
   [2] 状态: 请确认登录
   [3] 状态: 验证成功

   登录成功!
   用户: 测试用户
   RedID: red_123456
   Cookies: a1=xxx; web_session=yyy; ...

3. 搜索笔记示例...
   找到 5 条笔记:
   - 美食分享 (作者: 美食博主)
   - 今日午餐 (作者: 吃货日记)
   ...
```

## 五、常见问题

### Q1: 启动失败提示"ModuleNotFoundError"

**解决方案:**
```bash
cd Spider_XHS/fastapi_app
pip install -r requirements.txt
```

### Q2: C#客户端连接失败

**解决方案:**
1. 确认FastAPI服务已启动
2. 检查防火墙是否允许8300端口
3. 确认访问地址正确（http://localhost:8300）

### Q3: 二维码登录失败

**解决方案:**
1. 检查Node.js是否安装: `node --version`
2. 安装crypto-js: `cd Spider_XHS && npm install`
3. 查看FastAPI控制台错误信息

## 六、下一步

1. **查看完整文档**: 阅读 `fastapi_app/README.md`
2. **修改配置**: 根据需要修改API端口、超时等配置
3. **添加功能**: 参考文档添加自定义API接口
4. **部署上线**: 使用Docker或gunicorn部署到生产环境

## 七、技术支持

如遇问题，请检查：
1. Python版本（建议3.8+）
2. Node.js版本（建议16+）
3. 依赖包是否完整安装
4. 端口是否被占用
5. 防火墙设置

🎯