import requests
import json
from pprint import pprint

username = input('Введите username: ')
if username == '': # если пусто, то пользователь по умолчанию
    username = 'IgVasB'
url = 'https://api.github.com/users/'+username+'/repos'

resp=requests.get(url).json() # делаем запрос, получаем ответ, сразу преобразуем в json
print('Получен ответ сервера')
print(resp) #выводим на экран

repo = []
for i in resp: # в цикле ищем все репозитории по ключу и добавляем к repo
    repo.append(i['name'])
print(f'Репозитории пользователя {username}')
pprint(repo) #выводим репозитории пользователя на экран

#сохраняем репозитории в json файл
with open(username+'_repo.json', 'w') as f:
    json_repo = json.dump(repo, f)