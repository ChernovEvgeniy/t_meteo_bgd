# -*- coding: utf-8 -*-
import requests
from datetime import datetime
import time
import config
import json

#Класс метеостанции
class Meteostations:
    def __init__(self, iden, name, position):
        self.iden = iden
        self.name = name
        self.position = position


#Функция выполнения запроса к сайту агрегатору
def request_meteo(req_url):
    try:
        reqGet = requests.get(req_url, timeout = 15)
        reqGet.raise_for_status()
    except requests.exceptions.ConnectTimeout:
        print('Error! Connect timeout ocurred!')
    except requests.exceptions.RealTimeout:
        print('Error! Read timeout ocurred!')
    except requests.exceptions.ConnectionError:
        print('Seems like dns lookup failed.')
    except requests.exceptions.HTTPError as err:
        print('Error! HTTP Errors occured!')
        print('Response is: {connect}'.format(content=err.response.content))
    return reqGet

#Функиця определения является ли строка числом
def is_num(str):
    try:
        float(str)
        return True
    except ValueError:
        return False


#Запрос списка метеостанций и вывод в строчном значении
def IdMeteoLst():
    reqGet = request_meteo(config.adrrMapIndex)
    s_json = json.loads(reqGet.text)
    spListID = []
    spListNM = []
    spListFC = []
    for i in range(len(s_json)):
        spListID.append(s_json[i]['id'])
        spListNM.append(s_json[i]['name'])
        spListFC.append(s_json[i]['symbol'])
    return list(zip(spListID, spListNM, spListFC))

def DictDataMeteo():
    #Создаем список словарей данных с каждой метеостанции
    lstIdNameFC = IdMeteoLst()
    lDictMeteo = []
    nMeteo = []
    dictMeteo = {}
    for j in range(len(lstIdNameFC)):
        nMeteo.append(lstIdNameFC[j][0])
        map_index = config.adrrMapLast + str(nMeteo[j])
        reqGet = request_meteo(map_index)
        if reqGet == None:
            continue
        s_json = json.loads(reqGet.text)
        s_json['date'] = str(datetime.strptime(s_json['date'].split('.')[0], '%Y-%m-%dT%H:%M:%S'))
        lDictMeteo.append(s_json)
    return dict(zip(nMeteo, lDictMeteo))


def DataPressure():
    #Преобразование даты в читаемый формат с коррекцией и атмосферного давления в мм.рт.ст
    lisDictMeteo = DictDataMeteo()
    for i in list(lisDictMeteo.keys()):
        bufd, buft = lisDictMeteo[i]['date'].split()
        y, m, d = bufd.split('-')
        bufd = d + '-' + m + '-' + y
        h, m, s = buft.split(':')
        h = int(h)
        h += 3
        buft = str(h) + ':' + m + ':' + s
        lisDictMeteo[i]['date'] = bufd + ' ' + buft
        try:
            bufPress = lisDictMeteo[i]['pressure']
            bufPress = float(bufPress)
            bufPress *= 0.750063
            lisDictMeteo[i]['pressure'] = str(round(bufPress, 1))       
        except:
            continue
    # print(lisDictMeteo)
    return lisDictMeteo


lisDictMeteo = DataPressure()
tick = time.strftime("%Y-%m-%d/%H:%M:%S", time.localtime(time.time()))
# print(tick)

# for i in list(lisDictMeteo.keys()):
#     print(lisDictMeteo[i])
#     print('\n')

def baseCycle():
    b_time = time.time()
    e_time = time.time()
    while True:
        tick = time.strftime("%Y-%m-%d/%H:%M:%S", time.localtime(time.time()))
        e_time = time.time()
        if (e_time - b_time)//2 == 10:
            print(tick)
            b_time = e_time
            lisDictMeteo = DataPressure()
            break
    return lisDictMeteo



