# Blender用SLAM実行結果可視化スクリプト

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
```

---
## 実行スクリプト説明
- blender起動後に`スクリプト作成` → `開く` → ``
![動作例](https://github.com/master-jedi365/SLAM_viewer/assets/86700262/70f34dcc-a6ad-4c9c-b8ed-6b142472bb6e)


