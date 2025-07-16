#!/bin/bash

# 仮想環境の作成
python3 -m venv .venv

# 仮想環境のアクティベート
source .venv/bin/activate

# 必要なパッケージのインストール
pip install -r requirements.txt
