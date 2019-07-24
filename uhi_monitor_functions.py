# -*- coding: utf-8 -*-
"""
Created on Mon Jul  9 09:46:32 2018

@author: BBR
"""

import urllib.request
import json
import numpy as np
import pandas as pd 
import pymysql
pymysql.install_as_MySQLdb()
from sqlalchemy import create_engine
import datetime as dt

def stationsinfo(sheetname):
    filepath=r'./data/'
    filename=filepath+'站点分类.xlsx'
    stationsinfo=pd.read_excel(filename,sheetname)
    return stationsinfo
    
def sql2data(server,myQuery):
    engine=\
    create_engine\
    ('mysql://root:@{}:3306/tjclimatedata?charset=utf8'.format(server))
    df=pd.read_sql_query(myQuery,engine)
    return df 

def readDailyT(year,mon):
    server='10.226.110.138'
    myquery='''SELECT * FROM tem_day where Year={} and Mon={}'''.format(year,mon)
    df=sql2data(server,myquery)
    return df 

def nulldeal(df):
    df_copy=df.copy()
    df_copy=df_copy[df.TEM_Avg<9000]
    sta=df_copy['Station_Id_C']
    stanums=sta.value_counts()   # 计算相同数据的个数
    sta_deal=stanums[stanums>=28]   #剔除缺测三天(含三天）以上的站点，获取所需站点
    stanames=sta_deal.index      
    
    df.loc[df.TEM_Avg>9000,'TEM_Avg']=None
    df.loc[df.TEM_Max>9000,'TEM_Max']=None
    
    df=df.loc[df['Station_Id_C'].isin(stanames)] # 经清洗过后的数据
    return df 

def stationsdata_select(df,stanames):
    df=df.loc[df['Station_Id_C'].isin(stanames)] # 特定站点数据
    return df 

def getstationsinfo(stationsinfo):
# 全市郊区站、市区城市站、武清城市站、枫林路站、中新生态城站
    sta_all=stationsinfo('全市所有站')
    sta_suburb=stationsinfo('全市郊区站')
    sta_sq=stationsinfo('市区城市站')
    sta_wq=stationsinfo('武清城市站')
    sta_fl=stationsinfo('枫林路站')
    sta_zx=stationsinfo('中新生态城站')
    return sta_all,sta_suburb,sta_sq,sta_wq,sta_fl,sta_zx

def getstationsdata(df):
    sta_all,sta_suburb,sta_sq,sta_wq,sta_fl,sta_zx = getstationsinfo(stationsinfo)
    suburbdata=stationsdata_select(df,sta_suburb['站号'])  # 郊区
    sqdata=stationsdata_select(df,sta_sq['站号'])   # 市区
    wqdata=stationsdata_select(df,sta_wq['站号'])  # 武清
    fldata=stationsdata_select(df,sta_fl['站号'])  # 枫林路
    zxdata=stationsdata_select(df,sta_zx['站号'])  # 中新生态城
    alldata=stationsdata_select(df,sta_all['站号']) # 所有站点数据
    return alldata,suburbdata,sqdata,wqdata,fldata,zxdata

def stationsmean(df):
    alldata,suburbdata,sqdata,wqdata,fldata,zxdata=getstationsdata(df)
    subtemmean1=suburbdata.groupby('Station_Id_C').mean()  # 郊区站日平均温度
    subtemmean=subtemmean1['TEM_Avg'].mean()
    
    temmean=alldata.groupby('Station_Id_C').mean()  
    tmeandata=temmean[['Lon','Lat','TEM_Avg']] # 各站平均气温
    tmaxdata=temmean[['Lon','Lat','TEM_Max']] # 各站平均最高气温
    return tmeandata,tmaxdata,subtemmean

def stationsmeanplotdata(df):
    tmeandata,tmaxdata,subtemmean=stationsmean(df)
    uhi_tem=tmeandata.copy()
    uhi_tem['TEM_Avg']=uhi_tem['TEM_Avg']-subtemmean  # 城市热岛强度
    return tmeandata,tmaxdata,uhi_tem

def daily_uhi(df):
    alldata,suburbdata,sqdata,wqdata,fldata,zxdata=getstationsdata(df)
    subdaily=suburbdata.groupby('Day').mean()['TEM_Avg']  # 郊区逐日平均气温
    sqdaily=sqdata.groupby('Day').mean()['TEM_Avg']
    wqdaily=wqdata.groupby('Day').mean()['TEM_Avg']
    fldaily=fldata.groupby('Day').mean()['TEM_Avg']
    zxdaily=zxdata.groupby('Day').mean()['TEM_Avg']
    sq_uhi=sqdaily-subdaily
    wq_uhi=wqdaily-subdaily
    fl_uhi=fldaily-subdaily
    zx_uhi=zxdaily-subdaily
    uhi_all1=np.column_stack((sq_uhi,wq_uhi,fl_uhi,zx_uhi))
    uhi_all=pd.DataFrame(uhi_all1,index=None,columns=[u'市区',u'武清城区',u'解放南路示范区'\
                                           ,u'中新生态城示范区'])
    return uhi_all

def daily_uhi_sheet(uhi_all):
    region_mean=uhi_all.mean()
    region_mean.rename(column={'0':'平均热岛强度'})
    region_max=uhi_all.max()
    region_min=uhi_all.min()
    region_sxmean=uhi_all.loc[0:10,:].mean()
    region_zxmean=uhi_all.loc[10:20,:].mean()
    region_xxmean=uhi_all.loc[20:,:].mean()
    regiondata=pd.DataFrame([region_mean,region_max,region_min,region_sxmean\
                             ,region_zxmean,region_xxmean],index=['月平均值'\
                            ,'月最大值','月最小值','上旬平均值','中旬平均值','下旬平均值'])
    return regiondata
    
# 字符型数组转化成数值型
def str2num(df):
    df[['Lat','Lon','Year','Mon','Day','TEM_Avg','TEM_Max']]=\
    df[['Lat','Lon','Year','Mon','Day','TEM_Avg','TEM_Max']].apply(pd.to_numeric)
    return df 

df = readDailyT(2018,6)
df = str2num(df)
df=nulldeal(df)
## 统计分析
#tmeandata,tmaxdata,uhi_tem=stationsmeanplotdata(df) # 出图数据
#tocsv(tmeandata,tmaxdata,uhi_tem)
#
#uhi_all=daily_uhi(df)
#
#regiondata=daily_uhi_sheet(uhi_all)
#

