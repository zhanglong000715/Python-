# MKVFuse

**FFmpeg Media Stream Merger — 基于流检测的智能无损媒体封装工具**
**FFmpeg メディアストリームマージャー — ストリーム検出ベースのスマート無損失メディアパッケージツール**
**FFmpeg Media Stream Merger — Smart Lossless Media Muxing Tool Based on Stream Detection**

---

## 📋 简介 / 概要 / Introduction

**中文：**
MKVFuse（脚本文件：`MKV_Fuse.py`）是一个基于 Python 编写的高级 FFmpeg 媒体合并工具。其核心创新点在于摒弃了传统仅依赖文件扩展名来判断媒体类型的做法，转而通过调用 `ffprobe` 对文件内部的实际流（视频流、音频流、字幕流）进行深度检测与解析。这使得工具能够精准识别诸如"包含纯音频的 `.webm` 文件"或"包含字幕流的 `.mkv` 文件"等复杂情况，从而实现无损、高效的媒体封装，统一输出为 MKV 容器格式。

**日本語：**
MKVFuse（スクリプトファイル：`MKV_Fuse.py`）は、Python で記述された高度な FFmpeg メディア結合ツールです。最大の特徴は、従来のファイル拡張子だけに依存したメディアタイプ判定を廃止し、`ffprobe` を使用してファイル内部の実際のストリーム（ビデオストリーム、オーディオストリーム、サブタイトルストリーム）を深く検出・解析することです。これにより、「純粋なオーディオを含む `.webm` ファイル」や「サブタイトルストリームを含む `.mkv` ファイル」といった複雑なケースを正確に識別し、無損失かつ効率的なメディアパッケージを実現し、MKV コンテナ形式に統一出力します。

**English:**
MKVFuse (script file: `MKV_Fuse.py`) is an advanced FFmpeg media merger tool written in Python. Its core innovation lies in abandoning the traditional approach of relying solely on file extensions to determine media types. Instead, it uses `ffprobe` to deeply inspect and parse the actual streams (video, audio, subtitle) within files. This enables the tool to accurately identify complex cases such as "a `.webm` file containing only audio" or "a `.mkv` file containing subtitle streams," achieving lossless and efficient media muxing with unified MKV container output.

---

## ✨ 核心特性 / コア機能 / Core Features

| # | 中文 | 日本語 | English |
|---|------|--------|---------|
| 1 | 🧠 **智能流检测** — 利用 `ffprobe` 获取真实的 `codec_type`，确保分类准确无误 | 🧠 **インテリジェントストリーム検出** — `ffprobe` を使用して実際の `codec_type` を取得し、正確な分類を保証 | 🧠 **Smart Stream Detection** — Uses `ffprobe` to retrieve the real `codec_type`, ensuring accurate classification |
| 2 | 🔄 **无损合并** — 采用 `stream copy` 模式，将视频、多音轨、多字幕无损封装至 MKV 容器 | 🔄 **無損失結合** — `stream copy` モードを採用し、ビデオ、マルチオーディオトラック、マルチサブタイトルを MKV コンテナに無損失パッケージ | 🔄 **Lossless Merging** — Uses `stream copy` mode to losslessly mux video, multiple audio tracks, and multiple subtitles into MKV container |
| 3 | 🛡️ **降级容错机制** — 当字幕流直接 copy 失败时，自动尝试重编码为 MKV 兼容格式 | 🛡️ **フォールバック耐障害メカニズム** — サブタイトルストリームの直接コピーが失敗した場合、自動的に MKV 互換形式に再エンコード | 🛡️ **Fallback Fault Tolerance** — Automatically attempts re-encoding subtitles to MKV-compatible format when direct copy fails |
| 4 | 🎛️ **灵活工作模式** — 支持交互式命令行选择、自动同名匹配合并以及命令行参数直接指定 | 🎛️ **柔軟な作業モード** — インタラクティブコマンドライン選択、自動同名マッチング結合、コマンドライン引数直接指定をサポート | 🎛️ **Flexible Working Modes** — Supports interactive CLI selection, automatic same-name matching, and direct CLI argument specification |
| 5 | 🌐 **跨平台兼容** — 自动在系统 PATH 及常见安装目录中查找 `ffmpeg` / `ffprobe` 可执行文件 | 🌐 **クロスプラットフォーム互換** — システム PATH および一般的なインストールディレクトリで `ffmpeg` / `ffprobe` 実行ファイルを自動検索 | 🌐 **Cross-Platform Compatible** — Automatically locates `ffmpeg` / `ffprobe` executables in system PATH and common installation directories |

