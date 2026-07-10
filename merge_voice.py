import os
from pydub import AudioSegment

print("Начинаем склеивать обработанные части...")

# Создаем пустую аудиодорожку
final_audio = AudioSegment.empty()

index = 1
# Программа будет искать файлы 1.ogg, 2.ogg и так далее по очереди
while True:
    file_path = f"result/{index}.ogg"
    
    # Проверяем, существует ли такой файл
    if os.path.exists(file_path):
        print(f"Приклеиваем кусок: {index}.ogg...")
        chunk = AudioSegment.from_file(file_path)
        final_audio += chunk
        index += 1
    else:
        # Если файла с таким номером нет, значит мы склеили всё
        break

print("Сохраняем готовый результат...")
# Экспортируем итоговый файл
final_audio.export("final_voice.mp3", format="mp3")
print("Готово! Итоговый файл final_voice.mp3 сохранен.")
