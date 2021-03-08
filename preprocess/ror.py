import csv
import math
import os
import pandas as pd

import config


class ROR:
    def __init__(self, jader=pd.read_csv('target/data.csv', encoding='shift_jis')):
        self.jader = jader

    def create_ror_file(self):
        with open('target/ror.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['drug', 'side_effect', 'a', 'b',
                             'c', 'd', 'ror', '95%CI+', '95%CI-'])

    def ror(self, side_effect, drug):
        """TNFα阻害薬と有害事象によるRORの算出とcsvファイルへの書き込み"""
        total = self.jader['識別番号'].nunique()
        try:
            a = self.jader[(self.jader['有害事象'] == side_effect) & (
                self.jader[drug] == 1)]['識別番号'].nunique()
            b = self.jader[self.jader[drug] == 1]['識別番号'].nunique() - a
            c = self.jader[(self.jader['有害事象'] == side_effect) & (
                self.jader[drug] != 1)]['識別番号'].nunique()
            d = total - (a+b+c)
            ROR = (a/b)/(c/d)
            ci_95m = math.exp(math.log(ROR)-1.96*(1/a+1/b+1/c+1/d)**0.5)
            ci_95p = math.exp(math.log(ROR)+1.96*(1/a+1/b+1/c+1/d)**0.5)

            # 追記モード
            with open('target/ror.csv', 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(
                    [drug, side_effect, a, b, c, d, ROR, ci_95m, ci_95p])
            print(a, b, c, d, ROR, ci_95m, ci_95p)
        except ValueError:
            print('バグった', side_effect, drug)

    def get_se_list(self, drug, num=30):
        """各薬の上位30の有害事象の抽出"""
        return list(
            self.jader[self.jader.is_tnf == 1].groupby('有害事象').sum().sort_values(
                drug, ascending=False
            )[drug].index[:num]
        )


drug_list = [
    'Infliximab',
    'Etanercept',
    'Adalimumab',
    'Golimumab',
    'Certolizumab',
    'is_tnf'
]


def main():
    r = ROR()
    r.create_ror_file()

    # 有害事象と薬の全パターンを実行する
    for d in drug_list:
        for s in r.get_se_list(d):
            r.ror(s, d)


if __name__ == "__main__":
    main()
