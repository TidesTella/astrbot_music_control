# 🎵 LX Music（洛雪音乐助手）联动插件
> 本插件是 [LX Music](https://github.com/lyswhut/lx-music-desktop)（洛雪音乐助手）的 AstrBot 联动控制插件。  
> **需要先安装并配置好 LX Music 本体，本插件才能正常工作。**
---
## ⚠️ 前置要求
**本插件是 LX Music 的遥控器，不包含播放器本身！**
在使用本插件前，请确保：
1. ✅ **已下载并安装** [LX Music 桌面版](https://github.com/lyswhut/lx-music-desktop/releases)
2. ✅ **已启动 LX Music**（运行时保持后台运行）
3. ✅ **已在 LX Music 中开启开放 API 服务**（设置 → 开放 API 服务 → 启用）
4. ✅ **记下 API 端口**（默认 `23330`）
---
## ✨ 功能特性
本插件通过 LX Music 的 **HTTP API** + **Scheme URL** 双通道与播放器通信：
| 功能 | 实现方式 |
|------|---------|
| 查看播放状态 | HTTP API（`/status`） |
| 播放/暂停/切歌/音量/跳转 | HTTP API（`/play`、`/pause`、`/skip-next` 等） |
| 收藏/取消收藏 | HTTP API（`/collect`、`/uncollect`） |
| 搜索歌曲 | Scheme URL（`lxmusic://music/search/xxx`） |
| 搜索并播放 | Scheme URL（`lxmusic://music/searchPlay/xxx`） |
---
## 📋 命令列表
所有命令统一使用 `/music` 前缀：
| 命令 | 说明 | 示例 |
|------|------|------|
| `/music status` | 查看当前播放状态 | `/music status` |
| `/music play` | 继续播放 | `/music play` |
| `/music play 歌曲名` | 搜索并立即播放 | `/music play 反乌托邦` |
| `/music playnext 歌曲名` | 搜索并加入稍后播放 | `/music playnext 反乌托邦` |
| `/music pause` | 暂停播放 | `/music pause` |
| `/music next` | 下一曲 | `/music next` |
| `/music prev` | 上一曲 | `/music prev` |
| `/music volume 数值` | 调整音量（1-100） | `/music volume 50` |
| `/music seek 秒数` | 跳转到指定时间（秒） | `/music seek 90` |
| `/music search 关键词` | 在 LX Music 中搜索歌曲 | `/music search 周杰伦` |
| `/music collect` | 收藏当前歌曲 | `/music collect` |
| `/music uncollect` | 取消收藏 | `/music uncollect` |
---
## 🔧 配置步骤
### 第一步：在 LX Music 中开启 API 服务
1. 打开 LX Music 桌面版
2. 进入 **设置** → **开放 API 服务**
3. 开启 **启用开放 API 服务**
4. 记下端口号（默认 `23330`）
### 第二步：在 AstrBot 中配置插件
在 AstrBot WebUI → 插件配置 → `astrbot_music_control` 中填写：
| 配置项 | 说明 | 示例 |
|--------|------|------|
| `base_url` | LX Music API 地址 | `http://127.0.0.1:23330` |
| `api_key` | API Key（如未设置则留空） | 留空 |
| `default_filter` | 状态返回字段 | 保持默认 |
### 第三步：重启 AstrBot
配置完成后重启 AstrBot，插件即可生效。
---
## 🎯 两种搜索方式说明
| 命令 | 行为 | 适合场景 |
|------|------|---------|
| `/music search 歌曲名` | 在 LX Music 中**打开搜索页面**，结果由你手动选择播放 | 想浏览搜索结果再决定 |
| `/music play 歌曲名` | 搜索后**直接播放**匹配的第一首歌 | 明确想听某首歌，快速播放 |
---
## 🏗️ 工作原理
用户 → AstrBot → 本插件 → LX Music（HTTP API / Scheme URL）→ 播放器响应
- **HTTP API**：用于状态查询、播放控制、音量调节、收藏等
- **Scheme URL**（`lxmusic://`）：用于搜索、搜索播放等操作，无需认证
---