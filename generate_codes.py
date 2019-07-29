import secrets
from telegram_bot.db import cursor, connection


def generate(n: int = 8, k: int = 1, filename: str = 'codes'):
    with open(filename, 'wb') as file:
        for _ in range(k):
            code = secrets.token_hex(n)
            file.write(("'" + code + "',\n").encode())
            cursor.execute(f"insert into invite_codes (code) values ('{code}')")
            print(f'{code} loaded in database')
            print(f'{k - _} codes left')
    connection.commit()
    print('OK')


generate(8, 2000)