---

## 🚀 快速开始 / クイックスタート / Quick Start

### 前置依赖 / 前提条件 / Prerequisites

**中文：**
- **Python 3.6+**（脚本仅使用标准库，无需额外安装第三方包）
- **FFmpeg**（需安装并加入系统 PATH，或放置于常见安装目录）

**日本語：**
- **Python 3.6+**（スクリプトは標準ライブラリのみ使用、追加パッケージ不要）
- **FFmpeg**（インストールしてシステム PATH に追加、または一般的なインストールディレクトリに配置）

**English:**
- **Python 3.6+** (the script uses only standard libraries, no third-party packages required)
- **FFmpeg** (must be installed and added to system PATH, or placed in a common installation directory)

### 安装 FFmpeg / FFmpeg のインストール / Installing FFmpeg

| 平台 / プラットフォーム / Platform | 命令 / コマンド / Command |
|---|---|
| **Windows** | 从 [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) 下载，或使用 `winget install ffmpeg` / `scoop install ffmpeg` |
| **macOS** | `brew install ffmpeg` |
| **Linux** | `sudo apt install ffmpeg` (Debian/Ubuntu) 或 `sudo dnf install ffmpeg` (Fedora) |

---

## 📖 使用方法 / 使用方法 / Usage

### 模式一：交互模式 / モード1：インタラクティブモード / Mode 1: Interactive Mode

**中文：** 默认模式，逐步引导你选择视频、音频和字幕文件。

**日本語：** デフォルトモード。ビデオ、オーディオ、サブタイトルファイルの選択をステップごとにガイドします。

**English:** Default mode. Guides you step-by-step through selecting video, audio, and subtitle files.

```bash
python MKV_Fuse.py
# 或 / または / Or
python MKV_Fuse.py -i
python MKV_Fuse.py --interactive
```

### 模式二：自动匹配模式 / モード2：自動マッチングモード / Mode 2: Auto-Match Mode

**中文：** 自动扫描目录，将同名（或包含同名关键字）的视频、音频、字幕文件配对合并。适合批量处理。

**日本語：** ディレクトリを自動スキャンし、同名（または同名キーワードを含む）のビデオ、オーディオ、サブタイトルファイルをペアリングして結合します。バッチ処理に適しています。

**English:** Automatically scans the directory and pairs video, audio, and subtitle files with matching names (or containing the same keyword) for merging. Ideal for batch processing.

```bash
python MKV_Fuse.py -a
python MKV_Fuse.py --auto
# 指定输出目录 / 出力ディレクトリ指定 / Specify output directory
python MKV_Fuse.py -a -o ./output
```

### 模式三：命令行参数模式 / モード3：コマンドライン引数モード / Mode 3: CLI Argument Mode

**中文：** 直接通过参数指定所有输入输出文件，适合脚本集成和自动化。

**日本語：** すべての入出力ファイルを引数で直接指定。スクリプト統合や自動化に適しています。

**English:** Directly specify all input and output files via arguments. Perfect for script integration and automation.

```bash
python MKV_Fuse.py -v video.mp4 -A audio_jpn.m4a audio_eng.m4a -S sub_chs.ass sub_eng.srt -O output.mkv
```

### 查看文件流信息 / ファイルストリーム情報表示 / View File Stream Info

**中文：** 仅探测并显示指定文件的流信息，不执行合并。

**日本語：** 指定ファイルのストリーム情報のみを検出・表示し、結合は実行しません。

**English:** Only probe and display stream info of the specified file without performing any merge.

```bash
python MKV_Fuse.py -I somefile.mkv
```

---

## 📂 命令行参数一览 / コマンドライン引数一覧 / CLI Arguments Reference

