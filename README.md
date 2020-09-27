#Scoring API

## POST /method/
### Request
```
{"account": "<имя компании партнера>", "login": "<имя пользователя>", "method": "<имя метода>", "token": "<аутентификационный токен>", "arguments": {<словарь с аргументами вызываемого метода>}}
```
Arguments:
 - account: строка, опционально, может быть пустым
 - login: строка, обязательно, может быть пустым
 - method: строка, обязательно, может быть пустым
 - token: строка, обязательно, может быть пустым
 - arguments: словарь, обязательно, может быть пустым
 
### Response OK
```
{"code": <числовой код>, "response": {<ответ вызываемого метода>}}
```

### Response Error
```
{"code": <числовой код>, "error": {<сообщение об ошибке>}}
```

### Response Auth Error
```
{"code": 403, "error": "Forbidden"}
```

## Methods
### online_score
Arguments:
- phone - строка или число длиной 11 и начинается с 7. опционально, может быть пустым
- email - строка в к-ой есть @. опционально, может быть пустым
- first_name - строка, опционально, может быть пустым
- last_name - строка, опционально, может быть пустым
- birthday - дата DD.MM.YYYY с которой прошло не более 70 лет, опционально, может быть пустым
- gender - число 0, 1, 2. опционально, может быть пустым

Response:
```
{"code": 200, "response": {"score": 5.0}}
```

### clients_interests
Arguments:
- client_ids: список чисел, обязательно, не пустое
- date: дата DD.MM.YYYY, опционально, может быть пустым

Response:
```
{"client_id1": ["interest1", "interest2" ...], "client2": [...] ...}
```


### Как запускать
```sh
python api.py
```

#### Опции
  - -p - port, default = 8080
  - -l - loglevel, default = None

### Тесты
```sh
python -m unittest -v test
```