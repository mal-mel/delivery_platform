import telebot
from collections import defaultdict
from datetime import datetime

from config import *
from db import cursor, connection


bot = telebot.TeleBot(TOKEN)

RENAME_START, RENAME_S1, RENAME_CLOSE = range(3)
ACTIVATE_START, ACTIVATE_FINAL, ACTIVATE_CLOSE = range(3)
CREATE_SHOP_START, CREATE_SHOP_S1, CREATE_SHOP_FINAL, CREATE_SHOP_CLOSE = range(4)
CHANGE_DISH_START, CHANGE_DISH_STATE_S1, CHANGE_DISH_STATE_S2, CHANGE_DISH_STATE_S3, CHANGE_DISH_CLOSE = range(5)
ADD_DISH_START, ADD_DISH_NAME, ADD_DISH_DESCRIPTION, ADD_DISH_PHOTO, ADD_DISH_COST, ADD_DISH_CLOSE = range(6)
DELETE_DISH_START, DELETE_DISH_S1, DELETE_DISH_CLOSE = range(3)
ORDER_DATA_START, ORDER_DATA_S1, ORDER_DATA_CLOSE = range(3)

ACTIVATE_STATE = defaultdict(lambda: ACTIVATE_START)
RENAME_STATE = defaultdict(lambda: RENAME_START)
CREATE_SHOP_STATE = defaultdict(lambda: CREATE_SHOP_START)
ADD_DISH_STATE = defaultdict(lambda: ADD_DISH_START)
CHANGE_DISH_STATE = defaultdict(lambda: CHANGE_DISH_START)
DELETE_DISH_STATE = defaultdict(lambda: DELETE_DISH_START)
COMPLETE_ORDER_DATA_STATE = defaultdict(lambda: ORDER_DATA_START)

SHOP_DATA = {}
SHOP_MENU_DATA = {}
USER_BASKET_DATA = {}


def get_state(state_type, message):
    return state_type[message.chat.id]


def update_state(state_type, message, state):
    state_type[message.chat.id] = state


def create_keyboard_shops():
    shops = cursor.execute('select id, name from shops')
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=3)
    buttons = [telebot.types.InlineKeyboardButton(text=str(shop[1]), callback_data=str(shop[0]))
               for shop in shops]
    keyboard.add(*buttons)
    return keyboard


def create_panel_keyboard():
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    menu_button = telebot.types.InlineKeyboardButton(text='Упаравление меню', callback_data='menu_set')
    rename_button = telebot.types.InlineKeyboardButton(text='Изменить название ресторана', callback_data='rename_shop')
    link_to_orders_panel = telebot.types.InlineKeyboardButton(text='Перейти к управлению заказами',
                                                              url='delivery-platform.com')
    keyboard.add(menu_button, rename_button, link_to_orders_panel)
    return keyboard


def create_menu_set_keyboard():
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    add_dish_button = telebot.types.InlineKeyboardButton(text='Добавить блюдо', callback_data='AddDish')
    change_dish_button = telebot.types.InlineKeyboardButton(text='Изменить блюдо', callback_data='change_dish')
    delete_dish_button = telebot.types.InlineKeyboardButton(text='Удалить блюдо', callback_data='delete_dish')
    keyboard.add(add_dish_button, change_dish_button, delete_dish_button)
    return keyboard


def create_change_action():
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    rename_name_button = telebot.types.InlineKeyboardButton(text='Изменить название', callback_data='rename_name')
    rename_description_button = telebot.types.InlineKeyboardButton(text='Изменить описание',
                                                                   callback_data='rename_description')
    change_cost = telebot.types.InlineKeyboardButton(text='Изменить стоимость', callback_data='change_cost')
    change_photo = telebot.types.InlineKeyboardButton(text='Изменить фото', callback_data='change_photo')
    keyboard.add(rename_name_button, rename_description_button, change_cost, change_photo)
    return keyboard


