#!/usr/bin/env python
# coding: utf-8

# In[1]:


# import jieba
import pandas as pd
import numpy as np
from pymongo import MongoClient
get_ipython().run_line_magic('matplotlib', 'inline')
import matplotlib.pyplot as plt


# # 從資料庫拉資料

# In[2]:


client = MongoClient("mongodb://localhost:27017/")
db = client.news_textmining
news_title_collection = db.news_title_collection
news_amount = db.news_amount

cursor = news_title_collection.find()
dataset_main = pd.DataFrame([d for d in cursor])

cursor = news_amount.find()
news_amount = pd.DataFrame([d for d in cursor])


# # 資料整理
# 
# 對新聞標題作處理，將標號（e.g. 1.）去除  
# 將日期拆開成年、月、日

# In[3]:


dataset = dataset_main.drop(columns=["_id"])
dataset["title"] = dataset["title"].str.replace("(\d+)(\.)", "", regex=True)
dataset["title"] = dataset["title"].dropna()
dataset[dataset["title"].fillna("NA").str.contains("歐巴馬")]

news_amount = news_amount.drop(columns=["_id", "start_date", "key_word"])
news_amount["month"] = pd.to_numeric(news_amount["end_date"].str.split("-", expand = True)[1], errors = "coerce")
news_amount["year"] = pd.to_numeric(news_amount["end_date"].str.split("-", expand = True)[0], errors = "coerce")
news_amount = news_amount.drop(columns=["end_date"])


# In[9]:


dataset


# # 各關鍵字的出現次數
# 
# 比較剔除國際相關關鍵字後，新聞數量的增減。

# In[4]:


tmp1 = dataset[["key_word", "title"]].groupby(by="key_word").count().sort_values(by="title")

dataset[dataset["position"]=="國際"] = np.nan
dataset[dataset["position"]=="國際焦點"] = np.nan
dataset[dataset["position"]=="國際財經"] = np.nan
dataset[dataset["position"]=="國際村"] = np.nan
dataset[dataset["position"]=="國際‧運動"] = np.nan
tmp2 = dataset[["key_word", "title"]].groupby(by="key_word").count().sort_values(by="title")

tmp = pd.merge(tmp1, tmp2, on="key_word")
tmp


# # 資料對接
# 
# 篩選政黨惡鬥、朝野對立、藍綠對立、超越藍綠關鍵字

# In[5]:


dataset["month"] = pd.to_numeric(dataset["date"].str.split("-", expand = True)[1], errors = "coerce")
dataset["year"] = pd.to_numeric(dataset["date"].str.split("-", expand = True)[0], errors = "coerce")

dataset = dataset.sort_values(by=["key_word","year"])
des1 = dataset[dataset["key_word"] == "政黨惡鬥"][["year", "month", "key_word"]].groupby(by=["year", "month"]).count().reset_index()
des1 = des1.rename(columns={"key_word":"政黨惡鬥"})
des2 = dataset[dataset["key_word"] == "朝野對立"][["year", "month", "key_word"]].groupby(by=["year", "month"]).count().reset_index()
des2 = des2.rename(columns={"key_word":"朝野對立"})
des3 = dataset[dataset["key_word"] == "藍綠對立"][["year", "month", "key_word"]].groupby(by=["year", "month"]).count().reset_index()
des3 = des3.rename(columns={"key_word":"藍綠對立"})
des4 = dataset[dataset["key_word"] == "藍綠惡鬥"][["year", "month", "key_word"]].groupby(by=["year", "month"]).count().reset_index()
des4 = des4.rename(columns={"key_word":"藍綠惡鬥"})
des5 = dataset[dataset["key_word"] == "超越藍綠"][["year", "month", "key_word"]].groupby(by=["year", "month"]).count().reset_index()
des5 = des5.rename(columns={"key_word":"超越藍綠"})

merged = pd.merge(des1, des2, on=["year", "month"], how="outer")
merged = pd.merge(merged, des3, on=["year", "month"], how="outer")
merged = pd.merge(merged, des4, on=["year", "month"], how="outer")
merged = pd.merge(merged, des5, on=["year", "month"], how="outer")

merged = pd.merge(merged, news_amount, on=["year", "month"], how="outer")
merged = merged.sort_values(by=["year", "month"])

merged = merged.loc[merged["year"]>=1990,:]
merged.fillna(0, inplace=True)


# # 建構比率資料集（ratio）

# In[6]:


ratio_month = pd.DataFrame({"year":merged["year"].unique().tolist()})
for kw in ["政黨惡鬥", "朝野對立", "藍綠對立", "藍綠惡鬥", "超越藍綠"]:
    tmp = merged.loc[:,["{}".format(kw),"year","month"]]
    tmp["ratio"] = tmp["{}".format(kw)].divide(merged["amount"])
    tmp = tmp.loc[:,["ratio","year","month"]].groupby(by=["year","month"], as_index=False).mean()
    tmp.rename(columns={"ratio":"ratio_{}".format(kw)}, inplace=True)
    ratio_month = pd.merge(ratio_month, tmp)

ratio_month = pd.merge(ratio_month, merged.loc[:,["year", "month", "amount"]], on=["year","month"])
ratio_month["ratio_sum"] = ratio_month.iloc[:, 2:7].sum(axis=1)
ratio_month.index = pd.date_range(start='01/01/1990', end='12/31/2018', freq='1M')
ratio_month = ratio_month.drop(["year", "month"],axis=1)
ratio_month


# # 畫圖

# In[7]:


plt.rcParams["font.sans-serif"] = ["simhei"]
plt.figure(figsize=(20, 10))
plt.plot(ratio_month["ratio_sum"])
plt.ylabel("比率")
plt.xlabel("年度")
plt.twinx().plot(ratio_month["amount"],color="green")
plt.title("聯合知識庫新聞關鍵字搜尋，政治分裂新聞量比率結果時間趨勢圖")
plt.ylabel("新聞量")
plt.legend(prop={'size': 10}, title="關鍵字")


# In[11]:


ratio_month.plot(subplots=True, figsize=(20, 10),ylim=(0,0.005))

