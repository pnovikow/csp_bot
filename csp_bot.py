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
        with open('stickers/sticker.png', 'wb') as file:
            file.write(response.content)
    else:
        bot.send_message(message.chat.id, 'Не удалось скачать стикер.')

    # Отправляем сообщение
    bot.send_message(message.chat.id, message_text)

# Запускаем бота
bot.polling()

