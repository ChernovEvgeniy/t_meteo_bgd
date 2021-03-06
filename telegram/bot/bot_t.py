# -*- coding: utf-8 -*-
import telebot
import config
import request

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

def run_bot():
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

        #print(LMeteoLocation, LMeteoCommand)
        # Получение команды /start или /help
        '''Функция обработки команды /start или /help
            с выводом списка метеостанций одним сообщением'''
        @bot.message_handler(commands=['start', 'help'])
        def start(message):
            listMeteoPr = 'List meteostation in Belgorodskaya oblast \n'
            for i in range(0, len(LMeteoLocation)):
                listMeteoPr = listMeteoPr + '\n' + LMeteoLocation[i]
            bot.send_message(message.chat.id, listMeteoPr)

        '''Получение команды по одной из метеостанции
           и вывод реальных данных'''
        @bot.message_handler(commands=LMeteoCommand[:])
        def meteo(message):
            meteoState = request.DataPressure()
            #Вывод названия метеостанции с её месторасположением и прогноз
            for i in range(0, len(LMeteoCommand)):
                if message.text[1:] == LMeteoCommand[i]:
                    botMess = LMeteoLocation[i][1:] + '\n'
                    break
            # Формирование сообщения параметров метеостанции
            if len(message.text) > 7:
                masMeteo = meteoState[int(message.text[-2:])]
                print(masMeteo)
                print('-_- ---'*10)
                for i in range(0, len(paramMeteoLoc)):
                    if masMeteo[paramMeteoLocGet[i]] == 'null':
                        botMess = botMess + paramMeteoLoc[i] + 'Данные отсутствуют' + '\n'
                    else:
                        botMess = botMess + paramMeteoLoc[i] + str(masMeteo[paramMeteoLocGet[i]]) + paramMeteoLocDes[i] + '\n'
            else:
                masMeteo = meteoState[int(message.text[-1])]
                for i in range(0, len(paramMeteoLoc)):
                    if masMeteo[paramMeteoLocGet[i]] == 'null':
                        botMess = botMess + paramMeteoLoc[i] + 'Данные отсутствуют' + '\n'
                    else:
                        botMess = botMess + paramMeteoLoc[i] + str(masMeteo[paramMeteoLocGet[i]]) + paramMeteoLocDes[i] + '\n'
            bot.send_message(message.chat.id, botMess)
        bot.polling()

while True:
    try:
        listMeteoLocation(LMeteoLocation, LMeteoCommand)
        run_bot()
    except Exception:
        print('tak blet')
        continue
