## 1. 目的

本論文１）を参考に、PMDAの医薬品副作用データベース（Japanese Adverse Drug Event Report database、以下；JADER）からTNF-α阻害薬に分類される5剤（インフリキシマブ、エタネルセプト、アダリズマブ、ゴリズマブ、セルトリズマブ ぺゴル）に関連する各有害事象の報告オッズ比（ROR）と95％信頼区間（CI）を算出した。

## 2. 方法

### 2-1. 使用したデータベース

JADER（Japanese Adverse Drug Event Report database）とは独立行政法人医薬品医療機器総合機構（PMDA）が提供している「副作用が疑われる症例報告に関する情報『医薬品副作用データベース』」のことである。このデータベースは以下の4つのテーブルからなる。

![er](https://www.pmda.go.jp/files/000213668.png)

> [各テーブルのER図 PMDA](https://www.pmda.go.jp/safety/info-services/drugs/adr-info/suspected-adr/0004.html)

JADERはオープンデータとしてPMDAのサイトからダウンロードが可能であり、一定期間で最新のものに更新される。本研究では2020年8月までに報告されたデータを使用した。

### 2-2. 使用した言語・ライブラリ・実行環境

本研究では以下のものを使用し、解析や実行環境の構築を行った。

- Python 3.9
- Colaboratory：Googleが提供するブラウザからPython を記述、実行できるサービス
- Jupyter Notebook：PythonなどをWebブラウザ上で記述・実行できる統合開発環境
- Docker：コンテナ仮想化を用いてアプリケーションを開発・配置・実行するためのオープンソースソフトウェア

### 2-3. 解析手順



## 3. 結果



## 4. 考察

JADERを使用し解析を行う過程において、データベース上の問題点が浮き彫りになった。



## 5. 結論



## 6. 参考文献

1. Wakabayashi, T., Hosohata, K., Oyama, S., Inada, A., Ueno, S., Kambara, H.,… Iwanaga, K. (2020). Comparison of adverse event profiles of tumor necrosis factor-alfa inhibitors: Analysis of a spontaneous reporting database. Therapeutics and Clinical Risk Management.