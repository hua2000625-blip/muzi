$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot

$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    throw '未找到 .venv。先运行：python -m venv .venv；.\.venv\Scripts\python.exe -m pip install pyinstaller'
}

& $python -m PyInstaller --noconfirm --clean --windowed --onefile `
    --name '微信视频号小程序' app.py
if ($LASTEXITCODE -ne 0) { throw 'PyInstaller 打包失败。' }

$package = Join-Path $PSScriptRoot 'dist\微信视频号小程序'
$resolvedRoot = [IO.Path]::GetFullPath($PSScriptRoot).TrimEnd('\') + '\'
$resolvedPackage = [IO.Path]::GetFullPath($package)
if (-not $resolvedPackage.StartsWith($resolvedRoot, [StringComparison]::OrdinalIgnoreCase)) {
    throw '打包目录不在当前项目内，已停止。'
}
if (Test-Path -LiteralPath $package) { Remove-Item -LiteralPath $package -Recurse -Force }
New-Item -ItemType Directory -Path $package | Out-Null
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'dist\微信视频号小程序.exe') -Destination (Join-Path $package '微信视频号小程序.exe') -Force
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'README.md') -Destination (Join-Path $package '使用说明.md') -Force
$zip = Join-Path $PSScriptRoot 'dist\微信视频号小程序.zip'
if (Test-Path -LiteralPath $zip) { Remove-Item -LiteralPath $zip -Force }
Compress-Archive -Path (Join-Path $package '*') -DestinationPath $zip -CompressionLevel Optimal
Write-Host "已生成：$package"
Write-Host "压缩包：$zip"

