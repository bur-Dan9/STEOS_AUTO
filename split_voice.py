from pydub import AudioSegment
from pydub.silence import split_on_silence

print("Загружаем длинное аудио...")
# Загружаем твой файл
audio = AudioSegment.from_file("input/voice.mp3")
print(f"Аудио загружено! Общая длина: {len(audio) / 1000} секунд.")

print("Ищем естественные паузы в речи...")
# Разбиваем аудио на короткие фразы, ориентируясь на тишину
phrases = split_on_silence(
    audio,
    min_silence_len=400,            # Считаем паузой тишину от 0.4 секунд
    silence_thresh=audio.dBFS - 14, # Насколько тихо должно быть, чтобы считать это паузой
    keep_silence=200                # Оставляем немного тишины по краям, чтобы речь звучала естественно
)

print(f"Найдено {len(phrases)} коротких фраз. Начинаем собирать их в части до 29 секунд...")

current_chunk = AudioSegment.empty()
chunk_index = 1

# Собираем мелкие фразы в куски для бота
for phrase in phrases:
    # Если при добавлении новой фразы длина превысит 29 секунд (29000 миллисекунд)
    if len(current_chunk) + len(phrase) > 29000:
        # Сохраняем текущий кусок в папку parts
        current_chunk.export(f"parts/part_{chunk_index}.mp3", format="mp3")
        print(f"Сохранен файл part_{chunk_index}.mp3 (длина: {len(current_chunk)/1000} сек)")
        
        # Начинаем собирать следующий кусок
        chunk_index += 1
        current_chunk = phrase
    else:
        # Иначе просто приклеиваем фразу к текущему куску
        current_chunk += phrase

# Сохраняем самый последний кусочек (хвостик аудио), если в нём что-то осталось
if len(current_chunk) > 0:
    current_chunk.export(f"parts/part_{chunk_index}.mp3", format="mp3")
    print(f"Сохранен последний файл part_{chunk_index}.mp3 (длина: {len(current_chunk)/1000} сек)")

print("Нарезка успешно завершена! Проверь папку parts.")