# -*- coding: utf-8 -*-
"""
Created on Fri Mar 16 09:10:42 2018

@author: BBR
"""

import cmaps  # NCL色标模块
import maskout  #气象家园获取
from pykrige.ok import OrdinaryKriging  #克里金插值模块
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import math
from metpy.gridding.gridding_functions import (interpolate, remove_nan_observations,
                                               remove_repeat_coordinates)

plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文
plt.rcParams['axes.unicode_minus']=False  #用来正常显示负号

def uhi_kriging(shpFiles,lonlat,stationName,mLon,mLat,mTem,levels,outfilename):
       
    #绘图参数设置
    isStationInfoOn=False #站点信息是否标注
    isaxInfoOn=True  # 坐标轴信息是否标注
    cmap=cmaps.amwg256#BlAqGrYeOrReVi200 #色标选择 http://www.ncl.ucar.edu/Document/Graphics/color_table_gallery.shtml 参考该网址 MPL_YlOrRd  amwg256

    levels=levels
    fbl=0.05  #克里金插值空间分辨率
    picTitle='Temperature'
    zuobiaoSetInter=0.5 #坐标轴经纬度间隔设置
    
    
    # 初始化
    shpFile=shpFiles[0]
    bjshp=shpFiles[1]
    
    #天津经纬度范围设置
    llat=38.5
    ulat=40.3
    llon=116.7
    ulon=118.05
    
    fig=plt.figure(figsize=(6,6))
    plt.rc('font',size=15,weight='bold')
    ax=fig.add_subplot(111)
    
    # 底图读取及地图设置
    m=Basemap(llcrnrlon=llon,llcrnrlat=llat,urcrnrlon=ulon,urcrnrlat=ulat,\
        projection='cyl',resolution='c')   # 等距投影
    m.readshapefile(shpFile,'Name',linewidth=1,color='k')
    
    
    # 坐标系经纬度转换
    xllon,yllat=m(llon,llat)
    xulon,yulat=m(ulon,ulat)
    xmLon,ymLat=m(mLon,mLat)
    
    
    # meshgrid set the grid range
    gridx=np.arange(xllon,xulon,fbl)
    gridy=np.arange(yllat,yulat,fbl)
    
    Xlon,Ylat=np.meshgrid(gridx,gridy)

    #插值处理
    OK=OrdinaryKriging(xmLon,ymLat,mTem,variogram_model='linear',
               verbose=False,enable_plotting=False)
    z,ss=OK.execute('grid',gridx,gridy)
     
    
    cf=m.contourf(Xlon,Ylat,z,levels=levels,cmap=cmap)
    m.colorbar(cf,location='right',format='%.1f',size=0.3,\
            ticks=levels) #,label='单位：℃')
    
    # 添加站名信息
    if isStationInfoOn==True:
        m.scatter(xmLon,ymLat,c='k',s=10,marker='o')
        for i in range(0,len(xmLon)):
#            pass
            plt.text(xmLon[i],ymLat[i],stationName[i],va='bottom',fontsize=12)
           # plt.text(xmLon[i],ymLat[i],mTem[i],va='top',fontsize=12)
        
        plt.title(picTitle)  
     
    # 坐标轴标注
    if isaxInfoOn==True:
        lon_label=[]
        lat_label=[]
        lon_num=np.arange(xllon,xulon,zuobiaoSetInter)
        for lon in lon_num:
            lon_label.append(str(lon)+'°E')
        
        lat_num=np.arange(yllat,yulat,zuobiaoSetInter)
        for lat in lat_num:
            lat_label.append(str(lat)+'°N')
        
        plt.yticks(lat_num,lat_label)
        plt.xticks(lon_num,lon_label)
    
    
    # 白化
    maskout.shp2clip(cf,ax,bjshp,0.005588)  #0.005588为gis图周长信息
    
    # picture introduction
#    plt.show()
    plt.savefig(r'./results/'+outfilename, dpi=600)
    #图片输出
    '''
    plt.savefig('fig_province.', dpi=600, bbox_inches='tight')
    plt.clf()
    plt.close()
    '''

