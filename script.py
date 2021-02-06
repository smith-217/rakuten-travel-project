#!/usr/bin/env python
# -*- coding: utf-8 -*-
#使用するパッケージのインポート
import requests
import json
import numpy as np
import pandas as pd
import pprint as pp
import time
import csv
import datetime
import os

#地区コード取得
header_dist3=[]

res=requests.get('https://app.rakuten.co.jp/services/api/Travel/GetAreaClass/20131024?applicationId=######&format=json&largeClassCode=japan')
Dist=res.json()
for S in Dist['areaClasses']['largeClasses']:
    for T in S['largeClass']:
        #print(T)
        if len(T) ==1:
            #print(T['middleClasses'])
            for U in T['middleClasses']:
                #print(U['middleClass'])
                for V in U['middleClass']:
                    #print(V)
                    if len(V)==2:
                        mid_list=[]
                        mid_code=[]
                        mid_code.append(V['middleClassCode'])
                        mid_name=[]
                        mid_name.append(V['middleClassName'])
                        mid_list=mid_code+mid_name
                        #print(mid_list)
                    else:
                        for W in V['smallClasses']:
                            #print(W['smallClass'])
                            for X in W['smallClass']:
                                #print(X)
                                if len (X)==2:
                                    small_list=[]
                                    small_code=[]
                                    small_code.append(X['smallClassCode'])
                                    small_name=[]
                                    small_name.append(X['smallClassName'])
                                    small_list=small_code+small_name
                                    #print(small_list)
                                    header_dist=mid_list+small_list
                                
                                else:
                                    detail_list=[]
                                    for Y in X['detailClasses']:
                                        #print(Y['detailClass'])
                                        detail_code=[]
                                        detail_code.append(Y['detailClass']['detailClassCode'])
                                        detail_name=[]
                                        detail_name.append(Y['detailClass']['detailClassName'])
                                        detail_list=detail_code+detail_name
                                        header_dist2=header_dist+detail_list
                                        #print(header_dist2)
                                        header_dist3.append(header_dist2)
                            if len(X)==2:
                                header_dist3.append(header_dist)

df=pd.DataFrame(header_dist3,columns=['middleClassCode','middleClassName','smallClassCode','smallClassName','detailClassCode','detailClassName'])
df.to_csv('dist.csv')               

#ホテル情報を取得する関数
def gethoteldata():
    global Info
    global destination
    global payload
    global Data

    try:
        for A in range(len(Data['hotels'])):
            accomodation_hotel=[]
            accomodation_room=[]
            
            for keyrange in range(len(Data['hotels'][A])):
                #print(Data['hotels'][A][keyrange].keys())
                for Akey in Data['hotels'][A][keyrange].keys():
                    if Akey!='roomInfo':
                        for hotelinfo in Data['hotels'][A][keyrange][Akey].values():
                            accomodation_hotel.append(hotelinfo)
                    
                    else:
                        for Aroom in Data['hotels'][A][keyrange][Akey]:
                            for roominfo in Aroom.keys():
                                for roomdetail in Aroom[roominfo].values():
                                    accomodation_room.append(roomdetail)

            accomodation=destination+accomodation_hotel+accomodation_room
            Info.append(accomodation)
    except:
        pass

#ページをめくる関数
def pager():
    global payload
    global Data
    if 'pagingInfo' not in Data:
        pass
    else:
        while int(payload['page']) < Data['pagingInfo']['pageCount']:
            time.sleep(1)
            i = int(payload['page'])+1
            payload['page']=i
            
            try:
                res=requests.get(url,params=payload)
                Data=res.json()
            
            except:
                pass
            
            if 'pagingInfo' not in Data:
                break
            else:
                gethoteldata()


