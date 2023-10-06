import telebot
import os
import requests
from telebot import types

# Инициализируем бота
bot = telebot.TeleBot("TG_TOKEN")

# Словарь для хранения параметров стикерпака пользователя
user_sticker_pack_config = {}

@bot.message_handler(commands=['configure_sticker_pack'])
def configure_sticker_pack(message):
    user_id = message.from_user.id

    # Запрашиваем имя стикерпака
    bot.send_message(user_id, "Введите имя для вашего стикерпака, которое будет частью URL:")
    bot.register_next_step_handler(message, get_sticker_pack_name)

def get_sticker_pack_name(message):
    user_id = message.from_user.id
    sticker_pack_name = message.text

    # Сохраняем имя стикерпака в словаре
    user_sticker_pack_config[user_id] = {'name': sticker_pack_name}

    # Запрашиваем заголовок стикерпака
    bot.send_message(user_id, "Введите название для вашего стикерпака, оно будет видно в предвросмотре стикерпака:")
    bot.register_next_step_handler(message, get_sticker_pack_title)

def get_sticker_pack_title(message):
    user_id = message.from_user.id
    sticker_pack_title = message.text

    # Сохраняем заголовок стикерпака в словаре
    user_sticker_pack_config[user_id]['title'] = sticker_pack_title

    # Запрашиваем эмодзи стикерпака
    bot.send_message(user_id, "Введите эмодзи для вашего стикерпака:")
    bot.register_next_step_handler(message, get_sticker_pack_emojis)

def get_sticker_pack_emojis(message):
    user_id = message.from_user.id
    sticker_pack_emojis = message.text

    # Сохраняем эмодзи стикерпака в словаре
    user_sticker_pack_config[user_id]['emojis'] = sticker_pack_emojis

    # Запрашиваем тип стикерпака (статичный или анимированный)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add(types.KeyboardButton('Статичный'), types.KeyboardButton('Анимированный'))

    bot.send_message(user_id, "Выберите тип стикерпака:", reply_markup=markup)
    bot.register_next_step_handler(message, get_sticker_pack_type)

def get_sticker_pack_type(message):
    user_id = message.from_user.id
    sticker_pack_type = message.text.lower()

    if sticker_pack_type in ('статичный', 'анимированный'):
        # Сохраняем тип стикерпака в словаре
        user_sticker_pack_config[user_id]['is_animated'] = (sticker_pack_type == 'анимированный')

        # Выводим информацию о настроенных параметрах стикерпака
        config_info = user_sticker_pack_config[user_id]
        response = f"Настроенные параметры стикерпака:\nИмя: {config_info['name']}\nЗаголовок: {config_info['title']}\nЭмодзи: {config_info['emojis']}\nТип: {'Анимированный' if config_info['is_animated'] else 'Статичный'}"
        bot.send_message(user_id, response)

        # Здесь вы можете вызвать функцию create_sticker_pack, передав параметры из словаря user_sticker_pack_config

    else:
        bot.send_message(user_id, "Пожалуйста, выберите тип 'Статичный' или 'Анимированный'.")


@bot.message_handler(commands=['reset', 'start', 'help'])
def reset_handler(message):
    # Get the user's ID
    user_id = message.from_user.id

    # Create a directory for the user's stickers if it doesn't exist
    user_sticker_dir = f'assets/stickers_{user_id}'

    # Delete the contents of the user's sticker directory
    for file_name in os.listdir(user_sticker_dir):
        file_path = os.path.join(user_sticker_dir, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)

    # Clear the user's sticker pack configuration
    user_sticker_pack_config[user_id] = {}

    # Send a welcome message with usage instructions
    welcome_message =  "Welcom to CustomStickerPack bot.\n\n" \
                       "This bot can help you create your own perfect StickerPack\n" \
                       "with your favorite stickers, and you will not need\n" \
                       "save tonns unused StickerPacks. \n\n" \
                       "Instruction: \n" \
                       "1. Send /start command to start from the very beginning\n" \
                       "2. Now send to bots your favorite stickers. \n" \
                       "Please be aware - only static stickers are supported\n" \
                       "3. When you decide on the amount of stickers you need to configure\n" \
                       "you StickerPack setting\n" \
                       "4. Send /configure_sticker_pack command\n" \
                       "Name: set name, will part of URL: https://t.me/addstickers/YOUR_NAME+_by_c_s_p_bot \n" \
                       "Title: The name of StickerPack, will show in the StickerPack preview\n" \
                       "Emoji: 🤔\n" \
                       "Type: Now supported only static\n" \
                       "5. When finished send command /create_sticker_pack\n\n" \
                       "Enjoy!\n"
    
    bot.send_message(message.chat.id, welcome_message)