def metpyplot(shpFiles,lonlat,mLon,mLat,mTem):
    # 初始化
    #绘图参数设置
    isStationInfoOn=False #站点信息是否标注
    isaxInfoOn=False  # 坐标轴信息是否标注
    cmap=cmaps.BlAqGrYeOrReVi200 #色标选择 http://www.ncl.ucar.edu/Document/Graphics/color_table_gallery.shtml 参考该网址 MPL_YlOrRd  amwg256
    legendRange=[int(min(mTem)),math.ceil(max(mTem))]
    fbl=0.05  #克里金插值空间分辨率
    sebiaoNums=15 #色标个数
    picTitle='Temperature'
    zuobiaoSetInter=0.5 #坐标轴经纬度间隔设置
    
#    shpPath=r'./shp/TJ/'
#    shpName='TJ_all'
##    bjName='TJ_bj'
    shpFile=shpFiles[0]
#    bjshp=shpPath+bjName
    
    #天津经纬度范围设置
#    llat=38.5
#    ulat=40.3
#    llon=116.7
#    ulon=118.05
    llon=lonlat[0]
    ulon=lonlat[1]
    llat=lonlat[2]
    ulat=lonlat[3]
    
#    fig=plt.figure(figsize=(16,9))
    plt.rc('font',size=15,weight='bold')
#    ax=fig.add_subplot(111)
    
    # 底图读取及地图设置
    m=Basemap(llcrnrlon=llon,llcrnrlat=llat,urcrnrlon=ulon,urcrnrlat=ulat,\
        projection='cyl',resolution='c')   # 等距投影
    m.readshapefile(shpFile,'Name',linewidth=1,color='k')
    # 绘制经纬线
    parallels = np.arange(llat,ulat,0.5) 
    m.drawparallels(parallels,labels=[1,0,0,0],fontsize=10) # 绘制纬线

    meridians = np.arange(llon,ulon,0.5)
    m.drawmeridians(meridians,labels=[0,0,0,1],fontsize=10) # 绘制经线

    # 坐标系经纬度转换
    xllon,yllat=m(llon,llat)
    xulon,yulat=m(ulon,ulat)
    xmLon,ymLat=m(mLon,mLat)
    
    
    # meshgrid set the grid range
    gridx=np.arange(xllon,xulon,fbl)
    gridy=np.arange(yllat,yulat,fbl)
    
    Xlon,Ylat=np.meshgrid(gridx,gridy)

    #插值处理
#    OK=OrdinaryKriging(xmLon,ymLat,mTem,variogram_model='linear',
#               verbose=False,enable_plotting=False)
#    z,ss=OK.execute('grid',gridx,gridy)
    gx, gy, img = interpolate(xmLon, ymLat, mTem, \
                              interp_type='linear', hres=fbl)
     
    levels=np.linspace(legendRange[0],legendRange[1],sebiaoNums)
    cs=m.contourf(gx,gy,img,levels,cmap=cmap)
    m.colorbar(cs)
    
#    cf=m.contourf(Xlon,Ylat,z,levels=levels,cmap=cmap)
#    m.colorbar(cf,location='right',format='%.1f',size=0.3,\
#            ticks=np.linspace(legendRange[0],legendRange[1],sebiaoNums),label='单位：℃')
#    
        # 添加站名信息
    if isStationInfoOn==True:
        m.scatter(xmLon,ymLat,c='k',s=10,marker='o')
        for i in range(0,len(xmLon)):
#            pass
            plt.text(xmLon[i],ymLat[i],stationName[i],va='bottom',fontsize=12)
           # plt.text(xmLon[i],ymLat[i],mTem[i],va='top',fontsize=12)
        
        plt.title(picTitle)  
     
    # 坐标轴标注
    if isaxInfoOn==True:
        lon_label=[]
        lat_label=[]
        lon_num=np.arange(xllon,xulon,zuobiaoSetInter)
        for lon in lon_num:
            lon_label.append(str(lon)+'°E')
        
        lat_num=np.arange(yllat,yulat,zuobiaoSetInter)
        for lat in lat_num:
            lat_label.append(str(lat)+'°N')
        
        plt.yticks(lat_num,lat_label)
        plt.xticks(lon_num,lon_label)
    
    
    # 白化
#    maskout.shp2clip(cf,ax,bjshp,0.005588)  #0.005588为gis图周长信息
    
    # picture introduction
    plt.show()
    
    #图片输出
