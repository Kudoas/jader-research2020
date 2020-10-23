import csv
import math
import os
import pandas as pd

import config

jader = pd.read_csv('target/data.csv', encoding='shift-jis')

# 書き込み用CSVファイルの作成
with open('target/ror.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['drug', 'side_effect', 'a', 'b',
                     'c', 'd', 'ror', '95%CI+', '95%CI-'])


def ror(df, side_effect, drug):
    total = df['識別番号'].nunique()
    try:
        a = df[(df['有害事象'] == side_effect) & (df[drug] == 1)]['識別番号'].nunique()
        b = df[df[drug] == 1]['識別番号'].nunique() - a
        c = df[(df['有害事象'] == side_effect) & (df[drug] != 1)]['識別番号'].nunique()
        d = total - (a+b+c)
        ROR = (a/b)/(c/d)
        ci_95m = math.exp(math.log(ROR)-1.96*(1/a+1/b+1/c+1/d)**0.5)
        ci_95p = math.exp(math.log(ROR)+1.96*(1/a+1/b+1/c+1/d)**0.5)

        # 追記モード
        with open('target/ror.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(
                [drug, side_effect, a, b, c, d, ROR, ci_95m, ci_95p])
        print(a, b, c, d)
        print(ROR, ci_95m, ci_95p)
    except ValueError:
        print('バグった', side_effect, drug)


drug_list = [
    'Infliximab',
    'Etanercept',
    'Adalimumab',
    'Golimumab',
    'Certolizumab',
    'is_tnf'
]


def get_se_list(drug):
    return list(
        jader[jader.is_tnf == 1].groupby('有害事象').sum().sort_values(
            drug, ascending=False
        )[drug].index[:30]
    )


# ループで回して全パターンを実行する
for d in drug_list:
    for s in get_se_list(d):
        ror(jader, s, d)