| 参数 / 引数 / Argument | 说明 / 説明 / Description |
|---|---|
| `-d`, `--dir` | 中文：工作目录（默认当前目录）<br>日本語：作業ディレクトリ（デフォルトはカレントディレクトリ）<br>English: Working directory (defaults to current directory) |
| `-i`, `--interactive` | 中文：交互模式<br>日本語：インタラクティブモード<br>English: Interactive mode |
| `-a`, `--auto` | 中文：自动匹配模式<br>日本語：自動マッチングモード<br>English: Auto-match mode |
| `-o`, `--output-dir` | 中文：输出目录（自动模式下使用）<br>日本語：出力ディレクトリ（自動モードで使用）<br>English: Output directory (used in auto mode) |
| `-v`, `--video` | 中文：手动指定视频文件<br>日本語：ビデオファイルを手動指定<br>English: Manually specify video file |
| `-A`, `--audio` | 中文：手动指定音频文件（可多个）<br>日本語：オーディオファイルを手動指定（複数可）<br>English: Manually specify audio files (multiple allowed) |
| `-S`, `--subtitle` | 中文：手动指定字幕文件（可多个）<br>日本語：サブタイトルファイルを手動指定（複数可）<br>English: Manually specify subtitle files (multiple allowed) |
| `-O`, `--output` | 中文：手动指定输出文件<br>日本語：出力ファイルを手動指定<br>English: Manually specify output file |
| `-I`, `--info` | 中文：仅显示文件流信息<br>日本語：ファイルストリーム情報のみ表示<br>English: Display file stream info only |
| `-q`, `--quiet` | 中文：安静模式（减少输出）<br>日本語：静かモード（出力を削減）<br>English: Quiet mode (reduce output) |

---

## 🏗️ 工作原理 / 動作原理 / How It Works

