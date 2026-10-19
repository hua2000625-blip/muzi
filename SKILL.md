---
name: wechat-channels-download
description: Save WeChat Channels videos from weixin.qq.com/sph share links. Use a logged-in official WeChat desktop playback route for the highest available quality, or the bundled link parser for a quick download.
---

# WeChat Channels download

Choose the route that matches the user's quality and login requirements. For platform-level playback quality, prefer the logged-in route below. The adjacent `app.py` offers both a quick link downloader and a launcher for the separate `wx_channel` tool; it does not extract high-quality streams itself.

## Highest available quality with WeChat login

1. Check whether the standard Windows edition of [nobiyou/wx_channel](https://github.com/nobiyou/wx_channel) is already available. If not, consult its [current release](https://github.com/nobiyou/wx_channel/releases) and installation instructions. This is a separate third-party tool, not bundled with this Skill or `app.py`.
2. Before starting it for the first time, tell the user that it uses a local traffic proxy and installs a trusted certificate on Windows. Get their explicit approval for that system change. Accepting a WeChat login alone does not authorize certificate installation.
3. The GUI's **打开微信（扫码登录）** button launches the installed official WeChat desktop client. If the client is not logged in, the user scans its QR code and confirms on their phone; if already logged in, it opens the existing session. This is desktop-client login, not OAuth authorization to this Skill.
4. The separate **启动高清工具** button asks the user to choose the standard tool's EXE, shows the certificate/proxy disclosure, and starts it only after the user accepts. The **获取高清工具** button opens its official release page. The GUI passes its selected folder as `WX_CHANNEL_DOWNLOADS_DIR`; verify the actual save location in the third-party tool. The GUI copies the first pasted share link to the clipboard to help locate the target video. Never request or store the user's password, cookies, or session tokens.
5. Open the target video in the logged-in WeChat playback page and use the tool's single-video download menu. Its documented behavior is to use a clearly returned original `fullUrl` when available; otherwise it automatically picks the highest available `spec` by bitrate. Save the returned media stream without re-encoding.
6. Verify the saved video's resolution and, when available, bitrate with `ffprobe` or file metadata. Compare with any existing download before claiming a quality improvement. For the previously tested share link, the quick download was 1024×576; file size or H.265 encoding alone does not prove greater quality.

Official WeChat website OAuth login requires an approved website application, AppID, AppSecret, and a registered callback domain. Its documented `snsapi_login` scope handles identity authorization; it is not a substitute for a logged-in desktop playback session or a video download grant. Do not describe opening the WeChat client as OAuth authorization to this Skill.

If the logged-in page offers no stream above the previous version, say so. The highest stream available to a viewer is not necessarily the uploader's original file. Do not manufacture detail by upscaling and call it a higher-quality source.

The release tool provides `wx_channel.exe --uninstall` for removing its certificate; refer to its current documentation before using that command.

## Quick download from a share link

If the user prefers no login, or accepts the quality limit, run the adjacent `app.py` on Windows with Python 3.10 or newer:

```powershell
python app.py --download "https://weixin.qq.com/sph/EXAMPLE123" --output "D:\Videos"
```

Without arguments, `python app.py` opens the local GUI. Its **免登录下载** button sends the share link to the unofficial parser `v.mtotech.com` and downloads the returned MP4 from `finder.video.qq.com`. It currently prefers the H.264 URL. Tell the user about the third-party link submission when relevant. Check the exit status and saved file before reporting success; if parsing fails, report the actual error.

## Distribution

`build.ps1` packages the Windows GUI and quick downloader with PyInstaller. The external high-quality tool stays separate. `README.md` explains both routes. Keep generated `dist/`, virtual environments, browser profiles, login data, and downloaded videos out of the Skill repository. Save only content the user is authorized to keep.