def create_oder_panel_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1)
    order_button = telebot.types.KeyboardButton(text='Оформить заказ')
    basket_button = telebot.types.KeyboardButton(text='Посмотреть корзину')
    keyboard.add(order_button, basket_button)
    return keyboard


def create_add_to_the_basket_button(dish_info):
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    add_button = telebot.types.InlineKeyboardButton(text='Добавить в корзину', callback_data=f'add_{dish_info}')
    keyboard.add(add_button)
    return keyboard


def create_menu_keyboard(dish_names, shop_id=None):
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    if shop_id:
        dish_buttons = [telebot.types.InlineKeyboardButton(text=name,
                                                           callback_data=f'{shop_id}_{name}') for name in dish_names]
    else:
        dish_buttons = [telebot.types.InlineKeyboardButton(text=name, callback_data=name) for name in dish_names]
    keyboard.add(*dish_buttons)
    return keyboard


def create_orders_keyboard(orders_id):
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    orders_id_buttons = [telebot.types.InlineKeyboardButton(text='Заказ #'+str(order_id[0]),
                                                            callback_data='#_'+str(order_id[0]))
                         for order_id in orders_id]
    keyboard.add(*orders_id_buttons)
    return keyboard


def clear_all_state(message):
    update_state(DELETE_DISH_STATE, message, DELETE_DISH_CLOSE)
    update_state(CHANGE_DISH_STATE, message, CHANGE_DISH_CLOSE)
    update_state(ADD_DISH_STATE, message, ADD_DISH_CLOSE)
    update_state(ACTIVATE_STATE, message, ACTIVATE_CLOSE)
    update_state(RENAME_STATE, message, RENAME_CLOSE)
    update_state(CREATE_SHOP_STATE, message, CREATE_SHOP_CLOSE)
    update_state(COMPLETE_ORDER_DATA_STATE, message, ORDER_DATA_CLOSE)


@bot.message_handler(commands=['start'])
def start_command(message):
    clear_all_state(message)
    bot.send_message(message.chat.id, 'Привет, ты на универсальной платформе по доставке еды.\n'
                                      'Достпуный список команд - /help')
    user_id = str(message.from_user.id)
    if [user_id] not in cursor.execute('select user_id from users').fetchall():
        cursor.execute(f"insert into users (user_id) values ('{user_id}')")
        connection.commit()


@bot.message_handler(commands=['jopa'])
def jopa_handler(message):
    bot.send_photo(message.chat.id, open('photos/jopa.jpg', 'rb'))
    bot.send_message(message.chat.id, 'Привет я жыпа!)')


@bot.message_handler(commands=['help'])
def help_command(message):
    clear_all_state(message)
    bot.send_message(message.chat.id, '/shops - выбрать ресторан\n'
                                      '/orders - посмотреть список ваших заказов\n'
                                      '--------------------------\n'
                                      'Команды для админов мимов:\n'
                                      '/activate_shop - активировать ресторан\n'
                                      '/panel - панель управления')


@bot.message_handler(commands=['shops'])
def shops_command(message):
    clear_all_state(message)
    bot.send_message(message.chat.id, 'Рестораны', reply_markup=create_keyboard_shops())


@bot.message_handler(commands=['orders'])
def orders_command(message):
    orders = cursor.execute(f"select id from orders where user_id='{message.from_user.id}'").fetchall()
    if orders:
        bot.send_message(message.chat.id, 'Ваши заказы:', reply_markup=create_orders_keyboard(orders))
    else:
        bot.send_message(message.chat.id, 'Список ваших заказов пуст')


@bot.callback_query_handler(func=lambda callback: '#_' in callback.data)
def order_handler(callback):
    message = callback.message
    order_info = \
        cursor.execute(f"select shop_id, basket_data, date, order_cost from orders where id={callback.data[2:]}") \
        .fetchall()[0]
    shop_name = cursor.execute(f"select name from shops where id={order_info[0]}").fetchall()[0][0]
    answer_string = f'Ресторан "{shop_name}"\n' \
                    f'Заказ:\n{order_info[1]}\n' \
                    f'Дата: {order_info[2]}\n' \
                    f'Стоимость: {order_info[3]}руб.'
    bot.send_message(message.chat.id, answer_string)


