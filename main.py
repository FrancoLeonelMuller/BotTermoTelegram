import requests, time, pytz, os, ast, json
import pickle
from pytz import timezone
from datetime import datetime, timedelta
from os import listdir
from os.path import isfile, join

time.sleep(60)

bot_token = '***************************'
time_cycle_ms = 5
oldMsg = ''
IP_NodeM = ''
status_read = True
hora_prende_termo = ''
hora_apaga_termo = ''


def bot_send_text(chat_id, token,bot_message):
    send_text = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=Markdown&text=' + bot_message
    response = requests.post(send_text)
    return response.json()

def bot_get_mens(token):
    try:
        reponse = requests.get(f'https://api.telegram.org/bot{token}/getUpdates')
        data = reponse.json()
    except:
        print("No se pudo conectar con el servidor")
        return 'Reintentar'
    
    try:
        mensaje = data['result'][len(data['result'])-1]['message']['text']
        horaTimeS = data['result'][len(data['result'])-1]['message']['date']
        horaUTC = str(datetime.fromtimestamp(horaTimeS, pytz.timezone('America/Buenos_Aires')))
        #user = data['result'][len(data['result'])-1]['message']['chat']['username']
        chatID = data['result'][len(data['result'])-1]['message']['chat']['id']
        mesg = {"user": chatID,"hora": horaUTC,"msg": mensaje}
        return mesg
    except IndexError:
        print("No hay mensajes nuevos")
        return None
    except:
        print("Error general")
        return None
    
    
def prender_termo(IP_NodeM):
    r = requests.get(f'http://{IP_NodeM}/TERMO=ON')
    msg = "Termotanque prendido"
    return msg

def apagar_termo(IP_NodeM):
    r = requests.get(f'http://{IP_NodeM}/TERMO=OFF')
    msg = "Termotanque apagado"
    return msg

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

def status_termo(IP_NodeM, horaInicio, horaApago):
    msg = ''
    x = requests.get(f'http://{IP_NodeM}/')
    if "Termo esta: Prendido" in x.text:
        msg = f"""
El termo esta prendido
Se prende a las {str(horaInicio.strftime("%H:%M"))}
Se apaga a las {str(horaApago.strftime("%H:%M"))}
"""
    if "Termo esta: Apagado" in x.text:
        msg = f"""
El termo esta apagado
Se prende a las {str(horaInicio.strftime("%H:%M"))}
Se apaga a las {str(horaApago.strftime("%H:%M"))}
"""
    return msg

    

def save_file_conf(mensaje, horaPrende, horaApaga, force_on):
    data_store = {'mensaje_file' : mensaje, 'hora_prende_file' : horaPrende, 'hora_apaga_file': horaApaga, 'force_on_file': force_on}
    file_store = open("/home/pi/jupyterLab/TermoBot/BotTermoConf.tt", "wb") 
    pickle.dump(data_store, file_store)
    file_store.close
    
    return 'Datos guardados'
    
def load_file_conf():
    file_store = open("/home/pi/jupyterLab/TermoBot/BotTermoConf.tt", "rb") 
    restore_data = pickle.load(file_store)
    file_store.close
    
    return restore_data

def in_between(now, start, end):
    if start <= end:
        return start <= now < end
    else: # over midnight e.g., 23:30-04:15
        return start <= now or now < end




dataRestore = load_file_conf()
oldMsg = dataRestore['mensaje_file']
hora_prende_termo = dataRestore['hora_prende_file']
hora_apaga_termo = dataRestore['hora_apaga_file']
forzar_on = dataRestore['force_on_file']


time_now = datetime.now(timezone('America/Argentina/Buenos_Aires'))


status_readmsg = status_termo(IP_NodeM, hora_prende_termo, hora_apaga_termo)

if 'El termo esta prendido' in status_readmsg:
    status_read = True
if 'El termo esta apagado' in status_readmsg:
    status_read = False


    
while True:
    time.sleep(time_cycle_ms)
    newMsg = bot_get_mens(bot_token)
    if 'Reintentar' in newMsg:
        print(time_now, 'Error al obtener mensajes nuevos')
        continue
    
    time_now = datetime.now(timezone('America/Argentina/Buenos_Aires'))    
    
    if(newMsg != oldMsg and newMsg != None):
        oldMsg = newMsg
        print(time_now, 'Msg:', oldMsg)
        
        chatID = str(newMsg["user"])
        
        if(oldMsg["msg"].find('/start') != -1):
            bot_send_text(chatID, bot_token, tutorial()) 
        if(oldMsg["msg"].find('/status') != -1):
            bot_send_text(chatID, bot_token, status_termo(IP_NodeM, hora_prende_termo, hora_apaga_termo))
            
        if(oldMsg["msg"].find('/ON') != -1):
            bot_send_text(chatID, bot_token, prender_termo(IP_NodeM))
            prender_termo(IP_NodeM)
            print(time_now, 'El termotanque esta prendido')
            
        if(oldMsg["msg"].find('/OFF') != -1):
            bot_send_text(chatID, bot_token, apagar_termo(IP_NodeM)) 
            print(time_now, 'El termotanque esta prendido')
            
        if(oldMsg["msg"].find('/setHoraON') != -1):
            hora_prende_termo = datetime.strptime(f'{oldMsg["msg"][11:100][0:2]}:{oldMsg["msg"][11:100][2:4]}', '%H:%M')
            msg_return = f'Joya, prendo el termo a las {hora_prende_termo.strftime("%H:%M")}'
            bot_send_text(chatID, bot_token, msg_return)
        if(oldMsg["msg"].find('/setHoraOFF') != -1):
            hora_apaga_termo = datetime.strptime(f'{oldMsg["msg"][12:100][0:2]}:{oldMsg["msg"][12:100][2:4]}', '%H:%M')
            msg_return = f'Joya, apago el termo a las {hora_apaga_termo.strftime("%H:%M")}'
            bot_send_text(chatID, bot_token, msg_return)
    
    save_file_conf(oldMsg,hora_prende_termo,hora_apaga_termo, forzar_on)  

    #armar rutina de hora


    status_readmsg = status_termo(IP_NodeM, hora_prende_termo, hora_apaga_termo)
        
    if 'El termo esta prendido' in status_readmsg:
        status_read = True
    if 'El termo esta apagado' in status_readmsg:
        status_read = False
        
   
    desfasaje_prende = hora_prende_termo + timedelta(minutes=10)
    desfasaje_apaga = hora_apaga_termo + timedelta(minutes=10)
 

    en_tiempo_prende = in_between(time_now.time(), hora_prende_termo.time(), desfasaje_prende.time())
    en_tiempo_apaga = in_between(time_now.time(), hora_apaga_termo.time(), desfasaje_apaga.time())
    
    
    if en_tiempo_prende and status_read == False:
        print(time_now, 'El termotanque se prendio')
        prender_termo(IP_NodeM)
    if en_tiempo_apaga and status_read == True:
        print(time_now, 'El termotanque se apago')
        apagar_termo(IP_NodeM)
        
