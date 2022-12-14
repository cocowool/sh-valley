import pandas as pd

# 帮助自动合并 Excel 文件的 Python 工具
# 合并文件有多种情况，分别列在下面
# * 将多个文件以不同 Sheet 合并到一个文件中
# * 将多个文件内容作为不同的行汇总到一个文件中
# * 将多个文件的行中的内容，汇总补充到总表中
#
# 依赖组件
# * pandas
# * openpyxl
#
# Author: Wang Shiqiang
# Github: http://github.com/cocowool


df_a = pd.DataFrame([
    ['Wang', 'Male', 19, ''],
    ['Zhang', 'Female', 18, ''],
    ['Zhao', 'Male', 20, ''],
    ['Lee', 'Female', 23, ''],
    ['Liu', 'Male', 23, '']
], columns=['Name','Gender','Age', 'Address'])

df_b = pd.DataFrame([
    ['Wang', 'Male', 19, 'Haidian'],
    ['Zhang', 'Female', 18, 'Chaoyang'],
    ['Zhao', 'Male', 20, 'Fengtai'],
    ['Lee', 'Female', 23, 'Fangshan'],
    ['Liu', 'Male', 23, 'Tongzhou']
], columns=['Name','Gender','Age', 'Address'])

# print(pd.concat([df_a,df_b]))
print(pd.merge(df_a,df_b,how='right',on=['Name','Gender', 'Age', 'Address']))

# source_file="/Users/shiqiang/Documents/CCB/09.技术支持组/20221127-容量梳理专题事项/20221212-应用容量反馈/容量数据202211-创新处反馈.xlsx"
# cmmp_file="/Users/shiqiang/Documents/CCB/09.技术支持组/20221127-容量梳理专题事项/20221212-应用容量反馈/容量数据202211-CMMP.xlsx"
# ssm_file="/Users/shiqiang/Documents/CCB/09.技术支持组/20221127-容量梳理专题事项/20221212-应用容量反馈/容量数据202211-SSM.xlsx"
# cloud_file="/Users/shiqiang/Documents/CCB/09.技术支持组/20221127-容量梳理专题事项/20221212-应用容量反馈/容量数据202211-cloud.xlsx"
# apm_file="/Users/shiqiang/Documents/CCB/09.技术支持组/20221127-容量梳理专题事项/20221212-应用容量反馈/容量数据202211-apm.xlsx"
# doap_file="/Users/shiqiang/Documents/CCB/09.技术支持组/20221127-容量梳理专题事项/20221212-应用容量反馈/容量数据202211_NASDOAP.xlsx"
# cmpm_file="/Users/shiqiang/Documents/CCB/09.技术支持组/20221127-容量梳理专题事项/20221212-应用容量反馈/副本容量数据202211-1-CMPM.xlsx"

# xlsx_source_file = pd.ExcelFile(source_file)
# xlsx_cmmp_file = pd.ExcelFile(cmmp_file)
# xlsx_ssm_file = pd.ExcelFile(ssm_file)
# xlsx_cloud_file = pd.ExcelFile(cloud_file)
# xlsx_apm_file = pd.ExcelFile(apm_file)
# xlsx_doap_file = pd.ExcelFile(doap_file)
# xlsx_cmpm_file = pd.ExcelFile(cmpm_file)


# df_source = pd.read_excel(xlsx_source_file, '明细表')
# df_cmmp = pd.read_excel(xlsx_cmmp_file, '明细表')
# df_ssm = pd.read_excel(xlsx_ssm_file, '明细表')
# df_cloud = pd.read_excel(xlsx_cloud_file, '明细表')
# df_apm = pd.read_excel(xlsx_apm_file, '明细表')
# df_doap = pd.read_excel(xlsx_doap_file, '明细表')
# df_cmpm = pd.read_excel(xlsx_cmpm_file, '明细表')

# df_source_cxc = df_source[df_source['应用运维团队'] == '技术创新发展处']
# df_cmmp_cxc = df_cmmp[df_cmmp['应用运维团队'] == '技术创新发展处']
# df_ssm_cxc = df_ssm[df_ssm['应用运维团队'] == '技术创新发展处']
# df_cloud_cxc = df_cloud[df_cloud['应用运维团队'] == '技术创新发展处']
# df_apm_cxc = df_apm[df_apm['应用运维团队'] == '技术创新发展处']
# df_doap_cxc = df_doap[df_doap['应用运维团队'] == '技术创新发展处']
# df_cmpm_cxc = df_cmpm[df_cmpm['应用运维团队'] == '技术创新发展处']

# df_out = pd.concat( [df_source_cxc,df_cmmp_cxc,df_ssm_cxc,df_cloud_cxc,df_apm_cxc,df_doap_cxc,df_cmpm_cxc] )

# out_file = "/Users/shiqiang/Downloads/out_concat.xlsx"
# df_out.to_excel(out_file)

# print(df_out)

# df_out = pd.merge(df_source,df_cmmp,left_index=True,right_index=True,how='left')
# df_out = pd.merge(df_out,df_ssm,left_index=True,right_index=True,how='left')
# df_out = pd.merge(df_out,df_cloud,left_index=True,right_index=True,how='left')
# df_out = pd.merge(df_out,df_apm,left_index=True,right_index=True,how='left')
# df_out = pd.merge(df_doap,df_ssm,left_index=True,right_index=True,how='left')
# df_out = pd.merge(df_cmpm,df_ssm,left_index=True,right_index=True,how='left')

# print(df_out[ df_out['应用运维团队'] == '技术创新发展处'])