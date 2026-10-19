# 微信视频号下载 Skill

支持两种下载方式：直接粘贴分享链接快速下载，或先在官方微信客户端登录、再用独立的 [wx_channel](https://github.com/nobiyou/wx_channel) 工具下载平台提供的最高可用画质。本仓库的 `app.py` 可以打开微信客户端和启动高清工具，本身不提取高清流，也不接收微信 OAuth 授权。

## 安装为 Codex Skill

```powershell
git clone https://github.com/hua2000625-blip/muzi.git "$HOME\.codex\skills\wechat-channels-download"
```

之后可让 Codex 使用 `$wechat-channels-download`。Skill 会根据画质和登录要求选择流程，具体步骤见 [SKILL.md](SKILL.md)。

## 高清方式：登录微信客户端

1. 点“打开微信（扫码登录）”。小程序会启动本机安装的官方微信 Windows 客户端；尚未登录时在微信界面扫码并用手机确认。若已登录，则打开现有会话，不会强制退出或再次显示二维码。
2. 点“获取高清工具”，从 [wx_channel 的官方 GitHub Releases](https://github.com/nobiyou/wx_channel/releases) 获取 Windows **标准版**。首次使用建议下载 ZIP 并完整解压，阅读其中说明。
3. 点“启动高清工具”，选择解压得到的标准版 EXE，确认提示后才会启动。该工具会设置本地流量代理，首次运行可能自动安装 Windows 受信任根证书；用完可参照其文档卸载。小程序不自动下载或安装此工具。
4. 在已登录的微信中打开目标视频。若小程序中已粘贴链接，启动高清工具时会把第一条复制到剪贴板，方便查找视频。点击微信视频号页面内的下载按钮。该工具在微信明确返回原始 `fullUrl` 时使用原始地址，否则按码率选择最高可用规格。
5. 小程序会把所选文件夹作为 `WX_CHANNEL_DOWNLOADS_DIR` 传给高清工具，请在工具中确认实际保存位置。用视频属性或 `ffprobe` 检查分辨率与码率，再与旧文件比较。最高可用画质不保证是发布者上传前的源文件。

该方式依赖已登录的微信客户端播放页面。打开微信并不等于把微信账号 OAuth 授权给本程序；本程序不会读取微信密码、Cookie 或令牌。正式接入[微信开放平台网站应用授权](https://developers.weixin.qq.com/doc/oplatform/Website_App/WeChat_Login/Wechat_Login.html)需要已审核的网站应用、AppID、AppSecret 和回调域名，而该身份登录授权本身不提供视频号媒体下载权限。第三方工具的安装、证书与代理行为以其当前文档为准。

## 快速方式：仅分享链接

需要 Windows 和 Python 3.10 或更新版本；`app.py` 只使用 Python 标准库。

```powershell
python app.py --download "https://weixin.qq.com/sph/EXAMPLE123" --output "D:\Videos"
python app.py
```

第一条命令下载一条链接；第二条命令打开图形界面。点“免登录下载”可一次粘贴多条链接。当前快速方式优先下载解析服务返回的 H.264 MP4，并直接保存收到的字节，不再次压缩。它不会查询平台的完整清晰度列表。

快速方式会把分享链接发送给第三方解析服务 [v.mtotech.com](https://v.mtotech.com/)，视频文件则直接从 `finder.video.qq.com` 下载。服务并非微信官方接口，可用性与视频地址有效期可能变化。

## 打包小程序

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install pyinstaller
powershell -ExecutionPolicy Bypass -File .\build.ps1
```

生成的压缩包在 `dist/微信视频号小程序.zip`。它包含启动入口和免登录下载器，不包含 `wx_channel`。仓库不包含 exe、下载视频或虚拟环境。请只保存你有权下载的内容。

