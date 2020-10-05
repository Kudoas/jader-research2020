import pandas as pd
import numpy as np
import codecs
import os

os.chdir("./data/jader")

with codecs.open('drug202008.csv', "r", "Shift-JIS", "ignore") as file:
    jdrug = pd.read_table(file, delimiter=",")

# 重複削除
jdrug.drop_duplicates(inplace=True)
sus_drug = jdrug[jdrug["医薬品の関与"] == "被疑薬"]

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
    (sus_drug["医薬品（一般名）"] == "Humira")  # 追加
)
is_golimumab = (
    (sus_drug["医薬品（一般名）"] == "ゴリムマブ（遺伝子組換え）") |
    (sus_drug["医薬品（一般名）"] == "ゴリムマブ")
)
is_certolizumab = (
    (sus_drug["医薬品（一般名）"] == "セルトリズマブペゴル") |
    (sus_drug["医薬品（一般名）"] == "セルトリズマブ　ペゴル（遺伝子組換え）") |
    (sus_drug["医薬品（一般名）"] == "ＣＥＲＴＯＬＩＺＵＭＡＢ　ＰＥＧＯＬ")  # 追加
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

sus_drug[is_tnf].to_csv('check_tnf_drug.csv',
                        encoding='shift-jis', index=False)
sus_drug = sus_drug[
    ['識別番号', "医薬品（一般名）", 'Infliximab', 'Etanercept',
        'Golimumab', 'Adalimumab', 'Certolizumab']
]
sus_drug["is_tnf"] = is_tnf
sus_drug = sus_drug.drop_duplicates()

with codecs.open('demo202008.csv', "r", "Shift-JIS", "ignore") as file:
    demo = pd.read_table(file, delimiter=",")
# 重複削除
demo.drop_duplicates(inplace=True)
demo1 = demo[['識別番号', '性別', '年齢', '報告年度・四半期']]
outer_drug_demo = pd.merge(demo1, sus_drug, on="識別番号", how='outer')

# 欠損値の0埋め
outer_drug_demo[['Infliximab', 'Etanercept', 'Adalimumab',
                 'Golimumab', 'Certolizumab', 'is_tnf']].fillna(0)
# concat 横結合：レコード数が同じことに注意
outer_drug_demo = pd.concat([outer_drug_demo[['識別番号', '性別', '年齢', '報告年度・四半期', "医薬品（一般名）"]], outer_drug_demo[[
                            'Infliximab', 'Etanercept', 'Adalimumab', 'Golimumab', 'Certolizumab', 'is_tnf']].fillna(0)], axis=1)

with codecs.open('reac202008.csv', "r", "Shift-JIS", "ignore") as file:
    reac = pd.read_table(file, delimiter=",")
# 重複削除
reac1 = reac[['識別番号', '有害事象']].drop_duplicates()
jader = pd.merge(reac1, outer_drug_demo, on='識別番号')

jader.to_csv('jader.csv', encoding='shift-jis', index=False)
