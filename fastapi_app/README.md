# 小红书API FastAPI封装 + C#客户端

本项目将小红书爬虫API封装成FastAPI服务，并提供C#客户端组件调用。

## 项目结构

```
Spider_XHS/
├── fastapi_app/              # FastAPI应用
│   ├── main.py              # FastAPI主程序
│   ├── requirements.txt     # Python依赖
│   └── start_server.bat     # Windows启动脚本
├── csharp_client/            # C#客户端
│   ├── XHSApiService.cs     # API客户端类
│   ├── Program.cs           # 使用示例
│   └── XHSApiClient.csproj  # 项目文件
└── apis/                     # 原始API（已存在）
```

## 一、FastAPI服务

### 1. 安装依赖

```bash
cd Spider_XHS/fastapi_app
pip install -r requirements.txt
```

### 2. 启动服务

**Windows:**
```bash
# 方法1: 使用启动脚本
start_server.bat

# 方法2: 直接运行
cd Spider_XHS
python -m fastapi_app.main
```

**Linux/Mac:**
```bash
cd Spider_XHS
python -m fastapi_app.main
```

### 3. 访问API文档

启动服务后，访问以下地址查看API文档：

- **Swagger UI**: http://localhost:8300/docs
- **ReDoc**: http://localhost:8300/redoc

### 4. API接口列表

#### 认证相关

| 接口 | 方法 | 说明 |
|------|------|------|
| `/auth/qrcode/init` | POST | 初始化二维码登录 |
| `/auth/qrcode/check` | POST | 检查二维码状态 |
| `/auth/phone/send-code` | POST | 发送手机验证码 |
| `/auth/phone/login` | POST | 手机验证码登录 |

#### 数据爬取

| 接口 | 方法 | 说明 |
|------|------|------|
| `/search/notes` | POST | 搜索笔记 |
| `/search/users` | POST | 搜索用户 |
| `/note/info` | POST | 获取笔记详情 |
| `/user/info` | POST | 获取用户信息 |
| `/user/notes` | POST | 获取用户所有笔记 |
| `/note/comments` | POST | 获取笔记评论 |
| `/note/no-watermark/video` | GET | 获取无水印视频 |
| `/note/no-watermark/image` | GET | 获取无水印图片 |

#### 内容发布

| 接口 | 方法 | 说明 |
|------|------|------|
| `/creator/qrcode/init` | POST | 创作者平台二维码登录 |
| `/creator/note/publish` | POST | 发布笔记 |
| `/creator/notes` | GET | 获取已发布笔记 |

### 5. 使用示例（Python）

```python
import requests
import time

# 1. 初始化二维码登录
response = requests.post("http://localhost:8300/auth/qrcode/init")
result = response.json()

if result["success"]:
    qr_data = result["data"]
    print(f"二维码URL: {qr_data['qr_url']}")
    print("请使用小红书APP扫描二维码")

    # 2. 轮询检查二维码状态
    while True:
        time.sleep(2)

        check_response = requests.post(
            "http://localhost:8300/auth/qrcode/check",
            json={
                "qr_id": qr_data["qr_id"],
                "code": qr_data["code"],
                "cookies": qr_data["cookies"]
            }
        )
        check_result = check_response.json()

        if check_result["success"]:
            print(f"登录成功: {check_result['data']['user_info']['nickname']}")
            cookies_str = check_result['data']['cookies_str']
            break

    # 3. 搜索笔记
    search_response = requests.post(
        "http://localhost:8300/search/notes",
        json={
            "query": "美食",
            "cookies_str": cookies_str,
            "require_num": 10
        }
    )
    search_result = search_response.json()

    if search_result["success"]:
        for note in search_result["data"]:
            print(f"笔记: {note['title']}")
```

## 二、C#客户端

### 1. 项目配置

创建新的C#项目或添加到现有项目：

```bash
# 创建新项目
dotnet new console -n XHSApiClientExample
cd XHSApiClientExample

# 添加必要的包
dotnet add package System.Net.Http.Json
dotnet add package System.Text.Json
```

### 2. 添加客户端类

将 `XHSApiService.cs` 添加到项目中。

### 3. 使用示例

