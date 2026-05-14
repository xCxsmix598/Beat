import subprocess
import time
import signal
import sys

lavalink = subprocess.Popen(['java', '-jar', 'Lavalink.jar'], cwd='Lavalink/')
bot = subprocess.Popen(['python', 'main.py'])

x = 0

while True:
    try:
        time.sleep(120)
        x += 1
    except KeyboardInterrupt:
        lavalink.send_signal(signal.SIGINT)
        bot.send_signal(signal.SIGINT)
        sys.exit(0)