#    '''
#    plt.savefig('fig_province.png', dpi=600, bbox_inches='tight')
#    plt.clf()
#    plt.close()
#    '''
#def lonlatcsvdataread(dataFile,ele='TEM_Avg'):
#    #mData=np.loadtxt(dataFile)  #数据读取
#    mData=pd.read_csv(dataFile,header=0,sep=',')
#    #mData=pd.read_csv(dataFile,header=None,names=['stationid','lon','lat','T'])
#    
#    # 数值提取
#    stationName=mData['Station_Id_C']
#    stationName.enconding='utf-8'
#    stationName=stationName
#    mLon=mData['Lon']
#    mLat=mData['Lat']
#    mTem=mData[ele]
#    return stationName,mLon,mLat,mTem

#def uhidailyfileread(datafile):
#    mData=pd.read_csv(datafile,header=0,sep=',')
#    mData=mData[['市区','武清城区','解放南路示范区','中新生态城示范区']]
#    mDatalen=max(mData.index)+1
#    mData.index=np.arange(1,mDatalen+1)
#    return mData

def iniSet():
    shpPath=r'./shp/TJ/'
    shpName='TJ_all' #shp数据
    bjName='TJ_bj'  #白化用
    shpFile=shpPath+shpName
    bjshp=shpPath+bjName
    shpFiles=[shpFile,bjshp]    
    #天津经纬度范围设置
    llat=38.5
    ulat=40.3
    llon=116.7
    ulon=118.05
    lonlat=[llon,ulon,llat,ulat]
    return shpFiles,lonlat

def tmeanplot(shpFiles,lonlat,tmeandata,yr,mon):
    tmean_levels=np.arange(22,30.5,0.5)
    stationName=tmeandata.index
    mLon=tmeandata.Lon
    mLat=tmeandata.Lat
    mTem=tmeandata.TEM_Avg
    uhi_kriging(shpFiles,lonlat,stationName,mLon,mLat,mTem,tmean_levels,\
                'tmean_{}_{}.png'.format(yr,mon))

def tmaxplot(shpFiles,lonlat,tmaxdata,yr,mon):
    tmax_levels=np.arange(28,36.5,0.5)
    stationName=tmaxdata.index
    mLon=tmaxdata.Lon
    mLat=tmaxdata.Lat
    mTem=tmaxdata.TEM_Max
    uhi_kriging(shpFiles,lonlat,stationName,mLon,mLat,mTem,tmax_levels,\
                'tmax_{}_{}.png'.format(yr,mon))

def uhiplot(shpFiles,lonlat,uhi_tem,yr,mon):
    uhi_levels=np.arange(-4,4.5,0.5)
    stationName=uhi_tem.index
    mLon=uhi_tem.Lon
    mLat=uhi_tem.Lat
    mTem=uhi_tem.TEM_Avg
    uhi_kriging(shpFiles,lonlat,stationName,mLon,mLat,mTem,uhi_levels,\
                'uhi_{}_{}.png'.format(yr,mon))

def uhiminusplot(shpFiles,lonlat,uhi_tem,yr,mon):
    uhi_levels=np.arange(-2,2.2,0.2)
    stationName=uhi_tem.index
    mLon=uhi_tem.Lon
    mLat=uhi_tem.Lat
    mTem=uhi_tem.TEM_Avg
    uhi_kriging(shpFiles,lonlat,stationName,mLon,mLat,mTem,uhi_levels,\
                'uhi_minus_{}_{}.png'.format(yr,mon))

def dailyuhiplot(uhi_daily,yr,mon):
    uhi_daily_len=max(uhi_daily.index)+1
    uhi_daily.index=np.arange(1,uhi_daily_len+1)
    plt.figure()
    uhi_daily.plot(use_index=True,figsize=(10,7),fontsize=14)
    plt.xlabel("日期",fontsize=14) 
    plt.ylabel("热岛强度（℃）",fontsize=14) 
    plt.legend(loc='best',fontsize=14)
    plt.savefig(r'./results/'+'daily_uhi_{}_{}.png'.format(yr,mon), dpi=600)
    
#if __name__=='__main__':
#
#    shpFiles,lonlat=iniSet()
#
#    tmeanplot(shpFiles,tmeandata)
#    tmaxplot(shpFiles,tmaxdata)
#    uhiplot(shpFiles,uhi_tem)
#   
#    dailyuhiplot(uhi_daily)



