# Сервер лицензий karitsaDLC

Сервер создаёт аккаунты вручную, привязывает аккаунт к HWID при первом входе и
отклоняет вход с другого HWID. Пароли хранятся как PBKDF2-хеши, а клиент получает
короткую подписанную сессию на 5 минут.

Стартовый аккаунт `karitsa_009` автоматически импортируется из
`bootstrap-users.json`. В файле находится только хеш пароля, открытого пароля там нет.

## Локальная проверка

В PowerShell из папки `auth-server`:

```powershell
$env:AUTH_TOKEN_SECRET = 'замени-на-случайную-строку-длиной-больше-32-символов'
$env:AUTH_DB = "$PWD\licenses.db"
python server.py
```

Во втором PowerShell создайте покупателя:

```powershell
$env:AUTH_TOKEN_SECRET = 'та-же-секретная-строка'
$env:AUTH_DB = "$PWD\licenses.db"
python admin.py create-user buyer1
```

Сброс привязки после обращения покупателя:

```powershell
python admin.py reset-hwid buyer1
```

## VPS и HTTPS

1. Установите Docker и Docker Compose на VPS.
2. Направьте DNS-запись поддомена, например `auth.example.com`, на IP VPS.
3. Скопируйте папку `auth-server` на VPS.
4. Скопируйте `.env.example` в `.env`, укажите домен и длинный случайный секрет.
5. Выполните `docker compose up -d --build`.
6. Проверьте `https://ваш-домен/health`.

Создание пользователя на VPS:

```bash
docker compose exec auth python admin.py create-user buyer1
```

Сброс HWID:

```bash
docker compose exec auth python admin.py reset-hwid buyer1
```

Перед продажей замените `PRODUCTION_API_URL` в клиентском `AuthManager` на адрес
`https://ваш-домен/api/v1` и пересоберите JAR. Файл `.env` и базу нельзя
отправлять покупателям.
