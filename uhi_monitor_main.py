# -*- coding: utf-8 -*-
"""
Created on Mon Jul  9 09:46:32 2018

@author: BBR
"""

import uhi_monitor_functions as um
import uhi_plot_functions as up
import pandas as pd

def savedata(tmeandata,tmaxdata,uhi_tem,uhi_daily,regiondata,yr,mon):
    tmeandata.to_csv('./data/tmean_{}_{}.csv'.format(str(yr),str(mon)))
    tmaxdata.to_csv('./data/tmax_{}_{}.csv'.format(str(yr),str(mon)))
    uhi_tem.to_csv('./data/uhi_{}_{}.csv'.format(str(yr),str(mon)))
    uhi_daily.to_csv('./data/uhi_daily_{}_{}.csv'.format(str(yr),str(mon)))
    regiondata.to_excel('./results/uhidailymean_region_{}_{}.xls'\
                        .format(str(yr),str(mon)))
    
def alldataget(yr,mon):
    df = um.readDailyT(yr,mon)
    df = um.str2num(df)
    df=um.nulldeal(df)  #缺测处理
    tmeandata,tmaxdata,uhi_tem=um.stationsmeanplotdata(df) # 出图数据
    uhi_daily=um.daily_uhi(df)
    regiondata=um.daily_uhi_sheet(uhi_daily)
    savedata(tmeandata,tmaxdata,uhi_tem,uhi_daily,regiondata,yr,mon)
    return tmeandata,tmaxdata,uhi_tem,uhi_daily

def minus_uhi_cal(yr,mon):
    tmeandata,tmaxdata,uhi_tem_cur,uhi_daily=alldataget(yr,mon)
    tmeandata,tmaxdata,uhi_tem_past,uhi_daily=alldataget(yr-1,mon)
    uhi_tem_cur['stationid']=uhi_tem_cur.index
    uhi_tem_past['stationid']=uhi_tem_past.index
    uhi_merge=pd.merge(uhi_tem_cur,uhi_tem_past,on='stationid')
    uhi_merge['minus']=uhi_merge['TEM_Avg_x']-uhi_merge['TEM_Avg_y']
    uhi_minus=uhi_merge[['Lon_x','Lat_y','minus']]
    uhi_minus.index=uhi_merge['stationid']
    uhi_minus.columns=['Lon','Lat','TEM_Avg']
#    uhi_minus.rename(columns={'Lon_x':'Lon','Lat_x':'Lat','minus':'TEM_Avg'},\
#                     inplace = True)
    return uhi_minus
    

def alldataplot(yr,mon):
    uhi_minus=minus_uhi_cal(yr,mon)
    tmeandata,tmaxdata,uhi_tem,uhi_daily=alldataget(yr,mon)
    shpFiles,lonlat=up.iniSet()
    up.tmeanplot(shpFiles,lonlat,tmeandata,yr,mon)
    up.tmaxplot(shpFiles,lonlat,tmaxdata,yr,mon)
    up.uhiplot(shpFiles,lonlat,uhi_tem,yr,mon)
    up.uhiminusplot(shpFiles,lonlat,uhi_minus,yr,mon)
    up.dailyuhiplot(uhi_daily,yr,mon)


    
yr=2018
mon=6

alldataplot(yr,mon)   
