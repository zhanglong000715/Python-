***

# AV Stream Splitter (AV_Stream_Splitter.py)



---

## 🇨🇳 中文 (Chinese)

### 📖 项目简介

**AV Stream Splitter** 是一个轻量级但功能强大的 Python 脚本，旨在自动化处理媒体文件的流分离任务。它无需重新编码（Lossless），即可将视频文件中的音频轨、字幕轨提取为独立文件，或将其封装为纯音频容器。

本工具特别适合需要批量提取多音轨电影、保留原始画质/音质的归档工作，以及处理包含复杂字幕轨道的媒体文件。

### ✨ 核心特性

1.  **真正的无损提取 (Lossless Extraction)**
    *   全程使用 `-c copy` 模式，不进行任何重编码。提取后的音频和字幕与源文件比特级一致，零质量损失，速度极快。

2.  **智能容器策略 (Smart Container Selection)**
    *   **优先原格式**：尽可能保持与源文件相同的容器格式。
    *   **编码感知**：如果音频是 FLAC，自动优先输出为 `.flac`；如果是 AAC，则优先 `.m4a`。
    *   **字幕兼容**：检测到字幕时，自动选择支持内嵌字幕的容器（如 `.mkv`, `.mka`, `.mp4`），尝试将音频与字幕打包在一起。

3.  **最佳努力容错机制 (Best-Effort Fallback)**
    *   如果首选容器封装失败（例如某些格式不支持特定编码组合），脚本会自动尝试备选容器格式，确保最大程度成功导出。
    *   若无法将字幕封装进音频文件，会自动将字幕单独提取为 `.srt`, `.ass`, `.sup` 等独立文件。

4.  **丰富的元数据命名**
    *   输出文件名自动包含：`源文件名` + `流类型` + `索引` + `编码格式` + `语言标签` + `标题`。
    *   自动检测并清理非法字符，避免文件名冲突。

5.  **广泛的格式支持**
    *   支持 MP4, MKV, AVI, MOV, FLV, TS, WebM 等主流视频格式。
    *   支持 MP3, FLAC, AAC, OPUS, WAV 等音频格式。
    *   支持 SRT, ASS, PGS, VobSub 等字幕格式。

### 🚀 快速开始

#### 1. 环境准备
确保您的系统已安装 **FFmpeg** 和 **FFprobe**，并将它们添加到系统环境变量 `PATH` 中。
*   **Windows**: 下载 FFmpeg 静态构建版，将 `bin` 目录加入 PATH。
*   **macOS**: `brew install ffmpeg`
*   **Linux**: `sudo apt install ffmpeg` (Debian/Ubuntu) 或 `sudo dnf install ffmpeg` (Fedora)

#### 2. 使用方法
1.  将 `AV_Stream_Splitter.py` 放置在您想要处理的媒体文件所在的文件夹中。
2.  打开终端或命令行，进入该目录。
3.  运行脚本：
    ```bash
    python AV_Stream_Splitter.py
    ```
4.  脚本会自动扫描当前目录下的所有媒体文件，执行提取操作，并在完成后显示生成的文件列表。

### ⚙️ 工作流程示例

假设有一个名为 `Movie.mkv` 的文件，包含：
*   视频轨 (H.264)
*   音频轨 0: English AC3
*   音频轨 1: Japanese FLAC
*   字幕轨 0: Chinese ASS

**脚本将执行：**
1.  识别到音频轨 1 是 FLAC，且有字幕。
2.  尝试创建 `Movie.audio.1.flac.chi.ass.mkv` (或其他支持的容器)，将日语 FLAC 音频和中文字幕封装在一起。
3.  如果封装成功，完成。
4.  如果封装失败，回退策略：
    *   提取纯音频：`Movie.audio.1.flac.jpn.flac`
    *   提取纯字幕：`Movie.sub.0.ass.chi.ass`

---

## 🇯🇵 日本語 (Japanese)

### 📖 はじめに

**AV Stream Splitter** は、FFmpeg と FFprobe を駆使した、メディアファイルのストリーム分離を自動化する Python スクリプトです。