@bot.message_handler(commands=['activate_shop'])
def shop_activate_s1(message):
    clear_all_state(message)
    query_data = cursor.execute(f"select is_shop from users where user_id = '{message.from_user.id}'").fetchall()
    if query_data[0]:
        if not query_data[0][0]:
            bot.send_message(message.chat.id, 'Для создания магазина, отправьте боту специальный инвайт-код')
            update_state(ACTIVATE_STATE, message, ACTIVATE_FINAL)
        else:
            bot.send_message(message.chat.id, 'Вы уже активировали свой ресторан')
    else:
        user_id = str(message.from_user.id)
        if [user_id] not in cursor.execute('select user_id from users').fetchall():
            cursor.execute(f"insert into users (user_id) values ('{user_id}')")
            connection.commit()
        bot.send_message(message.chat.id, 'Для создания магазина, отправьте боту специальный инвайт-код')
        update_state(ACTIVATE_STATE, message, ACTIVATE_FINAL)


@bot.message_handler(func=lambda message: get_state(ACTIVATE_STATE, message) == ACTIVATE_FINAL)
def shop_activate_s2(message):
    code = message.text
    if [code] in cursor.execute('select code from invite_codes').fetchall():
        cursor.execute(f"delete from invite_codes where code = '{code}'")
        bot.send_message(message.chat.id,
                         'Вы успешно активировали свой ресторан, теперь вам доступна панель управления - /panel')
        cursor.execute(f"update users set is_shop = 'true' where user_id = '{message.from_user.id}'")
        connection.commit()
        update_state(ACTIVATE_STATE, message, ACTIVATE_CLOSE)
    else:
        bot.send_message(message.chat.id, 'Неверный код, попробуйте еще раз')


@bot.message_handler(commands=['panel'])
def panel_command(message):
    clear_all_state(message)
    if cursor.execute(f"select is_shop from users where user_id = '{message.from_user.id}'").fetchall()[0][0]:
        if cursor.execute(f"select user_id from shops where user_id = '{message.from_user.id}'").fetchall():
            bot.send_message(message.chat.id, f'Панель управления', reply_markup=create_panel_keyboard())
        else:
            bot.send_message(message.chat.id, 'Кажется вы еще не натсроили свой ресторан, давайте приступим!')
            bot.send_message(message.chat.id, 'Введите название своего ресторана')
            update_state(CREATE_SHOP_STATE, message, CREATE_SHOP_S1)
    else:
        bot.send_message(message.chat.id, 'У вас нет прав для использования данной команды')


@bot.message_handler(func=lambda message: get_state(CREATE_SHOP_STATE, message) == CREATE_SHOP_S1)
def create_shop_s1(message):
    SHOP_DATA[message.from_user.id] = {}
    SHOP_DATA[message.from_user.id]['name'] = message.text
    SHOP_DATA[message.from_user.id]['user_id'] = message.from_user.id
    bot.send_message(message.chat.id, 'Теперь введите описание своего ресторана')
    update_state(CREATE_SHOP_STATE, message, CREATE_SHOP_FINAL)


@bot.message_handler(func=lambda message: get_state(CREATE_SHOP_STATE, message) == CREATE_SHOP_FINAL)
def create_shop_final(message):
    SHOP_DATA[message.from_user.id]['description'] = message.text
    cursor.execute(
        f"insert into shops (name, description, user_id) values ('{SHOP_DATA[message.from_user.id]['name']}',"
        f" '{SHOP_DATA[message.from_user.id]['description']}',"
        f" '{SHOP_DATA[message.from_user.id]['user_id']}')"
    )
    connection.commit()
    bot.send_message(message.chat.id, f'Ресторан {SHOP_DATA[message.from_user.id]["name"]} успешно создан\n'
                                      f'Введите /panel для настройки меню ')
    update_state(CREATE_SHOP_STATE, message, CREATE_SHOP_CLOSE)


