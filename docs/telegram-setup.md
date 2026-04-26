# Telegram 配置教程 / Telegram Setup Guide

一步一步教你配置 Telegram 机器人和 API 凭证。

## Step 1: 创建 Telegram Bot

1. 在 Telegram 搜索 **@BotFather**
2. 发送 `/newbot`
3. 给你的机器人取个名字（比如 "My Video Brain"）
4. 给你的机器人取个用户名（比如 "my_video_brain_bot"）
5. BotFather 会给你一个 **Bot Token**，格式像这样：
   ```
   1234567890:ABCDefGhIjKlMnOpQrStUvWxYz
   ```
6. 把这个 Token 保存好

## Step 2: 获取 API ID 和 Hash

这一步是为了突破 20MB 的文件下载限制。

1. 打开 https://my.telegram.org
2. 输入你的手机号（带国际区号，比如 +86xxxxx）
3. 输入收到的验证码
4. 点击 **"API development tools"**
5. 填写：
   - **App title**: 随便写，比如 "Video Brain"
   - **Short name**: 随便写，比如 "vtb"
   - **URL**: 可以留空
   - **Platform**: 选 "Other"
   - **Description**: 可以留空
6. 点击 **Create application**
7. 你会看到：
   - **App api_id**: 一串数字（这就是 API ID）
   - **App api_hash**: 一串字母数字（这就是 API Hash）

## Step 3: 配置 .env 文件

在项目根目录创建 `.env` 文件：

```env
TELEGRAM_BOT_TOKEN=1234567890:ABCDefGhIjKlMnOpQrStUvWxYz
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=abcdef1234567890abcdef1234567890
```

## Step 4: 验证配置

```python
from src import is_available, check_dependencies

# 检查 Pyrogram 配置
print(f"大视频下载: {'✅ 已配置' if is_available() else '❌ 未配置'}")

# 检查 ffmpeg 和 whisper
deps = check_dependencies()
print(f"ffmpeg: {'✅' if deps['ffmpeg'] else '❌'}")
print(f"whisper: {'✅' if deps['whisper'] else '❌'}")
```

全部显示 ✅ 就说明配置成功了！

## 常见问题

### Q: API ID 看起来只有一位数（比如 6），正常吗？
A: 有些早期注册的 API ID 确实很短，能用就行。

### Q: 我在中国，my.telegram.org 打不开？
A: 需要科学上网才能访问。

### Q: Bot Token 过期了怎么办？
A: 找 @BotFather 发 `/revoke` 重新生成。
