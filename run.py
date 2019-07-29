import subprocess
import threading


def bot_process():
    return subprocess.Popen(['python', 'telegram_bot/bot.py'], stdout=subprocess.PIPE).wait()


def web_api_process():
    return subprocess.Popen(['python', 'web_api/main.py'], stdout=subprocess.PIPE).wait()


if __name__ == '__main__':
    p_1 = threading.Thread(target=bot_process).start()
    p_2 = threading.Thread(target=web_api_process).start()
    while True:
        if p_1 or p_2:
            continue
        break