@bot.callback_query_handler(func=lambda callback: callback.data == 'rename_shop')
def rename_shop(callback):
    message = callback.message
    bot.send_message(message.chat.id, 'Введите новое имя вашего ресторана')
    update_state(RENAME_STATE, message, RENAME_S1)


@bot.message_handler(func=lambda message: get_state(RENAME_STATE, message) == RENAME_S1)
def rename_shop_final(message):
    new_name = message.text
    old_name = cursor.execute(f"select name from shops where user_id = '{message.from_user.id}'").fetchall()[0][0]
    cursor.execute(f"update shops set name = '{new_name}' where name = '{old_name}'")
    update_state(RENAME_STATE, message, RENAME_CLOSE)
    connection.commit()
    bot.send_message(message.chat.id, 'Имя успешно изменено')


@bot.callback_query_handler(func=lambda callback: callback.data == 'menu_set')
def menu_set(callback):
    SHOP_DATA[callback.from_user.id] = {}
    message = callback.message
    shop_id = cursor.execute(f"select id from shops where user_id = '{callback.from_user.id}'").fetchall()[0][0]
    SHOP_DATA[callback.from_user.id]['shop_id'] = shop_id
    SHOP_DATA[callback.from_user.id]['menu'] = \
        cursor.execute(f"select * from menu where shop_id='{SHOP_DATA[callback.from_user.id]['shop_id']}'").fetchall()
    bot.send_message(message.chat.id, 'Выберите действие', reply_markup=create_menu_set_keyboard())


@bot.callback_query_handler(func=lambda callback: str(callback.data).isdigit())
def shop_menu(callback):
    message = callback.message
    if not USER_BASKET_DATA.get(callback.from_user.id):
        USER_BASKET_DATA[callback.from_user.id] = {}
    if [int(callback.data)] in cursor.execute('select shop_id from menu').fetchall():
        shop_name_description = \
            cursor.execute(f"select name, description from shops where id={callback.data}").fetchall()[0]
        bot.send_message(message.chat.id, f'Ресторан "{shop_name_description[0]}"\n{shop_name_description[1]}')
        dishes = cursor.execute(f"select description, name, photo, cost from menu where shop_id = '{callback.data}'")\
            .fetchall()
        names = [i[1] for i in dishes]
        SHOP_MENU_DATA[callback.from_user.id] = {dish[1]: dish for dish in dishes}
        bot.send_message(message.chat.id, 'Доступные блюда:', reply_markup=create_menu_keyboard(names, callback.data))
    else:
        bot.send_message(message.chat.id, 'Кажется этот ресторан еще не настроил свое меню')


@bot.callback_query_handler(func=lambda callback:
                            callback.data.split('_')[1] in SHOP_MENU_DATA.get(callback.from_user.id) if SHOP_MENU_DATA
                            else False)
def dish_handler(callback):
    message = callback.message
    dish = SHOP_MENU_DATA[callback.from_user.id][callback.data.split('_')[1]]
    bot.send_photo(message.chat.id, open(dish[2], 'rb'),
                   caption=f"{dish[1]}\n"
                   f"{dish[0]}\n"
                   f"Стоимость: {dish[3]} руб.", reply_markup=create_add_to_the_basket_button(callback.data))


@bot.callback_query_handler(func=lambda callback: 'add_' in callback.data)
def add_to_the_user_basket(callback):
    message = callback.message
    shop_id = int(callback.data.split('_')[1])
    dish = callback.data.split('_')[2]
    dish_cost = cursor.execute(f"select cost from menu where shop_id={shop_id} and name='{dish}'").fetchall()[0][0]
    if shop_id not in USER_BASKET_DATA[callback.from_user.id]:
        USER_BASKET_DATA[callback.from_user.id][shop_id] = [(dish, dish_cost)]
    else:
        USER_BASKET_DATA[callback.from_user.id][shop_id].append((dish, dish_cost))
    bot.send_message(message.chat.id, f'Товар "{dish}" успешно добавлен в корзину',
                     reply_markup=create_oder_panel_keyboard())


