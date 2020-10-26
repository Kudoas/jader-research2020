# colaboratoryで実行する場合のサンプルコード
# docs/データを読み込む方法.mdでのGoogle Driveでのデータ管理方法を参考し、
# 以下のコードをcolaboratoryで実行すると解析用のデータベースが作成されます。

import codecs
from google.colab import drive
import numpy as np
import os
import pandas as pd


drive.mount("/content/drive")
os.chdir('drive/My Drive/data')


# 解析用のデータベースの作成
class CreateDB:
    def __init__(self, drug: 'dataframe', demo: 'dataframe', reac: 'dataframe'):
        """JADERのオリジナルデータ

        dataframeの形で出力してください
        """
        self.drug = drug
        self.demo = demo
        self.reac = reac

    def extract_suspicious(self):
        """被疑薬のみの抽出"""
        sus_drug = self.drug[
            drug["医薬品の関与"] == "被疑薬"
        ]['識別番号', '医薬品連番', '医薬品（一般名）', '使用理由']
        return sus_drug

    def check_tnfa(self, sus_drug):
        """TNF-α阻害薬に分類される5剤（インフリキシマブ、エタネルセプト、アダリズマブ、ゴリズマブ、セルトリズマブ ぺゴル）の選択 

        該当の5剤、TNF-α阻害薬の服用の有無に対しフラグをつける
        """
        is_infliximab = (
            (sus_drug["医薬品（一般名）"] == "インフリキシマブ（遺伝子組換え）") |
            (sus_drug["医薬品（一般名）"] == "インフリキシマブ（遺伝子組換え）［後続１］") |
            (sus_drug["医薬品（一般名）"] == "インフリキシマブ（遺伝子組換え）［後続３］") |
            (sus_drug["医薬品（一般名）"] == "インフリキシマブ（遺伝子組換え）［後続２］") |
            (sus_drug["医薬品（一般名）"] == "INFLIXIMAB") |
            (sus_drug["医薬品（一般名）"] == "ＩＮＦＬＩＸＩＭＡＢ") |
            (sus_drug["医薬品（一般名）"] == "インフリキシマブ（遺伝子組換え）［インフリキシマブ後続３］") |
            (sus_drug["医薬品（一般名）"] == "INFLIXIMAB (NGX)")
        )
        is_etanercept = (
            (sus_drug["医薬品（一般名）"] == "エタネルセプト（遺伝子組換え）") |
            (sus_drug["医薬品（一般名）"] == "エタネルセプト（遺伝子組換え）［後続１］") |
            (sus_drug["医薬品（一般名）"] == "ETANERCEPT (NGX)") |
            (sus_drug["医薬品（一般名）"] == "エタネルセプト（遺伝子組換え）［後続２］") |
            (sus_drug["医薬品（一般名）"] == "エタネルセプト") |
            (sus_drug["医薬品（一般名）"] == "ETANERCEPT") |
            (sus_drug["医薬品（一般名）"] == "etanercept")
        )
        is_adalimumab = (
            (sus_drug["医薬品（一般名）"] == "ADALIMUMAB(GENETICAL RECOMBINATION)") |
            (sus_drug["医薬品（一般名）"] == "Adalimumab") |
            (sus_drug["医薬品（一般名）"] == "アダリムマブ（遺伝子組換え）") |
            (sus_drug["医薬品（一般名）"] == "アダリムマブ") |
            (sus_drug["医薬品（一般名）"] == "Humira")
        )
        is_golimumab = (
            (sus_drug["医薬品（一般名）"] == "ゴリムマブ（遺伝子組換え）") |
            (sus_drug["医薬品（一般名）"] == "ゴリムマブ")
        )
        is_certolizumab = (
            (sus_drug["医薬品（一般名）"] == "セルトリズマブペゴル") |
            (sus_drug["医薬品（一般名）"] == "セルトリズマブ　ペゴル（遺伝子組換え）") |
            (sus_drug["医薬品（一般名）"] == "ＣＥＲＴＯＬＩＺＵＭＡＢ　ＰＥＧＯＬ")
        )
        sus_drug['Infliximab'] = is_infliximab
        sus_drug['Etanercept'] = is_etanercept
        sus_drug['Adalimumab'] = is_adalimumab
        sus_drug['Golimumab'] = is_golimumab
        sus_drug['Certolizumab'] = is_certolizumab
        sus_drug = sus_drug.replace(False, 0).replace(True, 1)
        is_tnf = (
            (sus_drug['Infliximab'] == 1) |
            (sus_drug['Etanercept'] == 1) |
            (sus_drug['Golimumab'] == 1) |
            (sus_drug['Adalimumab'] == 1) |
            (sus_drug['Certolizumab'] == 1)
        )
        sus_drug["is_tnf"] = is_tnf
        sus_drug.drop(['医薬品連番', '医薬品（一般名）', '使用理由'], axis=1, inplace=True)

        # 重複削除
        sus_drug = sus_drug.drop_duplicates().replace(False, 0).replace(True, 1)
        return sus_drug

    def groupby_tnfa(self, sus_drug):
        """TNF-α阻害薬を服用した患者を1人1レコードへ変換"""
        sus_drug[sus_drug["is_tnf"] == 1].groupby("識別番号").max().to_csv(
            'target/tnf_druger.csv', encoding='shift-jis'
        )

    def join_tnfa_and_demo_reac(self):
        """drug, demo, jaderの結合

        drug, demo, jaderを結合し、csvファイルとして保存する
        """
        drug = pd.read_csv('target/tnf_druger.csv', encoding='shift-jis')

        # 重複削除
        self.demo.drop_duplicates(inplace=True)
        outer_drug_demo = pd.merge(
            self.demo[['識別番号', '性別', '年齢', '報告年度・四半期']], drug, on="識別番号", how='outer'
        )

        # 欠損値の0埋め
        outer_drug_demo[
            ['Infliximab', 'Etanercept', 'Adalimumab',
                'Golimumab', 'Certolizumab', 'is_tnf']
        ].fillna(0)
        outer_drug_demo = pd.concat(
            [outer_drug_demo[['識別番号', '性別', '年齢', '報告年度・四半期']],
             outer_drug_demo[
                ['Infliximab', 'Etanercept', 'Adalimumab',
                    'Golimumab', 'Certolizumab', 'is_tnf']
            ].fillna(0)], axis=1)

        # 重複削除
        jader = pd.merge(
            self.reac[['識別番号', '有害事象']].drop_duplicates(inplace=True),
            outer_drug_demo, on='識別番号', how='outer'
        )
        # ベースデータの保存
        jader.to_csv('target/data.csv', encoding='shift-jis')

    def get_se(self):
        """tnfαを飲んだ人の有害事象の集計データの保存"""
        jader = pd.read_csv('target/data.csv', encoding='shift-jis')
        jader[jader.is_tnf == 1].groupby('有害事象').sum().sort_values('is_tnf', ascending=False)[
            'is_tnf'].to_csv('target/count_side_effect.csv', encoding='shift-jis')


with codecs.open('jader/drug202008.csv', "r", "Shift-JIS", "ignore") as file:
    drug = pd.read_table(file, delimiter=",")

with codecs.open('jader/demo202008.csv', "r", "Shift-JIS", "ignore") as file:
    demo = pd.read_table(file, delimiter=",")

with codecs.open('jader/reac202008.csv', "r", "Shift-JIS", "ignore") as file:
    reac = pd.read_table(file, delimiter=",")


def main():
    c = CreateDB(drug, demo, reac)
    sus_drug = c.extract_suspicious()
    checked_drug = c.check_tnfa(sus_drug)
    c.groupby_tnfa(checked_drug)
    c.join_tnfa_and_demo_reac()
    c.get_se()


if __name__ == "__main__":
    main()
