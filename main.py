import requests, pickle, schedule, time
from datetime import datetime

file_conf_path = '/home/pi/jupyterLab/TermoBot/****.tt'
oldMsg = ''

def get_msg():
    while True:
        try:
            reponse = requests.get('https://api.telegram.org/bot*****/getUpdates', timeout=20)
            data = reponse.json()
            return data
        except:
            print("No se puede obtener mensajes")
    
def parce_msg(__msg__):
    username = __msg__['from']['username']
    chatID = __msg__['from']['id']
    date = __msg__['date']
    text = __msg__['text']
    
    msg_parce = {
        "username": username,
        "chatID": chatID,
        "date": date,
        "text": text
    }
    
    return msg_parce

def send_msg(chat_id,bot_message):
    send_text = f'https://api.telegram.org/bot****/sendMessage?chat_id={chat_id}&parse_mode=Markdown&text={bot_message}'
    print(f'Mensaje enviado a {chat_id}: {bot_message}')
    try:
        response = requests.post(send_text)
    except:
        print('Fallo el envio del mensaje')
        return 'Fallo el envio del mensaje'
    return response.json()
    
class termotanque:
    def __init__(self, IP):
        self.IP = IP
    
    def prender(self):
        try:
            r = requests.get(f'http://{self.IP}/TERMO=ON')
            return "Termotanque prendido"
        except:
            return 'Fallo prender el termo'
        
    def apagar(self):
        try:
            r = requests.get(f'http://{self.IP}/TERMO=OFF')
            return "Termotanque apagado"
        except:
            return 'Fallo apagar el termo'
    def get_status(self):
        try:
            x = requests.get(f'http://{self.IP}/')
            if "Termo esta: Prendido" in x.text:
                return "Termo prendido"
            if "Termo esta: Apagado" in x.text:
                return "Termo apagado"
        except:
            return 'Fallo comunicacion con el termo'

def load_file_conf():
    try:
        file_store = open(file_conf_path, "rb") 
        restore_data = pickle.load(file_store)
        file_store.close

        return restore_data
    except:
        print('Fallo cargar los datos')
        return 'Fallo cargar los datos'
    
def save_file_conf(mensaje, date, horaPrende, horaApaga):
    data_store = {'mensaje_file' : mensaje,'date_file' : date, 'hora_prende_file' : horaPrende, 'hora_apaga_file': horaApaga}
    file_store = open(file_conf_path, "wb") 
    pickle.dump(data_store, file_store)
    file_store.close
    return "Datos guardados"
    
def getType_msg(__msg__):
    if "/ON" in __msg__:
        return "prender"
    if "/OFF" in __msg__:
        return "apagar"
    if "/status" in __msg__:
        return "status"
    if "/start" in __msg__:
        return "start"
    if "/setHoraON" in __msg__:
        hora = datetime.strptime(__msg__[11:15], '%H%M')
        return "setON", hora
    if "/setHoraOFF" in __msg__:
        hora = datetime.strptime(__msg__[12:16], '%H%M')
        return "setOFF", hora
    
def tutorial():
    msg = """
Hola wachin, en que te puedo ayudar?
Te voy a pasar una lista de comandos que podes usar.
/ON Prende el termotanque
/OFF Apaga el termotanque
/status Te digo como esta el termotanque
/setHoraON *hora* pasame una hora para prender el termo (en formato 24hs sin :, ej /setHoraON 1506)
/setHoraOFF *hora* pasame una hora para apagar el termo (en formato 24hs sin :, ej /setHoraOFF 2236)

La hora que se apaga y la que se prende tienen un intervalo de 10min donde los comandos /ON y /OFF no funcionan
    """
    return msg

    

file_config = load_file_conf()       

 
                                                                                  
Termo = termotanque('*****')     


schedule.every(1).day.at(str(file_config['hora_prende_file'].strftime('%H:%M'))).do(Termo.prender).tag('daily-tasks', 'prende-termo')
schedule.every(1).day.at(str(file_config['hora_apaga_file'].strftime('%H:%M'))).do(Termo.apagar).tag('daily-tasks', 'apagar-termo')


while True:
    newMsg = get_msg()
    time.sleep(1)
    if(newMsg != oldMsg and newMsg != None):
        oldMsg = newMsg
        msg_handler = parce_msg(newMsg['result'][len(newMsg['result']) - 1]['message'])  
        print(msg_handler)
        print(file_config)
        
        if msg_handler['text'] == file_config['mensaje_file'] and  msg_handler['date'] == file_config['date_file']:
            continue
        msg_type = getType_msg(msg_handler['text'])
        
        if msg_type == "start":
            send_msg(msg_handler['chatID'], tutorial())
        if msg_type == "prender":
            send_msg(msg_handler['chatID'], Termo.prender())
        if msg_type == "apagar":
            send_msg(msg_handler['chatID'], Termo.apagar())
        if msg_type == "status":
            responseMsg = f"""
{Termo.get_status()}
Se prende a las {str(file_config['hora_prende_file'].strftime("%H:%M"))}
Se apaga a las {str(file_config['hora_apaga_file'].strftime("%H:%M"))}
"""
            
            send_msg(msg_handler['chatID'], responseMsg)
        if "setON" in msg_type:
            file_config['hora_prende_file'] = msg_type[1]
            send_msg(msg_handler['chatID'], f"Prendo el termo a las {str(msg_type[1].strftime('%H:%M'))}")
            
            schedule.clear('prende-termo')
            schedule.every(1).day.at(str(file_config['hora_prende_file'].strftime('%H:%M'))).do(Termo.prender).tag('daily-tasks', 'prende-termo')
                                                                                              
        if "setOFF" in msg_type:
            file_config['hora_apaga_file'] = msg_type[1]
            send_msg(msg_handler['chatID'], f"Apago el termo a las {str(msg_type[1].strftime('%H:%M'))}")
            
            schedule.clear('apagar-termo')
            schedule.every(1).day.at(str(file_config['hora_apaga_file'].strftime('%H:%M'))).do(Termo.apagar).tag('daily-tasks', 'apagar-termo')
            
        save_file_conf(msg_handler['text'], msg_handler['date'], file_config['hora_prende_file'], file_config['hora_apaga_file'])
        
    schedule.run_pending()
    
    
