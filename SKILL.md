---
name: wechat-channels-download
description: Save WeChat Channels videos from weixin.qq.com/sph share links. Use a logged-in WeChat playback page for the highest available quality, or the bundled link parser for a quick download when login is unwanted.
---

# WeChat Channels download

Choose the route that matches the user's quality and login requirements. For platform-level playback quality, prefer the logged-in route below. The adjacent `app.py` is a quick link downloader; it does not discover all playback quality variants and must not be described as a high-quality guarantee.

## Highest available quality with WeChat login

1. Check whether [nobiyou/wx_channel](https://github.com/nobiyou/wx_channel) is already available. If not, consult its [current release](https://github.com/nobiyou/wx_channel/releases) and installation instructions. This is a separate third-party tool, not bundled with this Skill or `app.py`.
2. Before starting it for the first time, tell the user that it uses a local traffic proxy and installs a trusted certificate on Windows. Get their explicit approval for that system change. Accepting a WeChat login alone does not authorize certificate installation.
3. Have the user log in by scanning in the official WeChat interface and open the target video in the logged-in playback page. Never request or store their password, cookies, or session tokens.
4. Use the tool's single-video download menu. Prefer the explicitly returned original address when available; otherwise choose the highest available quality specification. The tool's documentation distinguishes these choices. Save the returned media stream without re-encoding.
5. Verify the saved video's resolution and, when available, bitrate with `ffprobe` or file metadata. Compare with any existing download before claiming a quality improvement. For the previously tested share link, the quick download was 1024×576; file size or H.265 encoding alone does not prove greater quality.

If the logged-in page offers no stream above the previous version, say so. The highest stream available to a viewer is not necessarily the uploader's original file. Do not manufacture detail by upscaling and call it a higher-quality source.

The release tool provides `wx_channel.exe --uninstall` for removing its certificate; refer to its current documentation before using that command.

## Quick download from a share link

If the user prefers no login, or accepts the quality limit, run the adjacent `app.py` on Windows with Python 3.10 or newer:

```powershell
python app.py --download "https://weixin.qq.com/sph/EXAMPLE123" --output "D:\Videos"
```

Without arguments, `python app.py` opens the local GUI. It sends the share link to the unofficial parser `v.mtotech.com` and downloads the returned MP4 from `finder.video.qq.com`. It currently prefers the H.264 URL. Tell the user about the third-party link submission when relevant. Check the exit status and saved file before reporting success; if parsing fails, report the actual error.

## Distribution

`build.ps1` packages the quick-download Windows app with PyInstaller. `README.md` explains both routes. Keep generated `dist/`, virtual environments, browser profiles, login data, and downloaded videos out of the Skill repository. Save only content the user is authorized to keep.

