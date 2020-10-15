# JADERを用いたTNF-α阻害薬による有害事象数を使用したRORの算出

## 実行環境

環境構築するためにはアプリケーションが必要です。環境構築する前にローカルにインストールされていることを確認してください。

- Docker  19.03.12

- docker-compose 1.27.2

その他の利用しているライブラリは`docker/requirement.txt`を参照してください。

## 環境構築

docker で仮想環境を構築しています。次のコマンドで環境が作成されます。

```bash
$ docker-compose up -d
```

## フォルダ構造

```
|- data/
	|- jader/　　　　　　　　　- JADERの元データフォルダ
	|- target/		- 解析後のデータフォルダ
|- docker/
	|- Dockerfile
	|- requirements.txt     - 必要なライブラリ
|- docs/
|- notebooks/
|- preprecess/
	|- create_db.py  	- jaderデータから解析用のデータを作成するモジュール
	|- ror.py　　　　　　　　　- 薬物と有害事象ごとにRORを計算するモジュール
```

## 概要

TNF-α阻害薬に分類される5剤（インフリキシマブ、エタネルセプト、アダリズマブ、ゴリズマブ、セルトリズマブ ぺゴル）に関連する有害事象が発生した症例の患者情報と頻度の集計、RORを算出する。

## JADER（Japanese Adverse Drug Event Report database）について

独立行政法人医薬品医療機器総合機構（PMDA）が提供している「副作用が疑われる症例報告に関する情報『医薬品副作用データベース』」のこと。以下の4つのテーブルからなる。

 ![jader](https://czeek.com/wp-content/uploads/2017/08/ERJADER.png)

> [くすりの有害事象と薬剤疫学](https://czeek.com/) DB構造について　JADER版

## 実行

解析用のデータベース`target/data.csv`が作成されます。 またTNF-α阻害薬を服用していた場合の副作用の集計結果`target/count_side_effect.csv`とTNF-α阻害薬に分類される5剤（インフリキシマブ、エタネルセプト、アダリズマブ、ゴリズマブ、セルトリズマブ ぺゴル）の報告年度別の頻度`target/count_years.csv`も作成されます。

```bash
$ docker exec -it jader-inf-2020 python3 preprocess/create_db.py
```

`data.csv`を利用し、TNF-α阻害薬に分類される5剤（インフリキシマブ、エタネルセプト、アダリズマブ、ゴリズマブ、セルトリズマブ ぺゴル）とそれぞれの有害事象上位30までのRORの計算結果が`target/ror.csv`を算出されます。

```bash
$ docker exec -it jader-inf-2020 python3 preprocess/ror.py
```

## 手順



## 参考

- [Comparison of Adverse Event Profiles of Tumor Necrosis Factor-Alfa Inhibitors: Analysis of a Spontaneous Reporting Database](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7439489/)

- くすりの有害事象と薬剤疫学

    -  [DB構造について](https://czeek.com/epidemiology/dbstructure_jader/) JADER版
    - [カウント方法について（オーダー機能）](https://czeek.com/jissen/howtocount/)