```
┌─────────────────────────────────────────────────────────┐
│                    MKVFuse 工作流程                      │
│                  MKVFuse 作業フロー                       │
│                 MKVFuse Workflow                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. 扫描目录 / ディレクトリスキャン / Scan Directory       │
│     └─ 过滤媒体扩展名 / メディア拡張子フィルタ             │
│                                                         │
│  2. ffprobe 流检测 / ffprobe ストリーム検出                │
│     ├─ 视频流 (video)    → 分类为视频文件                  │
│     ├─ 音频流 (audio)    → 分类为音频文件                  │
│     └─ 字幕流 (subtitle) → 分类为字幕文件                  │
│                                                         │
│  3. 用户选择 / ユーザー選択 / User Selection               │
│     ├─ 交互模式：逐步选择                                 │
│     ├─ 自动模式：同名匹配                                 │
│     └─ 参数模式：直接指定                                 │
│                                                         │
│  4. 构建 FFmpeg 命令 / FFmpeg コマンド構築                 │
│     ├─ -map 映射所有流                                    │
│     ├─ -c:v copy (视频无损)                               │
│     ├─ -c:a copy (音频无损)                               │
│     └─ -c:s copy (字幕无损, 失败则自动降级)                │
│                                                         │
│  5. 输出 MKV / MKV 出力 / Output MKV                     │
│     └─ *_merged.mkv                                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 适用场景 / 適用シーン / Use Cases

**中文：**
- 🎬 将下载的视频与外挂音轨（如不同语言的配音）合并为一个 MKV 文件
- 📺 为视频添加一个或多个外挂字幕（如中/英/日多语字幕）
- 🗂️ 批量整理同目录下的视频、音频、字幕资源，一键自动合并
- 🔍 快速检测任意媒体文件的真实流信息（不依赖扩展名）
- 📦 将分散的音视频素材无损封装为统一的 MKV 容器

**日本語：**
- 🎬 ダウンロードしたビデオと外部オーディオトラック（異なる言語の吹き替えなど）を1つの MKV ファイルに結合
- 📺 ビデオに1つ以上の外部サブタイトルを追加（中/英/日多言語字幕など）
- 🗂️ 同一ディレクトリ内のビデオ、オーディオ、サブタイトルリソースを一括整理・自動結合
- 🔍 任意のメディアファイルの実際のストリーム情報を迅速に検出（拡張子に依存しない）
- 📦 分散したオーディオビジュアル素材を MKV コンテナに無損失パッケージ

**English:**
- 🎬 Merge downloaded videos with external audio tracks (e.g., dubs in different languages) into a single MKV file
- 📺 Add one or more external subtitles to videos (e.g., multilingual subtitles in Chinese/English/Japanese)
- 🗂️ Batch organize and auto-merge video, audio, and subtitle resources in the same directory
- 🔍 Quickly detect the real stream information of any media file (not relying on extensions)
- 📦 Losslessly mux scattered audio-visual materials into a unified MKV container

---

## 📁 支持格式 / 対応形式 / Supported Formats

**中文：** 以下扩展名用于初筛，最终分类以 `ffprobe` 实际检测结果为准。

**日本語：** 以下の拡張子は初期フィルタリングに使用され、最終分類は `ffprobe` の実際の検出結果に基づきます。

**English:** The following extensions are used for initial filtering; final classification is based on actual `ffprobe` detection results.

| 类型 / タイプ / Type | 格式 / 形式 / Formats |
|---|---|
| **视频 / ビデオ / Video** | `mp4` `mkv` `avi` `mov` `flv` `wmv` `mpg` `mpeg` `mts` `m2ts` `ts` `vob` `rm` `rmvb` `asf` `3gp` `3g2` `divx` `f4v` `ogv` `dv` `webm` `m4v` |
| **音频 / オーディオ / Audio** | `mp3` `wav` `aac` `m4a` `flac` `ogg` `oga` `opus` `wma` `ac3` `dts` `eac3` `mka` `aiff` `aif` `m4b` `ape` `tta` `mp2` `amr` `mpc` `wv` `spx` `ra` `ram` `caf` |
| **字幕 / サブタイトル / Subtitle** | `srt` `ass` `ssa` `sub` `idx` `vtt` `ttml` `dfxp` `smi` `sami` `mpl` `pjs` `stl` `sup` `pgs` `sbv` `lrc` `rt` `txt` |
| **原始流 /  raw ストリーム / Raw Streams** | `h264` `h265` `hevc` `avc` `vp9` `ivf` |

---

## ⚙️ 技术细节 / 技術詳細 / Technical Details

**中文：**
- **流分类逻辑**：优先使用 `ffprobe -show_streams` 获取 JSON 格式的流信息，按 `codec_type` 字段分类。若 `ffprobe` 不可用，则退回到扩展名猜测作为兜底方案。
- **合并策略**：视频文件提取全部视频流 + 自带音频/字幕流；外部音频文件仅提取音频流；外部字幕文件仅提取字幕流。全部使用 `-c copy` 模式实现零损耗。
- **字幕降级**：当 `-c:s copy` 导致 FFmpeg 报错时（常见于 PGS/SUP 等位图字幕），自动移除字幕 copy 指令，让 FFmpeg 选择 MKV 兼容的编码器。
- **超时保护**：FFmpeg 子进程设有 1 小时超时，防止卡死。
- **内存优化**：`StreamInfo` 类使用 `__slots__` 限制属性，减少内存占用。

**日本語：**
- **ストリーム分類ロジック**：`ffprobe -show_streams` で JSON 形式のストリーム情報を取得し、`codec_type` フィールドで分類。`ffprobe` が利用できない場合は拡張子推測にフォールバック。
- **結合戦略**：ビデオファイルから全ビデオストリーム＋内蔵オーディオ/サブタイトルを抽出。外部オーディオファイルからはオーディオストリームのみ、外部サブタイトルファイルからはサブタイトルストリームのみを抽出。すべて `-c copy` モードでゼロ損失を実現。
- **サブタイトルフォールバック**：`-c:s copy` が FFmpeg エラーを引き起こした場合（PGS/SUP などのビットマップ字幕で一般的）、自動的にサブタイトル copy 命令を削除し、FFmpeg に MKV 互換エンコーダーを選択させます。
- **タイムアウト保護**：FFmpeg サブプロセスに1時間のタイムアウトを設定し、ハングアップを防止。
- **メモリ最適化**：`StreamInfo` クラスは `__slots__` を使用して属性を制限し、メモリ使用量を削減。

**English:**
- **Stream Classification Logic**: Prioritizes `ffprobe -show_streams` to obtain JSON-formatted stream info and classifies by the `codec_type` field. Falls back to extension-based guessing if `ffprobe` is unavailable.
- **Merge Strategy**: Extracts all video streams + embedded audio/subtitle streams from the video file; extracts only audio streams from external audio files; extracts only subtitle streams from external subtitle files. All use `-c copy` mode for zero loss.
- **Subtitle Fallback**: When `-c:s copy` causes an FFmpeg error (common with bitmap subtitles like PGS/SUP), the subtitle copy directive is automatically removed, letting FFmpeg choose an MKV-compatible encoder.
- **Timeout Protection**: FFmpeg subprocess has a 1-hour timeout to prevent hanging.
- **Memory Optimization**: The `StreamInfo` class uses `__slots__` to restrict attributes and reduce memory footprint.

---

## 📄 许可证 / ライセンス / License

**中文：** 欢迎自由使用、修改和分发！

**日本語：** 自由に使用、改変、配布してください！

**English:** MIT License - Feel free to use, modify, and distribute!

---

> **MKVFuse** — *Fuse your streams. Losslessly.* 🔗
