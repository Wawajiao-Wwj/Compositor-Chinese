# 构建与打包

已验证环境：Apple 芯片 Mac、macOS 27.0.1、Apple Command Line Tools（Swift 6.4）及 macOS 26.5 SDK。

脚本直接使用 Apple 的编译工具。macOS 27 SDK 在本机 Command Line Tools 中缺少 SwiftUI 的编译宏插件，因此此构建明确使用已验证的 26.5 SDK。

## 前提

- 安装 Apple Command Line Tools，且包含 macOS 26.5 SDK。
- 安装原版 Compositor 1.4.7，用于复制应用图标及资源。
- 保留仓库根目录的 THIRD_PARTY_NOTICES.md 和 source/LICENSE。

官方基线：https://github.com/robbietilton/Compositor/releases/tag/v1.4.7

## 构建

在仓库根目录运行：

```sh
python3 source/scripts/build_chinese.py
python3 source/scripts/verify_localization.py
```

原版应用不在默认位置时，将路径作为第一个参数：

```sh
python3 source/scripts/build_chinese.py "/path/to/Compositor.app"
```

脚本检查原版版本，编译 C 与 Swift 源码，将语言目录写入应用资源，并进行本地签名。输出为 `dist/Compositor 中文.app`。它只重建仓库的输出，不修改原版。

重新构建前请退出输出的中文版应用。

## 发布包

```sh
python3 scripts/package_release.py
```

脚本先验证翻译与应用签名，再生成保留中文文件名及执行权限的 ZIP，以及 `dist/SHA256SUMS.txt` 校验文件。将 ZIP 与校验文件放入 GitHub Releases。`dist/` 和编译缓存不提交到源码仓库。