再エンコードなし（ロスレス）で、動画ファイルから音声トラックや字幕トラックを個別に抽出したり、純粋なオーディオコンテナとして再パッケージ化したりすることができます。マルチオーディオを含む映画のアーカイブや、高品質な音声・字幕のみを必要とするシーンで絶大な威力を発揮します。

### ✨ 主な特徴

1.  **完全なロスレス抽出 (Lossless Extraction)**
    *   全工程で `-c copy` モードを採用しています。再エンコードを行わないため、処理速度が桁違いに速く、音声や字幕の品質が一切劣化しません。ソースとビット単位で同一のデータを出力します。

2.  **インテリジェントなコンテナ選択 (Smart Container Selection)**
    *   **オリジナル優先**: 可能な限り元のコンテナ形式を維持しようとします。
    *   **コーデック認識**: 音声が FLAC の場合は `.flac` を、AAC の場合は `.m4a` を優先的に選択します。
    *   **字幕への配慮**: 字幕が含まれている場合、字幕の埋め込みに対応したコンテナ（`.mkv`, `.mka`, `.mp4` など）を自動的に選び、音声と字幕を一つのファイルにまとめることを試みます。

3.  **「ベストエフォート」なフォールバック機構**
    *   首选のコンテナでのmuxingに失敗した場合でも、あきらめません。代替となるフォーマットを自動的に試行し、成功確率を最大化します。
    *   字幕を音声ファイルに同梱できない場合は、字幕だけを `.srt`, `.ass`, `.sup` などの独立したファイルとして自動的に抽出します。

4.  **メタデータを活用した賢いファイル命名**
    *   出力ファイル名には、`元ファイル名`、`ストリーム種別`、`インデックス`、`コーデック`、`言語タグ`、`タイトル` が自動的に含まれます。
    *   ファイルシステムで使用できない文字は自動除去され、名前衝突も回避されます。

5.  **幅広いフォーマット対応**
    *   MP4, MKV, AVI, MOV, TS, WebM などの主要なビデオコンテナ。
    *   MP3, FLAC, AAC, OPUS, WAV などのオーディオフォーマット。
    *   SRT, ASS, PGS (Blu-ray), VobSub (DVD) などの字幕フォーマット。

### 🚀 クイックスタート

#### 1. 事前準備
システムに **FFmpeg** および **FFprobe** がインストールされ、PATH に登録されている必要があります。
*   **Windows**: FFmpeg の静的ビルドをダウンロードし、`bin` フォルダを環境変数 PATH に追加してください。
*   **macOS**: ターミナルで `brew install ffmpeg` を実行します。
*   **Linux**: `sudo apt install ffmpeg` (Debian/Ubuntu系) または `sudo dnf install ffmpeg` (Fedora系) を実行します。

#### 2. 使い方
1.  `AV_Stream_Splitter.py` を、処理したいメディアファイルが入っているフォルダに置きます。
2.  ターミナルまたはコマンドプロンプトでそのディレクトリに移動します。
3.  スクリプトを実行します：
    ```bash
    python AV_Stream_Splitter.py
    ```
4.  スクリプトは現在のディレクトリ内のすべてのメディアファイルを自動スキャンし、抽出処理を実行します。完了すると、生成されたファイルの一覧が表示されます。

### ⚙️ 動作例

例えば、以下のような構造を持つ `Movie.mkv` というファイルがあるとします：
*   映像トラック (H.264)
*   音声トラック 0: 英語 (AC3)
*   音声トラック 1: 日本語 (FLAC)
*   字幕トラック 0: 中国語 (ASS)

**スクリプトは以下のように動作します：**
1.  音声トラック 1 が FLAC であり、かつ字幕が存在することを検出します。
2.  字幕をサポートするコンテナ（例：`.mkv`）を選び、`Movie.audio.1.flac.jpn.chi.mkv` のような名前で、日本語音声と中国語字幕を一緒に封入しようと試みます。
3.  もし封入に成功すれば、そこで処理を終了します。
4.  もし何らかの理由で封入に失敗した場合、フォールバック処理が行われます：
    *   音声のみを抽出：`Movie.audio.1.flac.jpn.flac`
    *   字幕のみを抽出：`Movie.sub.0.ass.chi.ass`

