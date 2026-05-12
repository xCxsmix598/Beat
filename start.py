import subprocess
import signal
import sys
import time

lavalink = subprocess.Popen(['java', '-jar', 'Lavalink.jar'], cwd='Lavalink/')
bot = subprocess.Popen(['python', 'main.py'])


def stopBot():
    lavalink.send_signal(signal.SIGINT)
    bot.send_signal(signal.SIGINT)
    print('Program Exited')
    sys.exit(0)


x = 1
while True:
    try:
        time.sleep(120)
        x += 1
    except KeyboardInterrupt:
        stopBot()
