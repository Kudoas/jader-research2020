import codecs
import csv
import numpy as np
import os
import pandas as pd

import config


def drop_columns(df: 'DataFrame', keys: list):
    try:
        return df.drop(keys, axis=1, inplace=False)
    except KeyError:
        print('DataFrameに指定したKeyはありません')


def keep_columns(df: 'DataFrame', keys: list):
    try:
        return df[keys]
    except KeyError:
        print('DataFrameに指定したKeyはありません')


def one_to_many_dict(ls: list) -> dict:
    d = {}
    for s in set(ls):
        d[s] = []
    return d


# 解析用のデータベースの作成
class Jader:
    def __init__(self, drug: 'DataFrame', demo: 'DataFrame', reac: 'DataFrame'):
        """JADERのオリジナルデータ"""
        self.drug = drug
        self.demo = demo
        self.reac = reac

    def extract_suspicious(self) -> "DataFrame":
        """被疑薬のみの抽出"""
        return self.drug[drug["医薬品の関与"] == "被疑薬"]

    def get_tnfa_drug(self) -> dict:
        with open('master/tnfa_drug202008.csv', newline='') as f:
            rows = csv.reader(f)
            drug_list = [
                'infliximab', 'etanercept', 'adalimumab', 'golimumab', 'certolizumab'
            ]
            drug_dict = one_to_many_dict(drug_list)
            for row in rows:
                for drug in drug_list:
                    if drug == row[0]:
                        drug_dict[row[0]].append(row[1])
        return drug_dict

    def check_tnfa(self, df: "DataFrame", tnfa_dict: dict) -> "DataFrame":
        """TNF-α阻害薬に分類される5剤（インフリキシマブ、エタネルセプト、アダリズマブ、ゴリズマブ、セルトリズマブ ぺゴル）の選択

        該当の5剤、TNF-α阻害薬の服用の有無に対しフラグをつける
        """
        is_infliximab = df["医薬品（一般名）"].isin(tnfa_dict['infliximab'])
        is_etanercept = df["医薬品（一般名）"].isin(tnfa_dict['etanercept'])
        is_adalimumab = df["医薬品（一般名）"].isin(tnfa_dict['adalimumab'])
        is_golimumab = df["医薬品（一般名）"].isin(tnfa_dict['golimumab'])
        is_certolizumab = df["医薬品（一般名）"].isin(tnfa_dict['certolizumab'])
        df['Infliximab'] = is_infliximab
        df['Etanercept'] = is_etanercept
        df['Adalimumab'] = is_adalimumab
        df['Golimumab'] = is_golimumab
        df['Certolizumab'] = is_certolizumab
        df = df.replace(False, 0).replace(True, 1)
        is_tnf = (
            (df['Infliximab'] == 1) |
            (df['Etanercept'] == 1) |
            (df['Golimumab'] == 1) |
            (df['Adalimumab'] == 1) |
            (df['Certolizumab'] == 1)
        )
        df["is_tnf"] = is_tnf
        df = drop_columns(df, ['医薬品連番', '医薬品（一般名）', '使用理由'])

        # 重複削除し、FalseとTrueを0と1に置き換え
        df = df.drop_duplicates().replace(False, 0).replace(True, 1)
        return df

    def groupby_tnfa(self, sus_drug: 'DataFrame') -> 'DataFrame':
        """TNF-α阻害薬を服用した患者を1人1レコードへ変換"""
        return sus_drug[sus_drug["is_tnf"] == 1].groupby("識別番号").max()

    def join_tnfa_and_demo_reac(self):
        """drug, demo, jaderの結合

        drug, demo, jaderを結合し、csvファイルとして保存する
        """
        drug = pd.read_csv('target/tnf_druger.csv', encoding='shift_jis')

        # 重複削除
        self.demo.drop_duplicates(inplace=True)
        outer_drug_demo = pd.merge(
            self.demo[['識別番号', '性別', '年齢', '報告年度・四半期']], drug, on="識別番号", how='outer'
        )

        # 欠損値の0埋め
        outer_drug_demo[
            [
                'Infliximab', 'Etanercept', 'Adalimumab', 'Golimumab', 'Certolizumab', 'is_tnf'
            ]
        ].fillna(0)
        outer_drug_demo = pd.concat(
            [
                outer_drug_demo[['識別番号', '性別', '年齢', '報告年度・四半期']],
                outer_drug_demo[
                    ['Infliximab', 'Etanercept', 'Adalimumab',
                     'Golimumab', 'Certolizumab', 'is_tnf']
                ].fillna(0)
            ], axis=1
        )

        # 重複削除
        jader = pd.merge(
            self.reac[['識別番号', '有害事象']].drop_duplicates(inplace=False),
            outer_drug_demo, on='識別番号', how='outer'
        )
        return jader

    def get_se(self):
        """tnfαを飲んだ人の有害事象の集計データの保存"""
        jader = pd.read_csv('target/data.csv', encoding='shift_jis')
        groupby_jader = jader[jader.is_tnf == 1].groupby('有害事象')
        return groupby_jader.sum().sort_values('is_tnf', ascending=False)['is_tnf']


def main():
    with codecs.open('jader/drug202008.csv', "r", "Shift-JIS", "ignore") as file:
        drug = pd.read_table(file, delimiter=",")

    with codecs.open('jader/demo202008.csv', "r", "Shift-JIS", "ignore") as file:
        demo = pd.read_table(file, delimiter=",")

    with codecs.open('jader/reac202008.csv', "r", "Shift-JIS", "ignore") as file:
        reac = pd.read_table(file, delimiter=",")

    j = Jader(drug, demo, reac)
    sus_drug = keep_columns(
        j.extract_suspicious(),
        ['識別番号', '医薬品連番', '医薬品（一般名）', '使用理由']
    )
    tnfa_drug_dict = j.get_tnfa_drug()
    checked_drug = j.check_tnfa(sus_drug, tnfa_drug_dict)
    j.groupby_tnfa(checked_drug).to_csv(
        'target/tnf_druger.csv', encoding='shift_jis'
    )
    jader = j.join_tnfa_and_demo_reac()
    jader.to_csv('target/data.csv', encoding='shift_jis')
    j.get_se().to_csv('target/count_side_effect.csv', encoding='shift_jis')


if __name__ == "__main__":
    main()
