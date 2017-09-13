# -*- coding: utf-8 -*-
import telebot
import config
import request
from telebot import types

# Создаем объект бота
bot = telebot.TeleBot(config.token)
# Инициализируем пустые списки локаций и команд метеостанций
LMeteoLocation = []
LMeteoCommand = []


# Функция определяющяя списки локаций и команд метеостанций
def listMeteoLocation(LMeteoLocation, LMeteoCommand):
    meteoName = request.IdMeteoLst()
    for i in range(0, len(meteoName)):
        LMeteoLocation.append('/Meteo' + str(meteoName[i][0]) +
                              ' ' + str(meteoName[i][1]))
        LMeteoCommand.append('Meteo' + str(meteoName[i][0]))


# Описание возвращаемых параметров
paramMeteoLoc = ['-Состояние дорожного полотна: ', '-Влажность: ',
                 '-Атмосферное давление: ', '-Дата: ',
                 '-Предупреждения об опастности: ', '-Температура воздуха: ']
# Описание обозначений возвращаемых параметров
paramMeteoLocDes = ['', ' %', ' mm Hg', '', '', ' °C']
# Название параметров возвращаемыъх с сервиса
paramMeteoLocGet = ['surfacecondition', 'humidity', 'pressure', 'date',
                    'surfacewarning', 'airTemperature']
# Словарь соответствич прогноза
dictForeCast = {
     'clear-day': 'Ясно',
     'clear-night': 'Ясно',
     'rain': 'Ожидается дождь',
     'snow': 'Ожидается снег',
     'sleet': 'Ожидается дождь со снегом',
     'wind': 'Ожидается ветренная погода',
     'fog': 'Ожидается туман',
     'cloudy': 'Облачно',
     'partly-cloudy-day': 'Переменная облачность',
     'partly-cloudy-night': 'Переменная облачность',
     'hail': 'Ожидается град',
     'thunderstorm': 'Ожидается гроза',
     'tornado': 'ТОРНАДО!',
     'err': 'Ошибка! Прогноз временно отсутствует'
}
listMeteoLocation(LMeteoLocation, LMeteoCommand)

# Получение команды /start или /help


@bot.message_handler(commands=['start', 'help'])
def start(message):
    '''Функция обработки команды /start или /help 
       с выводом списка метеостанций одним сообщением'''
    listMeteoPr = 'List meteostation in Belgorodskaya oblast \n'
    if message.text == '/help':
        collect_inf = 'Данный бот позволяет получить информацию об актуальной \
                        метеорологической обстановке в различных районах Б. \
                        области. Ниже приведен список метеостанций, которе в \
                        в реальном времени позволяют получить информацию о \
                        температуре воздуха, атмосферного давления, влажности \
                        состоянии дорожного полотна и прогнозируемой погодной \
                        обстановке'
        bot.send_message(message.chat.id, collect_inf)
    for i in range(0, len(LMeteoLocation)):
        listMeteoPr = listMeteoPr + '\n' + LMeteoLocation[i]
    #Добавление кнопки для быстрого переходна на карту с расположением станций
    keyboard = types.InlineKeyboardMarkup()
    url_button = types.InlineKeyboardButton(text='Карта с расположением станций',
                                            url=config.url_button_as)
    keyboard.add(url_button)
    bot.send_message(message.chat.id, listMeteoPr, reply_markup=keyboard)





@bot.message_handler(commands=LMeteoCommand[:])
def meteo(message):
    '''Получение команды по одной из метеостанции
        и вывод реальных данных'''
    meteoState = request.DataPressure()
    #Вывод названия метеостанции с её месторасположением и прогноз
    for i in range(0, len(LMeteoCommand)):
        if message.text[1:] == LMeteoCommand[i]:
            botMess = LMeteoLocation[i][1:] + '\n'
            break
    # Формирование сообщения параметров метеостанции
    if len(message.text) > 7:
        masMeteo = meteoState[int(message.text[-2:])]
        for i in range(0, len(paramMeteoLoc)):
            if masMeteo[paramMeteoLocGet[i]] == 'null':
                botMess = botMess + paramMeteoLoc[i] + 'Данные отсутствуют'+'\n'
            else:
                botMess = botMess + paramMeteoLoc[i] + masMeteo[paramMeteoLocGet[i]] + paramMeteoLocDes[i] + '\n'
        botMess = botMess + '-Прогноз: ' + dictForeCast[masMeteo['symbol']]
        bot.send_message(message.chat.id, botMess)
    else:
        masMeteo = meteoState[int(message.text[-1])]
        for i in range(0, len(paramMeteoLoc)):
            if masMeteo[paramMeteoLocGet[i]] == 'null':
                botMess = botMess + paramMeteoLoc[i] + 'Данные отсутствуют'+'\n'
            else:
                botMess = botMess + paramMeteoLoc[i] + masMeteo[paramMeteoLocGet[i]] + paramMeteoLocDes[i] + '\n'
        botMess = botMess + '-Прогноз: ' + dictForeCast[masMeteo['symbol']]
        bot.send_message(message.chat.id, botMess)




bot.polling()