#全ての地域における１ヶ月分のデータ取得を実行するための関数
def GetData():
    global Info
    global payload
    global areacode
    global destination
    global Data
    
    #リクエストURLの作成
    url='https://app.rakuten.co.jp/services/api/Travel/VacantHotelSearch/20170426'
    payload={'applicationId':#######,'checkinDate':'0','checkoutDate':'0',
             'largeClassCode':'japan','middleClassCode':'0','smallClassCode':'0',
             'detailClassCode':'0','page':1,'responseType':'middle','formatVersion':2,'searchPattern':1,
             'maxCharge':999999999,'minCharge':0,'sort':'-roomCharge', 'elements':'pagingInfo,hotelNo,lowestCharge,highestCharge,roomClass,roomName,planId,payment,stayDate,dinnerSelectFlag,withDinnerFlag,breakfastSelectFlag,withBreakfastFlag,total'}  

    #日付取得
    checkin=datetime.date.today()
    checkindate=checkin.isoformat()
    payload['checkinDate']=checkindate

    checkout=checkin+ datetime.timedelta(days=1)
    checkoutdate=checkout.isoformat()
    payload['checkoutDate']=checkoutdate

    new_dir_path = '/楽天トラベルデータ'+checkindate
    os.makedirs(new_dir_path, exist_ok=True)
    os.chdir(new_dir_path)
    
    #1か月のループ
    for day in range(30):

        #地区コードのループ
        for a in df.itertuples():
            
            mid_url=a[1]
            payload['middleClassCode']=mid_url

            small_url=a[3]
            payload['smallClassCode']=small_url

            detail_url=a[5]
            payload['detailClassCode']=detail_url
            
            destination=[mid_url,small_url,detail_url]
            print(payload['middleClassCode'],payload['smallClassCode'],payload['detailClassCode'])

            res=requests.get(url,params=payload)
            Data=res.json()

            time.sleep(1)

            if 'pagingInfo' not in Data:
                continue

            else:
                print(Data['pagingInfo']['recordCount'])
                if Data['pagingInfo']['recordCount']<=3000:
                    gethoteldata()

                    if Data['pagingInfo']['pageCount']>1:
                        pager()

                else:
                    payload['maxCharge']=9500

                    res=requests.get(url,params=payload)
                    Data=res.json()
                    
                    if 'pagingInfo' not in Data:
                        time.sleep(1)
                        continue
                    else:
                        if Data['pagingInfo']['recordCount']<=3000:
                            gethoteldata()

                            if Data['pagingInfo']['pageCount']>1:
                                pager()

                        else:
                            try:
                                while Data['pagingInfo']['recordCount']>3000:
                                    if 'pagingInfo' not in Data:
                                        time.sleep(1)
                                        continue
                                    else:
                                        while Data['pagingInfo']['recordCount']>3000:
                                            time.sleep(1)
                                            payload['maxCharge']=payload['maxCharge']-1000

                                            res=requests.get(url,params=payload)
                                            Data=res.json()

                                        time.sleep(1)
                                        gethoteldata()

                                        if Data['pagingInfo']['pageCount']>1:
                                            pager()

                                    payload['minCharge']=payload['maxCharge']+1
                                    payload['maxCharge']=9500
                                    payload['page']=1

                                    res=requests.get(url,params=payload)
                                    Data=res.json()
                                
                            except:
                                pass

                            time.sleep(1)
                            gethoteldata()

                            if Data['pagingInfo']['pageCount']>1:
                                pager()

                    payload['minCharge']=9501
                    payload['maxCharge']=16000
                    payload['page']=1

                    res=requests.get(url,params=payload)
                    Data=res.json()
                    
                    if 'pagingInfo' not in Data:
                        time.sleep(1)
                        continue
                    else:

                        if Data['pagingInfo']['recordCount']<=3000:

                            time.sleep(1)
                            gethoteldata()

                            if Data['pagingInfo']['pageCount']>1:
                                pager()
                        else:
                            try:
                                while Data['pagingInfo']['recordCount']>3000:
                                    if 'pagingInfo' not in Data:
                                        time.sleep(1)
                                        continue
                                    else:
                                        while Data['pagingInfo']['recordCount']>3000:
                                            time.sleep(1)
                                            payload['maxCharge']=payload['maxCharge']-1000

                                            res=requests.get(url,params=payload)
                                            Data=res.json()

                                        time.sleep(1)
                                        gethoteldata()

                                        if Data['pagingInfo']['pageCount']>1:
                                            pager()

                                    payload['minCharge']=payload['maxCharge']+1
                                    payload['maxCharge']=16000
                                    payload['page']=1

                                    res=requests.get(url,params=payload)
                                    Data=res.json()
                                
                            except:
                                pass

                            time.sleep(1)
                            gethoteldata()

                            if Data['pagingInfo']['pageCount']>1:
                                pager()

                    payload['minCharge']=16001
                    payload['maxCharge']=400000
                    payload['page']=1

                    res=requests.get(url,params=payload)
                    Data=res.json()
                    
                    if 'pagingInfo' not in Data:
                        time.sleep(1)
                        continue
                    else:
                    
                        if Data['pagingInfo']['recordCount']<=3000:
                            time.sleep(1)
                            gethoteldata()
                            if Data['pagingInfo']['pageCount']>1:
                                pager()

                        else:
                            try:
                                while Data['pagingInfo']['recordCount']>3000:
                                    if 'pagingInfo' not in Data:
                                        time.sleep(1)
                                        continue
                                    else:
                                        while Data['pagingInfo']['recordCount']>3000:
                                            time.sleep(1)
                                            payload['maxCharge']=payload['maxCharge']-20000

                                            res=requests.get(url,params=payload)
                                            Data=res.json()

                                        time.sleep(1)
                                        gethoteldata()

                                        if Data['pagingInfo']['pageCount']>1:
                                            pager()

                                    payload['minCharge']=payload['maxCharge']+1
                                    payload['maxCharge']=999999999
                                    payload['page']=1

                                    res=requests.get(url,params=payload)
                                    Data=res.json()
                                
                            except:
                                pass

                            time.sleep(1)
                            gethoteldata()

                            if Data['pagingInfo']['pageCount']>1:
                                pager()
        
            payload['page']=1
            payload['maxCharge']=999999999
            payload['minCharge']=0
            
            print(len(Info))
            print(payload['checkinDate'])

        
        with open(checkoutdate+'rakutentravel.csv', 'w') as f:
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows(Info)
        
        Info.clear()

        payload['checkinDate']=checkoutdate
        checkout=checkout+ datetime.timedelta(days=1)
        checkoutdate=checkout.isoformat()
        payload['checkoutDate']=checkoutdate

        Info = [areacode]

#実行コマンド
Info=[]
areacode=['middleClassCode','smallClassCode','detailClassCode','hotelNo','lowestCharge','highestCharge','roomClass','roomName','planId','withDinnerFlag','dinnerSelectFlag','withBreakfastFlag','breakfastSelectFlag','payment','stayDate','total']
destination=[]
Info=[areacode]
GetData()
