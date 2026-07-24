#!/home/zhabee/AI/venv/bin/python3

from g4f.client import Client
from g4f.local import LocalClient #Если нужна локальная модель
from colorama import Fore, Style
from deep_translator import GoogleTranslator
from pick import pick
from pathlib import Path
import time
import json

def timers(star, end):
    res = end - star
    if res >= 60:
        res /= 60
        return f"{res:.2f} мин"
    else:
        return f"{res:.2f} сек"

def is_russ(text):
    for char in text:
        if char in rusA:
            return True
        else:
            return False

client = Client()
#client = LocalClient() - убрать # если нужна локальная модель и выбрать нужную из списка LocalModel.txt и вставить в model_ch
model_ch = "deepseek-r1"
model_image = "flux"
translator = GoogleTranslator(source='ru', target='en')
messages = []

folder_prompts = Path('prompts')
folder_prompts.mkdir(exist_ok=True)
folder_file = Path('file')
folder_file.mkdir(exist_ok=True)

titleMod = 'Модовая панель:'
optionsMod = ['• Чат бот', '• Генерация картинки', '• Вернуться к чату']
_, control = pick(optionsMod, titleMod, indicator="→")
control += 1

pod = ['yes', 'y', 'да', 'д']
otk = ['no', 'n', 'нет', 'н', 'т']
rusA = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя!,.?:;"
addition = ""

if control == 1:
    titleView = 'Глубина мышления'
    optionsView = ['• Глубокая генерация', '• Обычная генерация', '• Читать из файла']
    _,view = pick(optionsView,titleView, indicator="→")
    view += 1

    if view == 1:
        with open ("promptPLUS.txt", "r", encoding="utf-8") as f:
            addition = f.read()

    elif view == 2:
        addition = ""

    elif view == 3:
        docum = Path('file').glob('*.odt')
        nameDoc = [doc.name for doc in docum]
        nameDocument, _ = pick(nameDoc, indicator="→")
        with open (f'file/{nameDocument}', "r", encoding="utf-8") as f:
            addition = f.read() + "\n\n"
        

while True:
    if control == 1:
        question = input()
        contents = addition + question 

        if question == ".":
            print("Сохранить чат? (y/n)")
            history = str(input())
            if history in pod:
                print("Название чата:")
                nameFile = str(input())
                with open (f"prompts/{nameFile}.json", "w", encoding="utf-8") as f:
                    json.dump(messages, f, ensure_ascii=False)

                print('<Чат сохранен>')    
                break
            else:
                break
        
        messages.append({"role": "user", "content": contents}) # для контекста закидываем наше сообщение
        start = time.perf_counter()

        response = client.chat.completions.create(
            model=model_ch,
            messages=messages,
            web_search=False
        )

        reply = response.choices[0].message.content
        messages.append({"role": "assistant", "content": reply}) # заносим ответ в контекст

        end = time.perf_counter()
        print(f'{Fore.BLUE}—— {reply}{Style.RESET_ALL} \n({timers(start, end)})\n')

    elif control == 2:
        prompt = str(input())
        start = time.perf_counter()

        if is_russ(prompt):
            promptEN = translator.translate(prompt)
        else:
            promptEN = prompt

        response = client.images.generate(
        model=model_image,
        prompt=promptEN,
        response_format="url"
        )

        end = time.perf_counter()
        print(f"{Fore.BLUE}Generated image URL: {response.data[0].url}{Style.RESET_ALL}\n({timers(start, end)})")
        break

    elif control == 3:
        fiels = Path('prompts').glob('*.json')
        namePrompt = [fil.name for fil in fiels]
        foundNameFile, _ = pick(namePrompt, indicator="→")

        with open (f"prompts/{foundNameFile}") as f:
            messages = json.load(f)
        
        print(f"<История {foundNameFile} загружена. Переход к диалогу.>")
        control = 1
        continue 

    else:
        break