@bot.message_handler(content_types=['sticker'])
def sticker_handler(message):

    # Get the user's ID
    user_id = message.from_user.id

    # Create a directory for the user's stickers if it doesn't exist
    user_sticker_dir = f'assets/stickers_{user_id}'
    os.makedirs(user_sticker_dir, exist_ok=True)

    # Получаем информацию о стикере
    sticker = message.sticker

    # Формируем сообщение с информацией о стикере
    message_text = f'Стикер: {sticker.file_id}\n\n' \
                   f'Название: {sticker.set_name}\n\n' \
                   f'type: {sticker.type}'

    # Получаем URL файла стикера
    sticker_file_id = sticker.file_id
    file_info = bot.get_file(sticker_file_id)
    file_url = f'https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}'

    # Сохраняем изображение стикера на сервере
    response = requests.get(file_url)
    if response.status_code == 200:
        with open(f'{user_sticker_dir}/{sticker_file_id}.png', 'wb') as file:
            file.write(response.content)
    else:
        bot.send_message(message.chat.id, 'Не удалось скачать стикер.')

    # Отправляем сообщение
    bot.send_message(message.chat.id, message_text)

@bot.message_handler(commands=['create_sticker_pack'])
def create_sticker_pack(message):
    
    # Get the user's ID
    user_id = message.from_user.id
    # Create a directory for the user's stickers if it doesn't exist
    user_sticker_dir = f'assets/stickers_{user_id}'

    # Получаем список файлов в каталоге "stickers"
    sticker_files = [
        os.path.join(user_sticker_dir, file_name)
        for file_name in os.listdir(user_sticker_dir)
        if os.path.isfile(os.path.join(user_sticker_dir, file_name))
    ]

    # Проверяем, что в каталоге есть хотя бы 1 файл (минимальное количество для стикерпака)
    if len(sticker_files) < 1:
        bot.send_message(message.chat.id, 'Для создания стикерпака нужно как минимум 1 стикер.')
        return

    user_id = message.from_user.id

    # Конфигурируем параметры стикерпака
    # Читаем пользовательские настройки
    config_info = user_sticker_pack_config[user_id]
    # Получаем имя
    sticker_set_name = f"{config_info['name']}_{user_id}" + '_by_c_s_p_bot'
    title_name = f"{config_info['title']}"
    custom_emoji = f"{config_info['emojis']}"

    try:
        message = bot.send_message(chat_id=user_id, text='Processing...')

        sticker_set = None
        try:
            sticker_set = bot.get_sticker_set(sticker_set_name)
        except:
            pass

        if sticker_set:
            for sticker in sticker_set.stickers:
                bot.delete_sticker_from_set(sticker.file_id)
        bot.edit_message_text(chat_id=user_id, text='Creating sticker pack...',
                                            message_id=message.message_id)

        if sticker_set is None:
            bot.create_new_sticker_set(user_id, name=sticker_set_name, title=title_name,
                                                        png_sticker=open(sticker_files[0], 'rb'), emojis=[custom_emoji])

        idx = 1
        for file in sticker_files:
            text = 'Adding stickers to sticker set ' + str(idx) + '/' + str(len(sticker_files)) + '...'
            bot.edit_message_text(chat_id=user_id, text=text, message_id=message.message_id)
            bot.add_sticker_to_set(user_id, name=sticker_set_name, png_sticker=open(file, 'rb'),
                                                emojis=[custom_emoji])
            idx += 1
            
        sticker_set = bot.get_sticker_set(sticker_set_name)
        bot.edit_message_text(chat_id=user_id, text='Done!', message_id=message.message_id)
        # bot.send_sticker(chat_id=user_id, sticker=sticker_set.stickers[0].file_id)
        bot.edit_message_text(chat_id=user_id, text='Кликни по стикеру ^ чтобы добавить себе стикерпак!', message_id=message.message_id)
        # Получаем ссылку на созданный стикерпак
        sticker_pack_link = f'https://t.me/addstickers/{sticker_set_name}'

        # Define the file path for storing sticker pack links
        links_file_path = 'sticker_pack_links.txt'

        # Append the sticker pack link to the file
        with open(links_file_path, 'a') as links_file:
            links_file.write(sticker_pack_link + '\n')

        bot.send_message(message.chat.id, f'Или воспользуйся ссылкой:\n{sticker_pack_link}')

    except Exception as e:
        print(e)
        bot.send_message(chat_id=user_id, text='Something went wrong. Please try again.')
        bot.send_message(chat_id=user_id, text=str(e))

# Запускаем бота
bot.polling()
