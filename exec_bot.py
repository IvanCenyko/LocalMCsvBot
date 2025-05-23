import requests, telebot, time, datetime, threading, queue, os
from mcrcon import MCRcon as rcon
import public_ip as ip
from dotenv import load_dotenv
import os #provides ways to access the Operating System and allows us to read the environment variables

load_dotenv(".env")

key = os.getenv("TELEGRAM_KEY")

admins_list = []
admin_users = []
start_log = []
start_time_log = []
bot = telebot.TeleBot(key)

q = queue.Queue()

def server_status(status):
    q.queue.clear()
    q.put(status)

def is_started():
    return q.queue[0]

server_status(False)


def bot_exec():
    global is_started
    q.put(is_started)
    @bot.message_handler(commands=['start'])
    def server_starter(message):
        bot.reply_to(message, "Hola! Soy el bot del server de MC de Iván. Usá /help para los comandos")

    @bot.message_handler(commands=['ivan1234'])
    def server_admins(message):
        if not message.chat.id in admins_list:
            admins_list.append(message.chat.id)
            admin_users.append(str(message.from_user.first_name))
            bot.reply_to(message, "Ahora sos admin y podés ejecutar comandos especiales! Usá /helpadmin")
        else:
            bot.reply_to(message, "Ya sos admin! Podés usar /helpadmin")

    @bot.message_handler(commands=['help'])
    def commands_help(message):
        bot.reply_to(message, 
    """
Comandos:
- /svstart: Iniciar server.
- /list: Lista de jugadores.
- /adminlist: Lista de admins.
- /ip: IP del server.
""")
        
    @bot.message_handler(commands=['adminlist'])
    def admin_list(message):
        if admin_users:
            users = ", ".join(admin_users)
            bot.reply_to(message, f"Los admins son: {users}")
        else:
            bot.reply_to(message, "No hay admins!")

    @bot.message_handler(commands=['ip'])
    def server_ip(message):
        if is_started():
            bot.reply_to(message,
    f"""
IP: solarlink.ivi.pl // {ip.get()}
""")
        else:
            bot.reply_to(message,
    f"""
IP: solarlink.ivi.pl // {ip.get()}
Ojo que el sv está cerrado!
""")  


    @bot.message_handler(commands=['svstart'])
    def server_starter(message):
        if not is_started():
            start_log.append(str(message.from_user.first_name))
            start_time_log.append(f"{datetime.datetime.now().hour:02}:{datetime.datetime.now().minute:02}, {datetime.datetime.now().day}/{datetime.datetime.now().month}")
            os.chdir(r"C:\Users\helii\Documents\Minecraft\server 1.19.3")
            os.startfile(r"exec.bat")
            bot.reply_to(message,
    f"""
Server abriendo...
Esperá a que yo te avise que abrió para tirarme otro comando del server!
IP: solarlink.ivi.pl // {ip.get()}
    """)
            resp = 0
            while not resp == "Unknown or incomplete command, see below for errorhola<--[HERE]":
                try:
                    with rcon('192.168.1.64', 'ivancapo') as mcr:
                        resp = str(mcr.command('/hola'))
                except:
                    pass
            bot.reply_to(message, "El server abrió!")
            server_status(True)
            requests.get("https://freedns.afraid.org/dynamic/update.php?REc0dERLRzVaaG0zZjRMYml6NERzdHVsOjIxMzYwNDA3")
        else:
            bot.reply_to(message, "El server ya está abierto!")


    @bot.message_handler(commands=['list'])
    def server_list(message):
        if is_started():
            with rcon('192.168.1.64', 'ivancapo') as mcr:
                resp = str(mcr.command('/list'))
                bot.reply_to(message, resp)
        else:
            bot.reply_to(message, "El server está cerrado!")

    @bot.message_handler(commands=['helpadmin'])
    def commands_help_admin(message):
        if message.chat.id in admins_list:
            bot.reply_to(message, 
"""
Comandos de admin:
- /svstop: Cerrar server.
- /publicip: IP pública de la PC host.
- /log: Historial de starts del sv.
- Si escribís cualquier palabra con el sv abierto, se ejecuta como comando de MC!
""")
        else:
            bot.reply_to(message, "No sos admin, no tenés permiso para eso!")

    @bot.message_handler(commands=['log'])
    def log(message):
        if start_log and message.chat.id in admins_list:
            final_string = ""
            for i in range(len(start_log)):
                final_string += start_log[i] + " "
                final_string += start_time_log[i] + "\n"
            bot.reply_to(message, final_string)
        elif not start_log and message.chat.id in admins_list:
            bot.reply_to(message, "No hay historial de starts.")
        else:
            bot.reply_to(message, "No sos admin, no tenés permiso para eso!")

    @bot.message_handler(commands=['svstop'])
    def server_stop(message):
        if message.chat.id in admins_list and is_started():
            with rcon('192.168.1.64', 'ivancapo') as mcr:
                resp = str(mcr.command('/stop'))
                bot.reply_to(message, "Servidor cerrado.")
            server_status(False)
        elif message.chat.id not in admins_list and not is_started():
            bot.reply_to(message, "No sos admin, no tenés permiso para eso! Igual ya está cerrado...")
        elif message.chat.id not in admins_list and is_started():
            bot.reply_to(message, "No sos admin, no tenés permiso para eso!")
        else:
            bot.reply_to(message, "El servidor ya está cerrado!")

    @bot.message_handler(commands=['publicip'])
    def server_public_ip(message):
        if message.chat.id in admins_list:
            bot.reply_to(message, ip.get())
            requests.get("https://freedns.afraid.org/dynamic/update.php?REc0dERLRzVaaG0zZjRMYml6NERzdHVsOjIxMzYwNDA3")
        else:
            bot.reply_to(message, "No sos admin, no tenés permiso para eso!")

    @bot.message_handler(func=lambda message: True)
    def admin_full_commands(message):
        if message.chat.id in admins_list and message.text[0] == "/":
            bot.reply_to(message, "No te entendí, usá comandos que conozca! (/help o /helpadmin)")
        elif message.chat.id in admins_list and not is_started() and not message.text[0] == "/":
            bot.reply_to(message, "El server está cerrado!")
        elif message.chat.id in admins_list and is_started():
            with rcon('192.168.1.64', 'ivancapo') as mcr:
                resp = str(mcr.command(f'/{message.text}'))
                bot.reply_to(message, resp)
                if message.text == "stop":
                    server_status(False)
        else:
            bot.reply_to(message, "No te entendí, usá comandos que conozca! (/help)")

    bot.infinity_polling()

def server_conf():
    counter = 0
    while 1:
        time_ref = time.time()
        while is_started():
            time_check = time.time()
            if (time_check - time_ref) / 60 >= 5:
                with rcon('192.168.1.64', 'ivancapo') as mcr:
                    resp = mcr.command('/list')
                if resp == "There are 0 of a max of 20 players online: ":
                    counter += 1
                else:
                    counter = 0
                time_ref = time.time()
            if counter >= 3:
                with rcon('192.168.1.64', 'ivancapo') as mcr:
                    resp = str(mcr.command('/stop'))
                    server_status(False)
                    counter = 0
                break
            
if __name__ =="__main__":
    t1 = threading.Thread(target=bot_exec)
    t2 = threading.Thread(target=server_conf)
    t1.start()
    t2.start()
