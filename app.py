"""Download a WeChat Channels MP4 from a share link, without user login."""

from __future__ import annotations

import argparse
import json
import os
import queue
import re
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import ProxyHandler, Request, build_opener, getproxies, urlopen


PARSER_URL = "https://v.mtotech.com/api/resolve"
LINK_RE = re.compile(r"https://weixin\.qq\.com/sph/[A-Za-z0-9_-]+/?", re.I)
DEFAULT_OUTPUT = Path.home() / "Downloads" / "微信视频号"
CHUNK_SIZE = 1024 * 1024


class DownloadError(Exception):
    pass


class Cancelled(Exception):
    pass


def extract_links(text: str) -> list[str]:
    return list(dict.fromkeys(match.group(0).rstrip("/") for match in LINK_RE.finditer(text)))


def safe_name(value: str, limit: int) -> str:
    value = re.sub(r'[<>:"/\\|?*\x00-\x1f]', " ", value)
    value = re.sub(r"\s+", " ", value).strip(" .")
    return value[:limit].rstrip(" .") or "视频"


def open_request(request: Request, timeout: int):
    try:
        return urlopen(request, timeout=timeout)
    except HTTPError:
        raise
    except URLError:
        if not getproxies():
            raise
        # A stale system proxy must not prevent an otherwise reachable URL.
        return build_opener(ProxyHandler({})).open(request, timeout=timeout)


def parse_video(link: str) -> dict:
    if not LINK_RE.fullmatch(link):
        raise DownloadError("请输入完整的视频号分享链接。")
    request = Request(
        PARSER_URL,
        data=json.dumps({"url": link}).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Origin": "https://v.mtotech.com",
            "Referer": "https://v.mtotech.com/",
            "User-Agent": "Mozilla/5.0 WeChat-Video-Local/2.0",
        },
        method="POST",
    )
    try:
        with open_request(request, timeout=100) as response:
            result = json.load(response)
    except HTTPError as exc:
        raise DownloadError(f"解析服务返回 HTTP {exc.code}。") from exc
    except (URLError, TimeoutError, OSError, ValueError) as exc:
        raise DownloadError(f"解析服务连接失败：{exc}") from exc
    if not isinstance(result, dict) or not result.get("ok"):
        detail = result.get("error", "解析失败") if isinstance(result, dict) else "返回格式错误"
        raise DownloadError(f"解析服务：{detail}")
    data = result.get("data")
    if not isinstance(data, dict):
        raise DownloadError("解析服务未返回视频信息。")
    video_url = data.get("h264_url") or data.get("h265_url")
    parts = urlsplit(video_url) if isinstance(video_url, str) else None
    if not parts or parts.scheme != "https" or parts.hostname != "finder.video.qq.com":
        raise DownloadError("未取得可信的视频下载地址。")
    return data


def available_path(folder: Path, stem: str) -> Path:
    target = folder / f"{stem}.mp4"
    number = 2
    while target.exists() or target.with_suffix(".mp4.part").exists():
        target = folder / f"{stem} ({number}).mp4"
        number += 1
    return target


