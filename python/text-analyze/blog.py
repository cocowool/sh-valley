import os
import os.path
import codecs
import pandas
import jieba
import numpy
import re
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# 博客的目录
# ~/Projects/edulinks-blog/source/_posts/*md

filePaths = []
fileContents = []

# 文本读取，构建语料库
for root, dirs, files in os.walk( "/Users/shiqiang/Projects/edulinks-blog/source/_posts", topdown = False , followlinks = True ):
# for root, dirs, files in os.walk( "~/Projects/blog-backup/_posts", followlinks = True):
    # ~/Projects/blog-backup/_posts/
    # print(root)
    # print(dirs)
    # print(files)
    for name in files:
        if name.endswith(".md"):
            # print(name)
            filePath = os.path.join(root, name)
            filePaths.append( filePath )
            fh = codecs.open(filePath, 'r', 'utf-8')
            file_content = fh.read()
            fh.close()
            fileContents.append(file_content)

corpos = pandas.DataFrame({
    'filePath': filePaths,
    'fileContent': fileContents
})

# 分词
segments = []
filePaths = []
for index, row in corpos.iterrows():
    filePath = row['filePath']
    fileContent = row['fileContent']
    # 去掉标点符号
    fileContent = re.sub(r"[\s+\n\r\"$\';:：]","", fileContent)
    # 暂时先去掉英文
    fileContent = re.sub(r"[a-zA-Z0-9]","", fileContent)
    segs = jieba.cut(fileContent)
    for seg in segs:
        segments.append(seg)
        filePaths.append(filePath)

segmentDataFrame = pandas.DataFrame({
    'segment' : segments,
    'filePath' : filePaths
})


# 统计词频
segStat = segmentDataFrame.groupby(by="segment")["segment"].agg([("计数", numpy.size)]).reset_index().sort_values(by=['计数'],ascending=False)


stopwords = pandas.read_csv("./StopWordsCN.txt", encoding='utf8',index_col=False)

fSegStat = segStat[~segStat.segment.isin(stopwords)]

# 画词云
wordcloud = WordCloud( font_path = './CHXBS.TTF', background_color = "white")
words = fSegStat.set_index('segment').to_dict()
wordcloud.fit_words(words['计数'])
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.show()

# print(segStat)
# print(segmentDataFrame)
# print(fSegStat)