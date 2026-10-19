# 微信视频号链接下载 Skill

输入 `https://weixin.qq.com/sph/...` 分享链接，将视频保存为 MP4。支持 Codex Skill、命令行和 Windows 图形界面。用户无需登录微信或腾讯元宝，也无需扫码。

## 安装为 Codex Skill

将本仓库克隆到 Codex 的 skills 目录：

```powershell
git clone https://github.com/hua2000625-blip/muzi.git "$HOME\.codex\skills\wechat-channels-download"
```

之后可以让 Codex 使用 `$wechat-channels-download` 处理视频号分享链接。Skill 的指令见 [SKILL.md](SKILL.md)。

## 直接运行

需要 Windows 和 Python 3.10 或更新版本。源码只使用 Python 标准库。

```powershell
python app.py --download "https://weixin.qq.com/sph/EXAMPLE123" --output "D:\Videos"
python app.py
```

第一条命令下载视频；第二条命令打开图形界面，可以一次粘贴多条链接。保存目录默认是用户的 Downloads 文件夹下的“微信视频号”。

## 打包 Windows 小程序

打包需要 PyInstaller：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install pyinstaller
powershell -ExecutionPolicy Bypass -File .\build.ps1
```

生成的压缩包在 `dist/微信视频号小程序.zip`。仓库不包含 exe、下载视频或虚拟环境。

## 依赖与限制

程序使用公开的第三方解析服务 [v.mtotech.com](https://v.mtotech.com/) 将分享链接解析为腾讯视频 CDN 地址。分享链接会发送给该服务；视频文件直接从 `finder.video.qq.com` 下载。该服务不是微信官方接口，可用性和返回地址的有效期可能变化。

程序只接受腾讯视频域名的下载地址，并验证返回内容是 MP4。请只下载你有权保存的内容。