@bot.message_handler(regexp='Посмотреть корзину')
def order_handler(message):
    clear_all_state(message)
    answer_string = ''
    cost_counter = 0
    if message.from_user.id in USER_BASKET_DATA:
        for i in USER_BASKET_DATA[message.from_user.id]:
            shop = cursor.execute(f"select name from shops where id={i}").fetchall()[0][0]
            answer_string += f'Из ресторана "{shop}" вы добавили в корзину:\n'
            for dish_and_cost in USER_BASKET_DATA[message.from_user.id][i]:
                answer_string += '  ' + dish_and_cost[0] + f' - {dish_and_cost[1]}руб.\n'
                cost_counter += dish_and_cost[1]
        answer_string += f'Общая сумма заказа - {cost_counter}руб.'
        bot.send_message(message.chat.id, answer_string)
    else:
        bot.send_message(message.chat.id, 'Корзина пуста')


@bot.callback_query_handler(func=lambda callback: callback.data == 'delete_dish')
def delete_dish_start(callback):
    message = callback.message
    bot.send_message(message.chat.id, 'Выберите позицию, которую хотите удалить',
                     reply_markup=create_menu_keyboard([i[2] for i in SHOP_DATA[callback.from_user.id]['menu']]))
    update_state(DELETE_DISH_STATE, message, DELETE_DISH_S1)


@bot.callback_query_handler(func=lambda callback: get_state(DELETE_DISH_STATE, callback.message) == DELETE_DISH_S1)
def delete_dish_final(callback):
    message = callback.message
    cursor.execute(f"delete from menu where name='{callback.data}'")
    connection.commit()
    bot.send_message(message.chat.id, 'Позиция успешно удалена')
    update_state(DELETE_DISH_STATE, message, DELETE_DISH_CLOSE)


@bot.callback_query_handler(func=lambda callback: callback.data == 'change_dish')
def change_dish_start(callback):
    message = callback.message
    bot.send_message(message.chat.id, 'Выберите позицию для изменения:',
                     reply_markup=create_menu_keyboard([i[2] for i in SHOP_DATA[callback.from_user.id]['menu']]))
    update_state(CHANGE_DISH_STATE, message, CHANGE_DISH_STATE_S1)


@bot.callback_query_handler(func=lambda callback:
                            get_state(CHANGE_DISH_STATE, callback.message) == CHANGE_DISH_STATE_S1)
def select_change_action(callback):
    message = callback.message
    dish = None
    for i in SHOP_DATA[callback.from_user.id]['menu']:
        if callback.data in i:
            dish = i
            break
    SHOP_DATA[callback.from_user.id]['change_position'] = dish
    bot.send_message(message.chat.id, 'Выберите действие:', reply_markup=create_change_action())
    update_state(CHANGE_DISH_STATE, message, CHANGE_DISH_STATE_S2)


@bot.callback_query_handler(func=lambda callback:
                            get_state(CHANGE_DISH_STATE, callback.message) == CHANGE_DISH_STATE_S2)
def action_handler(callback):
    message = callback.message
    dish_name = SHOP_DATA[callback.from_user.id]['change_position'][2]
    if callback.data == 'rename_name':
        bot.send_message(message.chat.id, f'Введите новое название для "{dish_name}"')
    elif callback.data == 'rename_description':
        bot.send_message(message.chat.id, f'Введите новое описание для "{dish_name}"')
    elif callback.data == 'change_cost':
        bot.send_message(message.chat.id, f'Укажите новую стоимость для "{dish_name}"')
    else:
        bot.send_message(message.chat.id, f'Отправьте новое фото для "{dish_name}"')
    SHOP_DATA[callback.from_user.id]['change_action'] = callback.data
    update_state(CHANGE_DISH_STATE, message, CHANGE_DISH_STATE_S3)


