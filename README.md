# 機器学習サンプルコード集

## 動作確認環境
| 項目 | 内容 |
| :--- | :--- | 
| OS | Windows 11 Pro |
| OS Build | 22621.2428 |
| RAM | 32GB |
| CPU | Intel(R) Core(TM) i7-10750H CPU  |
| GPU  | NVIDIA GeForce RTX 2080 |
| blender | 3.6 |

---
## 環境構築

Blenderのインストールフォルダ (ここではblender3.6)に移動して必要なpythonライブラリをインストールする：
```
$ ./blender3.6/3.6/python/bin/python.exe -m pip install scipy 
$ docker build -t ml_sample:latest .
```

![動作例](pic/annimation.gif)

---
## 実行スクリプト説明
- run_simple_regression.sh: カリフォルニアデータセットの単線形回帰分析を行うスクリプト
- run_multi_regression.sh: カリフォルニアデータセットの重線形回帰分析を行うスクリプト