import os
import telebot
from telebot import types
from pydub import AudioSegment
from pydub.silence import split_on_silence

# Вставь свой токен внутри кавычек
TOKEN = '8849250357:AAH1cs0AUK9MtqB9vr4bk3dQqHLYXuJGr48'
bot = telebot.TeleBot(TOKEN)

WORK_DIR = "bot_work"
os.makedirs(WORK_DIR, exist_ok=True)

def get_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🧵 Сшить файлы"), types.KeyboardButton("🗑 Очистить память"))
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    text = "Привет! Я готов. Скидывай длинное аудио или куски от STEOS."
    bot.send_message(message.chat.id, text, reply_markup=get_keyboard())

@bot.message_handler(func=lambda message: message.text in ["🧵 Сшить файлы", "🗑 Очистить память"])
def handle_buttons(message):
    if message.text == "🗑 Очистить память":
        for file in os.listdir(WORK_DIR):
            os.remove(os.path.join(WORK_DIR, file))
        bot.send_message(message.chat.id, "Память очищена! Жду новые файлы.", reply_markup=get_keyboard())
        
    elif message.text == "🧵 Сшить файлы":
        files = sorted(os.listdir(WORK_DIR))
        if not files:
            bot.send_message(message.chat.id, "Память пуста. Сначала скинь мне куски!")
            return
            
        bot.send_message(message.chat.id, "Склеиваю файлы, подожди секунду...")
        try:
            final_audio = AudioSegment.empty()
            for file in files:
                final_audio += AudioSegment.from_file(os.path.join(WORK_DIR, file))
            
            final_audio.export("final_result.mp3", format="mp3")
            with open("final_result.mp3", 'rb') as f:
                bot.send_audio(message.chat.id, f, title="Грубый голос (Готово)")
            bot.send_message(message.chat.id, "Сделано! Нажми «Очистить память» перед следующим треком.")
        except Exception as e:
            bot.send_message(message.chat.id, "Ой, произошла ошибка при склейке.")
            print(e)

@bot.message_handler(content_types=['voice', 'audio', 'document'])
def handle_docs_audio(message):
    bot.send_message(message.chat.id, "Скачиваю файл...")
    try:
        if message.content_type == 'voice':
            file_info = bot.get_file(message.voice.file_id)
        elif message.content_type == 'audio':
            file_info = bot.get_file(message.audio.file_id)
        else:
            file_info = bot.get_file(message.document.file_id)
            
        downloaded_file = bot.download_file(file_info.file_path)
        
        temp_path = f"temp_{message.message_id}.mp3"
        with open(temp_path, 'wb') as new_file:
            new_file.write(downloaded_file)
            
        audio = AudioSegment.from_file(temp_path)
        audio_length = len(audio) / 1000
        
        if audio_length > 35:
            bot.send_message(message.chat.id, f"Длинное аудио ({int(audio_length)} сек). Режу...")
            phrases = split_on_silence(audio, min_silence_len=400, silence_thresh=audio.dBFS - 14, keep_silence=200)
            
            current_chunk = AudioSegment.empty()
            chunk_index = 1
            for phrase in phrases:
                if len(current_chunk) + len(phrase) > 29000:
                    chunk_path = f"part_{chunk_index}.mp3"
                    current_chunk.export(chunk_path, format="mp3")
                    with open(chunk_path, 'rb') as f:
                        bot.send_audio(message.chat.id, f, title=f"Часть {chunk_index}")
                    os.remove(chunk_path)
                    chunk_index += 1
                    current_chunk = phrase
                else:
                    current_chunk += phrase
                    
            if len(current_chunk) > 0:
                chunk_path = f"part_{chunk_index}.mp3"
                current_chunk.export(chunk_path, format="mp3")
                with open(chunk_path, 'rb') as f:
                    bot.send_audio(message.chat.id, f, title=f"Часть {chunk_index}")
                os.remove(chunk_path)
                
            bot.send_message(message.chat.id, "Нарезка завершена! Перешли эти куски в STEOS.")
        else:
            # ИСПРАВЛЕНО ЗДЕСЬ: Сохраняем в MP3 вместо OGG
            part_path = os.path.join(WORK_DIR, f"{message.message_id}.mp3")
            audio.export(part_path, format="mp3")
            bot.send_message(message.chat.id, f"✅ Кусок сохранён в память.")
            
        os.remove(temp_path)
        
    except Exception as e:
        print(f"Ошибка: {e}")
        bot.send_message(message.chat.id, "Файл не удалось прочитать.")

print("Бот готов к работе (mp3 версия)!")
bot.polling(none_stop=True)