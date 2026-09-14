# OpenCode Telegram Bot

Telegram-бот для управления OpenCode-агентами, YouGile и фокусом.

## Деплой на Railway (бесплатно, 2 минуты)

### Шаг 1: Создайте GitHub-репозиторий

1. Зайдите на [github.com](https://github.com)
2. Нажмите **"New"** (кнопка вверху справа)
3. Введите имя: `opencode-bot`
4. Нажмите **"Create repository"**
5. Нажмите **"uploading an existing file"**
6. Перетащите все файлы из папки проекта (кроме `bot_config.json` и `__pycache__`)
7. Нажмите **"Commit changes"**

### Шаг 2: Зарегистрируйтесь на Railway

1. Зайдите на [railway.app](https://railway.app)
2. Нажмите **"Login"**
3. Войдите через GitHub

### Шаг 3: Разверните бота

1. Нажмите **"New Project"**
2. Выберите **"Deploy from GitHub repo"**
3. Выберите ваш репозиторий `opencode-bot`
4. Railway автоматически установит зависимости и запустит бота

### Шаг 4: Настройте токен

1. В проекте Railway нажмите на **"Variables"**
2. Добавьте переменную: `bot_token` = ваш токен от @BotFather
3. Бот перезапустится автоматически

### Шаг 5: Проверьте

1. Откройте Telegram на телефоне
2. Найдите вашего бота
3. Нажмите **/start**

## Управление через телефон

| Команда | Действие |
|---------|----------|
| `/start` | Главное меню |
| Кнопка **🎯 Фокус** | Управление задачами |
| Кнопка **📋 YouGile** | Задачи в YouGile |
| Кнопка **🤖 OpenCode** | Запуск/остановка агентов |

## Локальная разработка

```bash
pip install -r requirements.txt
python bot.py
```
