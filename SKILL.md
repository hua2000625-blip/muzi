---
name: wechat-channels-download
description: Download WeChat Channels videos from weixin.qq.com/sph share links to local MP4 files without user login. Use for link-based downloads or the bundled Windows desktop app; requires a reachable third-party parser.
---

# WeChat Channels link download

Use this skill when the user provides a `https://weixin.qq.com/sph/...` share link and asks to save its video. The helper uses a public, unofficial parser; the user's link is sent to `v.mtotech.com`, then the MP4 is downloaded from `finder.video.qq.com`. It does not ask the user to log in to WeChat or Tencent Yuanbao.

## Download

On Windows with Python 3.10 or newer, run the adjacent `app.py`:

```powershell
python app.py --download "https://weixin.qq.com/sph/EXAMPLE123" --output "D:\Videos"
```

Replace the example link and output folder with the user's values. For several links, run the command once per link. The helper uses Python's standard library; no browser, FFmpeg, API key, or WeChat session is needed. Without arguments, `python app.py` opens the desktop interface.

Check the command's exit status and the saved file before reporting success. A successful download is an MP4 with a validated header and complete response length when the server provides one. If the third-party parser or video URL fails, report the actual error and stop; do not substitute a login or QR-code workflow when the user requested a login-free download.

## Distribution

`build.ps1` packages the Windows desktop app with PyInstaller. `README.md` has human-facing usage instructions. Keep generated `dist/`, virtual environments, and downloaded videos out of the Skill repository.

The parser is not an official WeChat API and may change or stop working. Tell the user about the third-party link submission when it matters to their decision, and save only content they are authorized to keep.