@bot.message_handler(func=lambda message: get_state(CHANGE_DISH_STATE, message) == CHANGE_DISH_STATE_S3)
def save_new_param(message):
    dish_id = SHOP_DATA[message.from_user.id]['change_position'][0]
    if SHOP_DATA[message.from_user.id]['change_action'] == 'rename_name':
        new_name = message.text
        cursor.execute(f"update menu set name='{new_name}' where id={dish_id}")
    elif SHOP_DATA[message.from_user.id]['change_action'] == 'rename_description':
        new_description = message.text
        cursor.execute(f"update menu set description='{new_description}' where id={dish_id}")
    elif SHOP_DATA[message.from_user.id]['change_action'] == 'change_cost':
        new_cost = int(message.text)
        cursor.execute(f"update menu set cost={new_cost} where id={dish_id}")
    else:
        try:
            file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            with open(file_info.file_path, 'wb') as new_file:
                new_file.write(downloaded_file)
            cursor.execute(f"update menu set photo='{file_info.file_path}' where id{dish_id}")
        except Exception:
            bot.send_message(message.chat.id, 'Размер фотографии не должен превышать 20мб')
    connection.commit()
    new_dish = cursor.execute(f"select * from menu where id={dish_id}").fetchall()
    dish_name = new_dish[0][2]
    dish_description = new_dish[0][1]
    dish_photo = new_dish[0][3]
    dish_cost = new_dish[0][4]
    bot.send_photo(message.chat.id, open(dish_photo, 'rb'),
                   caption=f"{dish_name}\n{dish_description}\nСтоимость: {dish_cost} руб.")
    update_state(CHANGE_DISH_STATE, message, CREATE_SHOP_CLOSE)
    SHOP_DATA[message.from_user.id].pop('change_position')
    SHOP_DATA[message.from_user.id].pop('change_action')
    bot.send_message(message.chat.id, 'Все данные были успешно изменены')


@bot.callback_query_handler(func=lambda callback: callback.data == 'AddDish')
def add_dish_start(callback):
    message = callback.message
    bot.send_message(message.chat.id, 'Введите название блюда')
    SHOP_DATA[callback.from_user.id]['dish'] = {}
    update_state(ADD_DISH_STATE, message, ADD_DISH_NAME)


@bot.message_handler(func=lambda message: get_state(ADD_DISH_STATE, message) == ADD_DISH_NAME)
def add_dish_name(message):
    SHOP_DATA[message.from_user.id]['dish']['name'] = message.text
    bot.send_message(message.chat.id, 'Введите описание')
    update_state(ADD_DISH_STATE, message, ADD_DISH_DESCRIPTION)


@bot.message_handler(func=lambda message: get_state(ADD_DISH_STATE, message) == ADD_DISH_DESCRIPTION)
def add_dish_description(message):
    SHOP_DATA[message.from_user.id]['dish']['description'] = message.text
    bot.send_message(message.chat.id, 'Пришлите фото')
    update_state(ADD_DISH_STATE, message, ADD_DISH_PHOTO)