```csharp
using XHSApiClient;

// 创建客户端
using var client = new XHSApiClient("http://localhost:8300");

// 1. 健康检查
var health = await client.HealthCheckAsync();
Console.WriteLine($"服务状态: {health.Success}");

// 2. 二维码登录
var qrLogin = await client.InitQRCodeLoginAsync();
if (qrLogin.Success)
{
    Console.WriteLine($"二维码URL: {qrLogin.Data.QRUrl}");

    // 轮询检查状态
    for (int i = 0; i < 30; i++)
    {
        await Task.Delay(2000);

        var status = await client.CheckQRCodeStatusAsync(
            qrLogin.Data.QRId,
            qrLogin.Data.Code,
            qrLogin.Data.Cookies
        );

        if (status.Success && status.Data?.UserInfo != null)
        {
            Console.WriteLine($"登录成功: {status.Data.UserInfo.Nickname}");
            var cookiesStr = status.Data.CookiesStr;

            // 3. 搜索笔记
            var searchResult = await client.SearchNotesAsync(
                query: "美食",
                cookiesStr: cookiesStr,
                requireNum: 10
            );

            if (searchResult.Success)
            {
                foreach (var note in searchResult.Data)
                {
                    Console.WriteLine($"笔记: {note.Title}");
                }
            }

            break;
        }
    }
}

// 4. 手机验证码登录
var phoneCode = await client.SendPhoneCodeAsync("13800138000");
if (phoneCode.Success)
{
    Console.WriteLine("验证码已发送");
    // 用户输入验证码
    var code = Console.ReadLine();

    var loginResult = await client.PhoneLoginAsync(
        "13800138000",
        code,
        phoneCode.Data.Cookies
    );

    if (loginResult.Success)
    {
        Console.WriteLine($"登录成功: {loginResult.Data.UserInfo.Nickname}");
    }
}

// 5. 获取无水印视频
var videoResult = await client.GetNoWatermarkVideoAsync("note_id");
if (videoResult.Success)
{
    Console.WriteLine($"视频地址: {videoResult.Data.VideoUrl}");
}
```

### 4. 编译运行

```bash
# 编译
dotnet build

# 运行
dotnet run
```

## 三、API详细说明

### 1. 二维码登录流程

```
1. 调用 /auth/qrcode/init 获取二维码
2. 显示二维码给用户扫描
3. 轮询调用 /auth/qrcode/check 检查状态
4. 登录成功后获取 cookies_str
5. 使用 cookies_str 调用其他API
```

### 2. 手机验证码登录流程

```
1. 调用 /auth/phone/send-code 发送验证码
2. 用户输入验证码
3. 调用 /auth/phone/login 完成登录
4. 登录成功后获取 cookies_str
```

### 3. 搜索笔记参数说明

```json
{
  "query": "搜索关键词",
  "cookies_str": "登录cookies",
  "require_num": 10,           // 获取数量
  "sort_type": 0,              // 排序: 0综合, 1最新, 2最多点赞, 3最多评论, 4最多收藏
  "note_type": 0,              // 类型: 0不限, 1视频, 2普通
  "note_time": 0               // 时间: 0不限, 1一天内, 2一周内, 3半年内
}
```

### 4. 发布笔记流程

```
1. 先上传图片或视频（需要实现文件上传接口）
2. 调用 /creator/note/publish 发布笔记
```

## 四、部署说明

### 1. 本地开发

```bash
# 启动FastAPI服务
python -m fastapi_app.main

# 运行C#客户端
dotnet run
```

### 2. 生产部署

**FastAPI部署:**

```bash
# 使用gunicorn + uvicorn
pip install gunicorn uvicorn

gunicorn fastapi_app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8300
```

**使用Docker:**

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . /app

RUN pip install -r fastapi_app/requirements.txt

EXPOSE 8000
CMD ["python", "-m", "fastapi_app.main"]
```

**C#客户端配置:**

修改API基础URL为生产环境地址：

```csharp
var client = new XHSApiClient("https://your-api-server.com");
```

## 五、注意事项

1. **Node.js依赖**: 确保Spider_XHS项目已安装Node.js依赖（crypto-js, jsdom）
2. **Cookies管理**: 登录后的cookies需要妥善保存，用于后续API调用
3. **请求频率**: 避免频繁请求，建议添加延迟
4. **错误处理**: 所有API返回统一的响应格式，注意检查success字段
5. **超时设置**: C#客户端默认超时30秒，可根据需要调整

## 六、故障排除

### 1. FastAPI服务无法启动

```bash
# 检查依赖
pip install -r fastapi_app/requirements.txt

# 检查端口占用
netstat -ano | findstr :8300
```

### 2. C#客户端连接失败

- 确认FastAPI服务已启动
- 检查防火墙设置
- 确认API地址正确

### 3. 登录失败

- 检查Node.js环境
- 确认crypto-js已安装
- 查看FastAPI日志

## 七、扩展开发

### 1. 添加新的API接口

在 `fastapi_app/main.py` 中添加新的路由：

```python
@app.post("/new-endpoint", response_model=ResponseModel)
async def new_endpoint(request: NewRequest):
    # 实现逻辑
    return ResponseModel(success=True, message="成功", data=result)
```

### 2. 添加新的C#方法

在 `XHSApiService.cs` 中添加新方法：

```csharp
public async Task<ApiResponse<T>> NewMethodAsync(...)
{
    return await PostAsync<T>("/new-endpoint", new { ... });
}
```

## 八、许可证

本项目基于原Spider_XHS项目，请遵守原项目的许可证规定。