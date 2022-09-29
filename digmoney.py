# 使用说明
# 在根目录下放入etherscan导出的xxx.csv
# 运行程序
import os
import csv
from time import sleep



result = {}
# 读取csv至字典
# csvFile = open("/Users/fernando/Desktop/SmartMinter.csv", "r")
# reader = csv.reader(open("/Users/fernando/Desktop/SmartMinter/bodl.csv", "r"))


path = "./SmartMinter/" #文件夹目录
files= os.listdir(path)
files.remove(".DS_Store")
print(files)
# sleep(100)
for collection in files:
    # result[collection] = []
    with open("./SmartMinter/"+collection,'r') as f:
        # Creating a list for each collection.
        reader = csv.reader(f)
        column = [row[4] for row in reader]
        # print(column)
        result[collection]=column

# print(result["Doom.csv"])

# for clt1 in files:
    # print(clt1)
    # print(result[clt1])
    # break

ret = []

for clt1 in files:
    for clt2 in files:
        for clt3 in files:
            for clt4 in files:
                if  clt4 == clt3 or clt4 == clt2 or clt4 == clt1 or clt3 == clt2 or clt3 == clt1 or clt2 == clt1:
                    continue
                else:
                    ret = ret + list(set(result[clt1]) & set(result[clt2]) & set(result[clt3]) & set(result[clt4]))

                # for clt5 in files:
                #     if clt5 == clt4 or clt5 == clt3 or clt5== clt2 or clt5== clt1 or clt4 == clt3 or clt4 == clt2 or clt4 == clt1 or clt3 == clt2 or clt3 == clt1 or clt2 == clt1:
                #         continue
                #     else:
                #         # print(clt1 + " and " + clt2 + " and " + clt3 + " in common")
                #         # tmp = [val for val in result[clt1] if val in result[clt2]]
                #         # tmp2 = [val for val in tmp if val in result[clt3]]
                #         # tmp3 = [val for val in tmp2 if val in result[clt4]]
                #         # print(list(set(result[clt1]).intersection(set(result[clt2]))))
                #         ret = ret + list(set(result[clt1]) & set(result[clt2]) & set(result[clt3]) & set(result[clt4]) & set(result[clt5]))

print(len(list(set(ret))))
print(list(set(ret)))