@bot.message_handler(func=lambda message: get_state(ADD_DISH_STATE, message) == ADD_DISH_PHOTO, content_types=['photo'])
def add_dish_photo(message):
    try:
        file_info = bot.get_file(message.photo[len(message.photo)-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open(file_info.file_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        SHOP_DATA[message.from_user.id]['dish']['photo'] = file_info.file_path
        bot.send_message(message.chat.id, 'Укажите цену на блюдо в рублях')
        update_state(ADD_DISH_STATE, message, ADD_DISH_COST)
    except Exception:
        bot.send_message(message.chat.id, 'Размер фотографии не должен превышать 20мб')


@bot.message_handler(func=lambda message: get_state(ADD_DISH_STATE, message) == ADD_DISH_COST)
def add_dish_final(message):
    if message.text.isdigit():
        SHOP_DATA[message.from_user.id]['dish']['cost'] = message.text
        bot.send_photo(message.chat.id, open(SHOP_DATA[message.from_user.id]['dish']['photo'], 'rb'),
                       caption=f"{SHOP_DATA[message.from_user.id]['dish']['name']}\n"
                               f"{SHOP_DATA[message.from_user.id]['dish']['description']}\n"
                               f"Стоимость: {SHOP_DATA[message.from_user.id]['dish']['cost']} руб.")
        cursor.execute(f"insert into menu (description, name, photo, cost, shop_id) "
                       f"values ('{SHOP_DATA[message.from_user.id]['dish']['description']}',"
                       f" '{SHOP_DATA[message.from_user.id]['dish']['name']}',"
                       f" '{SHOP_DATA[message.from_user.id]['dish']['photo']}',"
                       f" '{SHOP_DATA[message.from_user.id]['dish']['cost']}',"
                       f" '{SHOP_DATA[message.from_user.id]['shop_id']}')")
        connection.commit()
        bot.send_message(message.chat.id, 'Все данные были успешно сохранены')
        update_state(ADD_DISH_STATE, message, ADD_DISH_CLOSE)
    else:
        bot.send_message(message.chat.id, 'Пожалуйста введите числовое значение')


@bot.message_handler(regexp='Оформить заказ')
def checkout_handler(message):
    clear_all_state(message)
    if not cursor.execute(f"select delivery_data from users where user_id='{message.from_user.id}'").fetchall()[0][0]:
        bot.send_message(message.chat.id, 'Кажется вы еще не заполнили данные для доставки, давайте приступим')
        bot.send_message(message.chat.id, 'Отправьте свои данные вида:\n'
                                          'Город, улица, дом, корпус, подъезд, этаж\n'
                                          'Имя\n'
                                          'Телефон для связи')
        update_state(COMPLETE_ORDER_DATA_STATE, message, ORDER_DATA_S1)
    elif message.from_user.id in USER_BASKET_DATA:
        delivery_data = cursor.execute(f"select delivery_data from users where user_id='{message.from_user.id}'") \
                        .fetchall()[0][0]
        date = datetime.now()
        for shop_id in USER_BASKET_DATA[message.from_user.id]:
            cursor.execute(f"insert into orders (shop_id, basket_data, delivery_data, date, user_id, order_cost) "
                           f"values ("
                           f"{shop_id}, "
                           f"'{', '.join(map(lambda x: x[0], USER_BASKET_DATA[message.from_user.id][shop_id]))}', "
                           f"'{delivery_data}', '{date}', '{message.from_user.id}', "
                           f"{sum(map(lambda x: x[1], USER_BASKET_DATA[message.from_user.id][shop_id]))}"
                           f")")
            connection.commit()
        # Где-то здесь данные должны отправляться API
        USER_BASKET_DATA.pop(message.from_user.id)
        orders_id = cursor.execute(f"select id from orders where date='{date}'").fetchall()
        for order_id in orders_id:
            bot.send_message(message.chat.id, f'Заказ #{order_id[0]} успешно создан')
    else:
        bot.send_message(message.chat.id, 'Ваша корзина пуста, вы не можете оформить заказ')


@bot.message_handler(func=lambda message: get_state(COMPLETE_ORDER_DATA_STATE, message) == ORDER_DATA_S1)
def checkout_handler_final(message):
    order_data = message.text
    cursor.execute(f"update users set delivery_data='{order_data}' where user_id='{message.from_user.id}'")
    connection.commit()
    if USER_BASKET_DATA[message.from_user.id]:
        bot.send_message(message.chat.id, 'Данные успешно сохранены\nСейчас произойдет оформление заказа')
        checkout_handler(message)
    else:
        bot.send_message(message.chat.id, 'Данные успешно сохранены')
    update_state(COMPLETE_ORDER_DATA_STATE, message, ORDER_DATA_CLOSE)


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0, timeout=3)