このように、ユーザーが意識することなく、最適な形でデータを取り出します。

---

## 🇺🇸 English

### 📖 Introduction

**AV Stream Splitter** is a lightweight yet powerful Python script designed to automate the separation of media streams. It extracts audio and subtitle tracks from video files into standalone files or repackages them into audio-only containers without re-encoding (Lossless).

This tool is ideal for archiving multi-audio movies, preserving original quality, and handling media files with complex subtitle tracks.

### ✨ Key Features

1.  **True Lossless Extraction**
    *   Uses `-c copy` mode throughout the process. No re-encoding means zero quality loss and blazing-fast speeds. The output is bit-perfect compared to the source.

2.  **Smart Container Strategy**
    *   **Original First**: Prefers the original container format whenever possible.
    *   **Codec Aware**: Automatically prioritizes `.flac` for FLAC audio and `.m4a` for AAC.
    *   **Subtitle Compatible**: When subtitles are detected, it selects containers that support embedded subtitles (e.g., `.mkv`, `.mka`, `.mp4`) and attempts to bundle audio and subtitles together.

3.  **Best-Effort Fallback Mechanism**
    *   If the preferred container fails to mux (e.g., due to incompatible codec combinations), the script automatically tries alternative formats to ensure successful export.
    *   If subtitles cannot be muxed into the audio file, they are automatically extracted as separate files (`.srt`, `.ass`, `.sup`, etc.).

4.  **Rich Metadata Naming**
    *   Output filenames automatically include: `Source Name` + `Stream Type` + `Index` + `Codec` + `Language Tag` + `Title`.
    *   Illegal characters are sanitized, and filename conflicts are automatically avoided.

5.  **Broad Format Support**
    *   Supports major video containers: MP4, MKV, AVI, MOV, FLV, TS, WebM.
    *   Supports audio formats: MP3, FLAC, AAC, OPUS, WAV.
    *   Supports subtitle formats: SRT, ASS, PGS, VobSub.

### 🚀 Quick Start

#### 1. Prerequisites
Ensure **FFmpeg** and **FFprobe** are installed and added to your system's `PATH` environment variable.
*   **Windows**: Download FFmpeg static build and add the `bin` directory to PATH.
*   **macOS**: Run `brew install ffmpeg`.
*   **Linux**: Run `sudo apt install ffmpeg` (Debian/Ubuntu) or `sudo dnf install ffmpeg` (Fedora).

#### 2. Usage
1.  Place `AV_Stream_Splitter.py` in the folder containing the media files you wish to process.
2.  Open your terminal or command prompt and navigate to that directory.
3.  Run the script:
    ```bash
    python AV_Stream_Splitter.py
    ```
4.  The script will automatically scan all media files in the current directory, perform the extraction, and display a list of generated files upon completion.

### ⚙️ Workflow Example

Consider a file named `Movie.mkv` with the following structure:
*   Video Track (H.264)
*   Audio Track 0: English AC3
*   Audio Track 1: Japanese FLAC
*   Subtitle Track 0: Chinese ASS

**The script will:**
1.  Detect that Audio Track 1 is FLAC and that subtitles exist.
2.  Attempt to create a file like `Movie.audio.1.flac.jpn.chi.mkv` (or another supported container), muxing the Japanese FLAC audio and Chinese subtitles together.
3.  If muxing succeeds, the process is complete.
4.  If muxing fails, it triggers the fallback strategy:
    *   Extract audio only: `Movie.audio.1.flac.jpn.flac`
    *   Extract subtitles only: `Movie.sub.0.ass.chi.ass`

---

## 📄 许可证 / ライセンス / License

**中文：** 欢迎自由使用、修改和分发！

**日本語：** 自由に使用、改変、配布してください！

**English:** MIT License - Feel free to use, modify, and distribute!

---

> **Note**: This tool requires FFmpeg and FFprobe to be installed on your system. Ensure they are accessible via your command line before running the script.
