<p align="center">
  <img src="images/logo.png" alt="NoAdsFM Logo" width="225" height="225">
</p>

# NoAdsFM

NoAdsFM is a Python script that removes ads from recorded radio streams—clean audio, no interruptions.

## Motivation

Downloading audio streams or online radio broadcasts often includes unwanted advertisements. NoAdsFM provides a simple post-processing solution to cut these ads and deliver a seamless listening experience.

## Prerequisites

Make sure you have the following installed before running NoAdsFM:

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

Additionally, install [FFmpeg](https://ffmpeg.org/download.html), which includes both `ffmpeg` and `ffprobe`, required for audio processing.

## Usage

To run NoAdsFM, use the following command:

```bash
python3 main.py <path to your input file.mp3 or .aac>
```