def download_video(link: str, folder: Path, report, cancel: threading.Event) -> Path:
    if cancel.is_set():
        raise Cancelled()
    report("正在解析分享链接…")
    data = parse_video(link)
    if cancel.is_set():
        raise Cancelled()
    video_url = data.get("h264_url") or data.get("h265_url")
    title = safe_name((data.get("description") or "视频").splitlines()[0], 65)
    author = safe_name(data.get("author") or "视频号", 25)
    folder.mkdir(parents=True, exist_ok=True)
    target = available_path(folder, f"{author} - {title}")
    part = target.with_suffix(".mp4.part")
    report(f"正在下载：{target.name}")
    request = Request(video_url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with open_request(request, timeout=60) as response:
            final_url = urlsplit(response.url)
            if final_url.scheme != "https" or final_url.hostname != "finder.video.qq.com":
                raise DownloadError("视频地址跳转到了非预期站点，已停止下载。")
            first = response.read(32)
            if len(first) < 12 or first[4:8] != b"ftyp":
                raise DownloadError("服务器返回的不是 MP4 视频。")
            total = int(response.headers.get("Content-Length") or 0)
            received = 0
            with part.open("wb") as file:
                file.write(first)
                received += len(first)
                while True:
                    if cancel.is_set():
                        raise Cancelled()
                    chunk = response.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    file.write(chunk)
                    received += len(chunk)
                    if total:
                        report(f"正在下载：{received / 1024 / 1024:.1f} / {total / 1024 / 1024:.1f} MB")
                    else:
                        report(f"正在下载：{received / 1024 / 1024:.1f} MB")
            if total and received != total:
                raise DownloadError(f"文件未下载完整（{received}/{total} 字节）。")
            os.replace(part, target)
            report(f"已保存：{target}")
            return target
    except HTTPError as exc:
        raise DownloadError(f"视频下载返回 HTTP {exc.code}，请重新解析。") from exc
    except (URLError, TimeoutError) as exc:
        raise DownloadError(f"视频连接中断：{exc}") from exc
    finally:
        if part.exists():
            part.unlink()


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("微信视频号链接下载")
        self.geometry("720x500")
        self.minsize(560, 400)
        self.events: queue.Queue[tuple[str, str]] = queue.Queue()
        self.cancel = threading.Event()
        self.worker: threading.Thread | None = None
        frame = ttk.Frame(self, padding=16)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="粘贴视频号分享链接（一行一个）").pack(anchor="w")
        self.links = scrolledtext.ScrolledText(frame, height=7, wrap="word")
        self.links.pack(fill="both", expand=True, pady=(8, 14))
        ttk.Label(frame, text="保存到").pack(anchor="w")
        row = ttk.Frame(frame)
        row.pack(fill="x", pady=(6, 14))
        self.folder = tk.StringVar(value=str(DEFAULT_OUTPUT))
        ttk.Entry(row, textvariable=self.folder).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="浏览…", command=self.choose_folder).pack(side="left", padx=(8, 0))
        controls = ttk.Frame(frame)
        controls.pack(fill="x")
        self.start_button = ttk.Button(controls, text="开始下载", command=self.start)
        self.start_button.pack(side="left")
        self.cancel_button = ttk.Button(controls, text="取消", command=self.stop, state="disabled")
        self.cancel_button.pack(side="left", padx=(8, 0))
        ttk.Label(frame, text="运行记录").pack(anchor="w", pady=(16, 6))
        self.log = scrolledtext.ScrolledText(frame, height=8, wrap="word", state="disabled")
        self.log.pack(fill="both", expand=True)
        ttk.Label(
            frame,
            text="免微信扫码；解析依赖第三方 v.mtotech.com，分享链接会发送至该站。",
            foreground="#555555",
        ).pack(anchor="w", pady=(10, 0))
        self.after(100, self.poll_events)

    def choose_folder(self) -> None:
        selected = filedialog.askdirectory(initialdir=self.folder.get() or str(Path.home()))
        if selected:
            self.folder.set(selected)

    def write_log(self, line: str) -> None:
        self.log.configure(state="normal")
        self.log.insert("end", line + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def start(self) -> None:
        links = extract_links(self.links.get("1.0", "end"))
        if not links:
            messagebox.showerror("链接错误", "请粘贴 https://weixin.qq.com/sph/... 分享链接。")
            return
        folder_text = self.folder.get().strip()
        if not folder_text:
            messagebox.showerror("保存位置错误", "请选择保存文件夹。")
            return
        folder = Path(folder_text).expanduser()
        self.cancel.clear()
        self.start_button.configure(state="disabled")
        self.cancel_button.configure(state="normal")
        self.write_log(f"开始处理 {len(links)} 条链接。")
        self.worker = threading.Thread(target=self.run_jobs, args=(links, folder), daemon=True)
        self.worker.start()

    def stop(self) -> None:
        self.cancel.set()
        self.cancel_button.configure(state="disabled")
        self.write_log("正在取消…")

    def run_jobs(self, links: list[str], folder: Path) -> None:
        succeeded = 0
        try:
            for index, link in enumerate(links, 1):
                if self.cancel.is_set():
                    break
                self.events.put(("log", f"[{index}/{len(links)}] {link}"))
                try:
                    download_video(link, folder, lambda line: self.events.put(("log", line)), self.cancel)
                    succeeded += 1
                except Cancelled:
                    break
                except (DownloadError, OSError, ValueError) as exc:
                    self.events.put(("log", f"失败：{exc}"))
            self.events.put(("log", f"结束：成功 {succeeded}/{len(links)} 条。"))
        finally:
            self.events.put(("done", ""))

    def poll_events(self) -> None:
        try:
            while True:
                kind, value = self.events.get_nowait()
                if kind == "log":
                    self.write_log(value)
                elif kind == "done":
                    self.start_button.configure(state="normal")
                    self.cancel_button.configure(state="disabled")
        except queue.Empty:
            pass
        self.after(100, self.poll_events)


def main() -> int:
    parser = argparse.ArgumentParser(description="免登录下载微信视频号分享链接")
    parser.add_argument("--download", metavar="LINK", help="命令行下载单条链接")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="下载目录")
    args = parser.parse_args()
    if args.download:
        try:
            path = download_video(args.download, args.output, print, threading.Event())
            print(path)
            return 0
        except (DownloadError, OSError, ValueError) as exc:
            print(f"下载失败：{exc}", file=sys.stderr)
            return 1
    App().mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

