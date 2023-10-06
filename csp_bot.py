import telebot
import os
import requests

# Инициализируем бота
bot = telebot.TeleBot("5554833944:AAE14KSp7zE0ihRKMnZ_JlxMuXBX5gawdwM")

# Обрабатываем входящие сообщения
@bot.message_handler(commands=['start', 'help'])
def start(message):
    # Отправляем приветствие
    bot.send_message(message.chat.id, 'Привет! Я твой бот. Что ты хочешь сделать?')

@bot.message_handler(content_types=['sticker'])
def sticker_handler(message):
    # Получаем информацию о стикере
    sticker = message.sticker

    # Формируем сообщение с информацией о стикере
    message_text = f'Стикер: {sticker.file_id}\n\n' \
                   f'Название: {sticker.set_name}\n\n' \
                   f'Размер: {sticker.file_size} байт\n\n' \
                   f'custom_emoji_id: {sticker.custom_emoji_id}\n\n' \
                   f'emoji: {sticker.emoji}\n\n' \
                   f'width: {sticker.width}\n\n' \
                   f'height: {sticker.height}\n\n' \
                   f'thumbnail: {sticker.thumbnail}\n\n' \
                   f'type: {sticker.type}'

    # Получаем URL файла стикера
    sticker_file_id = sticker.file_id
    file_info = bot.get_file(sticker_file_id)
    file_url = f'https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}'

    # Сохраняем изображение стикера на сервере
    response = requests.get(file_url)
    if response.status_code == 200:
        with open(f'stickers/{sticker_file_id}.png', 'wb') as file:
            file.write(response.content)
    else:
        bot.send_message(message.chat.id, 'Не удалось скачать стикер.')

    # Отправляем сообщение
    bot.send_message(message.chat.id, message_text)

@bot.message_handler(commands=['create_sticker_pack'])
def create_sticker_pack(message):
    # Получаем список файлов в каталоге "stickers"
    sticker_files = [
        os.path.join('stickers', file_name)
        for file_name in os.listdir('stickers')
        if os.path.isfile(os.path.join('stickers', file_name))
    ]

    # Проверяем, что в каталоге есть хотя бы 1 файл (минимальное количество для стикерпака)
    if len(sticker_files) < 1:
        bot.send_message(message.chat.id, 'Для создания стикерпака нужно как минимум 1 стикер.')
        return

    # Отправляем отладочное сообщение с найденными файлами для стикеров
    # (используем метод .get_file_names() вместо .file_size_bytes())
    files_message = 'Найденные файлы для стикеров:\n'
    for file_name in sticker_files:
        files_message += file_name + '\n'
    bot.send_message(message.chat.id, files_message)
    user_id = message.from_user.id
    sticker_set_name = f"csp_bot_test_{user_id}" + '_by_c_s_p_bot'

    try:
        message = bot.send_message(chat_id=user_id, text='Processing...')

        sticker_set = None
        try:
            sticker_set = bot.get_sticker_set(sticker_set_name)
        except:
            pass

        if sticker_set:
            # context.bot.edit_message_text(chat_id=user_id, text='Done!', message_id=message.message_id)

            # context.bot.send_sticker(chat_id=user_id, sticker=sticker_set.stickers[0].file_id)
            # return

            for sticker in sticker_set.stickers:
                bot.delete_sticker_from_set(sticker.file_id)
        bot.edit_message_text(chat_id=user_id, text='Creating sticker pack...',
                                            message_id=message.message_id)

        if sticker_set is None:
            bot.create_new_sticker_set(user_id, name=sticker_set_name, title="MagicPack",
                                                        png_sticker=open(sticker_files[0], 'rb'), emojis=['👍'])

        idx = 1
        for file in sticker_files:
            text = 'Adding stickers to sticker set ' + str(idx) + '/' + str(len(sticker_files)) + '...'
            bot.edit_message_text(chat_id=user_id, text=text, message_id=message.message_id)
            bot.add_sticker_to_set(user_id, name=sticker_set_name, png_sticker=open(file, 'rb'),
                                                emojis=['👍'])
            idx += 1
        sticker_set = bot.get_sticker_set(sticker_set_name)
        bot.edit_message_text(chat_id=user_id, text='Done!', message_id=message.message_id)
        bot.send_sticker(chat_id=user_id, sticker=sticker_set.stickers[0].file_id)
        bot.edit_message_text(chat_id=user_id, text='Кликни по стикеру ^ чтобы добавить себе стикерпак!', message_id=message.message_id)
        # Получаем ссылку на созданный стикерпак
        sticker_pack_link = f'https://t.me/addstickers/{new_sticker_set.name}'
        bot.send_message(message.chat.id, f'Или воспользуйся ссылкой:\n{sticker_pack_link}')

    except Exception as e:
        print(e)
        bot.send_message(chat_id=user_id, text='Something went wrong. Please try again.')
        bot.send_message(chat_id=user_id, text=str(e))

# Запускаем бота
bot.polling()
