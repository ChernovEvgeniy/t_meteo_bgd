# -*- coding: utf-8 -*-
import requests
import time
import config


# Функиця определения является ли строка числом
def is_num(sMeteoVal):
    try:
        float(sMeteoVal)
        return True
    except ValueError:
        return False


#Функция выполнения запроса к сервису и обработка ошибок
def request_as(adrr):
    try:
        reqGet = requests.get(adrr, timeout=15)
        reqGet.raise_for_status()
    except requests.exceptions.ConnectTimeout:
        reqGet = ''
        print('Error! Connect timeout ocurred!')
    except requests.exceptions.RealTimeout:
        reqGet = ''
        print('Error! Read timeout ocurred!')
    except requests.exceptions.ConnectionError:
        reqGet = ''
        print('Seems like dns lookup failed.')
    except requests.exceptions.HTTPError as err:
        reqGet = ''
        print('Error! HTTP Errors occured!')
        print('Response is: {connect}'.format(content=err.response.content))
    finally:
        return reqGet


# Запрос списка метеостанций и вывод в строчном значении
def IdMeteoLst():
    reqGet = request_as(config.adrrMapIndex)
    reqMeteo = reqGet.text
    spReqMet = reqMeteo.split(',')
    spListID = []
    spListNM = []
    spListFC = [] #Символ прогноза/облачности
    spListXY = []
    sBufListX = []
    sBufListY = []
    # Создаем список id метеостанций и названий и координат
    for i in range(len(spReqMet)):
        sPointID = spReqMet[i].find('id')
        sPointNM = spReqMet[i].find('name')
        sPointFC = spReqMet[i].find('symbol')
        sPointX = spReqMet[i].find('"x"')
        sPointY = spReqMet[i].find('"y"')
        if sPointX != -1:
            sBufListX.append(float(spReqMet[i][spReqMet[i].rfind(':') + 1:]))
        if sPointY != -1:
            sBufListY.append(float(spReqMet[i][spReqMet[i].rfind(':') + 1:]))
        if sPointID != -1:
            spListID.append(int(spReqMet[i][spReqMet[i].rfind(':') + 1:]))
        if sPointNM != -1:
            spListNM.append(spReqMet[i][spReqMet[i].rfind(':') + 2:-1])
        if sPointFC != -1:
            if spReqMet[i][-1] == ']' and spReqMet[i][-2] == '}':
                spListFC.append(spReqMet[i][spReqMet[i].rfind(':') + 2:-3])
            elif spReqMet[i][-1] == '}' or ']':
                spListFC.append(spReqMet[i][spReqMet[i].rfind(':') + 2:-2])
            else:
                spListFC.append(spReqMet[i][spReqMet[i].rfind(':') + 2:-1])
    spListXY = (list(zip(sBufListX, sBufListY)))
    return list(zip(spListID, spListNM, spListFC, spListXY))


def DictDataMeteo():
    # Создаем список словарей данных с каждой метеостанции
    lstIdNameFC = IdMeteoLst()
    lDictMeteo = []
    nMeteo = []
    dictMeteo = {}
    for j in range(len(lstIdNameFC)):
        nMeteo.append(lstIdNameFC[j][0])
        reqGet = request_as(config.adrrMapLast + str(nMeteo[j]))
        if reqGet == '':
            continue
        splMeteo = reqGet.text.split(',')
        x, y = splMeteo[0].split('":')
        dictMeteo = {}
        dictMeteo[x[2:]] = y[:-1]
        for i in range(1, len(splMeteo)):
            x, y = splMeteo[i].split('":')
            if is_num(y) or y == 'null':
                dictMeteo[x[1:]] = y
            else:
                if i == len(splMeteo):
                    dictMeteo[x[1:]] = y[1:-2]
                else:
                    dictMeteo[x[1:]] = y[1:-1]
        dictMeteo['symbol'] = lstIdNameFC[j][2]
        lDictMeteo.append(dictMeteo)
    return dict(zip(nMeteo, lDictMeteo))


def DataPressure():
    '''Преобразование даты в читаемый формат с
       коррекцией и атмосферного давления в мм.рт.ст'''
    lisDictMeteo = DictDataMeteo()
    for i in list(lisDictMeteo.keys()):
        bufd, buft = lisDictMeteo[i]['date'].split('T')
        y, m, d = bufd.split('-')
        bufd = d + '-' + m + '-' + y
        h, m, s = buft.split(':')
        h = int(h)
        h += 3
        buft = str(h) + ':' + m + ':' + s
        lisDictMeteo[i]['date'] = bufd + ' ' + buft[:-5]
        try:
            bufPress = lisDictMeteo[i]['pressure']
            bufPress = float(bufPress)
            bufPress *= 0.750063
            lisDictMeteo[i]['pressure'] = str(round(bufPress, 1))
        except:
            continue
    return lisDictMeteo
