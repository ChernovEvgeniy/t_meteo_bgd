# -*- coding: utf-8 -*-
import requests
import time
import threading
import config

#Функиця определения является ли строка числом
def is_num(sMeteoVal):
	try:
		float(sMeteoVal)
		return True
	except ValueError:
		return False

#Запрос списка метеостанций и вывод в строчном значении
def IdMeteoLst():
	try:
		reqGet = requests.get(config.adrrMapIndex, timeout = 15)
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
	reqMeteo = reqGet.text
	spReqMet = reqMeteo.split(',')
	spListID = []
	spListNM = []
	spListFC = []
	#Создаем список id метеостанций и названий
	for i in range(len(spReqMet)):
		sPointID = spReqMet[i].find('id')
		sPointNM = spReqMet[i].find('name')
		sPointFC = spReqMet[i].find('symbol')
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
	return list(zip(spListID, spListNM, spListFC))

def DictDataMeteo():
	#Создаем список словарей данных с каждой метеостанции
	lstIdNameFC = IdMeteoLst()
	lDictMeteo = []
	nMeteo = []
	dictMeteo = {}
	for j in range(len(lstIdNameFC)):
		nMeteo.append(lstIdNameFC[j][0])
		try:
			reqGet = requests.get(config.adrrMapLast + str(nMeteo[j]), timeout = 15)
			reqGet.raise_for_status()
		except requests.exceptions.ConnectTimeout:
			print('Error! Connect timeout ocurred!')
			continue
		except requests.exceptions.RealTimeout:
			print('Error! Read timeout ocurred!')
			continue
		except requests.exceptions.ConnectionError:
			print('Seems like dns lookup failed.')
			continue
		except requests.exceptions.HTTPError as err:
			print('Error! HTTP Errors occured!')
			print('Response is: {connect}'.format(content=err.response.content))
			continue
		splMeteo = reqGet.text.split(',')
		x, y = splMeteo[0].split('":"')
		dictMeteo = {}
		dictMeteo[x[2:]] = y[:-1]
		for i in range(1, len(splMeteo)):
			x, y = splMeteo[i].split(':')
			if is_num(y) or y == 'null':
				dictMeteo[x[1:-1]] = y
			else:
				if i == len(splMeteo):
					dictMeteo[x[1:-1]] = y[1:-2]
				else:
					dictMeteo[x[1:-1]] = y[1:-1]
		dictMeteo['symbol'] = lstIdNameFC[j][2]
		lDictMeteo.append(dictMeteo)
	return dict(zip(nMeteo, lDictMeteo))
	# print(lisDictMeteo)

def DataPressure():
	#Преобразование даты в читаемый формат с коррекцией и атмосферного давления в мм.рт.ст
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


# lstIdNameFC = IdMeteoLst()
# print(lstIdNameFC)
lisDictMeteo = DataPressure()
tick = time.strftime("%Y-%m-%d/%H:%M:%S", time.localtime(time.time()))
print(tick)

for i in list(lisDictMeteo.keys()):
	print(lisDictMeteo[i])
	print('\n')

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

