import os
import os.path
import codecs
import pandas

# 博客的目录
# ~/Projects/edulinks-blog/source/_posts/*md

filePaths = []
fileContents = []

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

print(filePaths)