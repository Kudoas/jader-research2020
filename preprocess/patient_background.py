import pandas as pd
import os

import config


class Background:
    def __init__(
        self,
        jader=pd.read_csv('target/data.csv', encoding='shift_jis'),
        drug_info_path='target/drug_info.csv',
        patient_sex_path='target/sex.csv',
        patient_age_path='target/age.csv'
    ):
        self.jader = jader
        self.drug_info_path = drug_info_path
        self.patient_sex_path = patient_sex_path
        self.patient_age_path = patient_age_path

    def get_drug_freq(self):
        """年度別の各tnfα阻害薬の使用状況の集計"""
        df = self.jader[
            ['識別番号', '報告年度・四半期', 'Infliximab', 'Etanercept',
                'Adalimumab', 'Golimumab', 'Certolizumab', 'is_tnf']
        ]
        df.drop_duplicates(inplace=True)
        year = df['報告年度・四半期'].str[:4]
        df = pd.concat(
            [year, df[
                ['Infliximab', 'Etanercept', 'Adalimumab',
                    'Golimumab', 'Certolizumab', 'is_tnf']
            ].fillna(0)], axis=1
        )
        df.groupby('報告年度・四半期').sum().to_csv(
            self.drug_info_path,
            encoding="shift_jis"
        )

    def describe_age(self):
        """tnfα阻害薬を服用している患者の性別の集計"""
        jader_is_tnf = self.jader[self.jader['is_tnf'] == 1]
        jader_is_tnf = jader_is_tnf[['識別番号', '性別', '年齢', 'is_tnf']]

        jader_is_tnf.drop_duplicates(inplace=True)
        count_is_tnf = len(jader_is_tnf)

        grouped_jader_sex = jader_is_tnf.groupby('性別')
        table2_sex = grouped_jader_sex.sum()
        table2_sex['per_total'] = table2_sex['is_tnf'] / count_is_tnf * 100
        table2_sex.to_csv(self.patient_sex_path, encoding="shift_jis")

    def describe_sex(self):
        """tnfα阻害薬を服用している年齢の集計"""
        jader_is_tnf = self.jader[self.jader['is_tnf'] == 1]
        jader_is_tnf = jader_is_tnf[['識別番号', '性別', '年齢', 'is_tnf']]

        jader_is_tnf.drop_duplicates(inplace=True)
        count_is_tnf = len(jader_is_tnf)

        grouped_jader_age = jader_is_tnf.groupby('年齢')
        table2_age = grouped_jader_age.sum()
        table2_age['per_total'] = table2_age['is_tnf'] / count_is_tnf * 100
        table2_age.to_csv(self.patient_age_path, encoding="shift_jis")


def main():
    b = Background()
    b.get_drug_freq()
    b.describe_age()
    b.describe_sex()


if __name__ == "__main__":
    main()
