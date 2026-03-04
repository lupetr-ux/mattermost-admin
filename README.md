# Mattermost Admin Panel

Веб-интерфейс для управления пользователями Mattermost.

## 🌟 Возможности

- **👥 Пользователи**
  - Просмотр всех пользователей
  - Создание новых пользователей
  - Редактирование имени и фамилии
  - Деактивация/активация
  - Полное удаление пользователей

- **🏢 Команды (Teams)**
  - Просмотр всех команд
  - Создание новых команд
  - Удаление команд
  - Просмотр участников команды
  - Добавление пользователей в команды

- **📢 Каналы (Channels)**
  - Просмотр всех каналов (публичных и приватных)
  - Создание новых каналов
  - Удаление каналов
  - Управление участниками каналов
  - Добавление/удаление пользователей из каналов

- **📦 Массовое создание**
  - Создание нескольких пользователей из CSV файла
  - Пример формата: `email,username,имя,фамилия,пароль`

## 🚀 Быстрый старт

### На сервере с Mattermost

1. Клонируйте репозиторий:
```bash
git clone https://github.com/lupetr-ux/mattermost-admin.git
cd mattermost-admin

2. Настройте подключение к Mattermost:
    Отредактируйте файл docker-compose.yml
    Укажите правильный MATTERMOST_HOST (обычно http://172.17.0.1:8065)
    Укажите ваш токен администратора

3.Запустите приложение
 docker-compose build
 docker-compose up -d
 
4.Откройте в браузере:
  http://IP-ВАШЕГО-СЕРВЕРА:5000
Пароль для входа: admin123

⚙️ Настройка
Получение токена администратора
bash

curl -i -X POST http://127.0.0.1:8065/api/v4/users/login \
  -H "Content-Type: application/json" \
  -d '{"login_id":"admin@aдрес сервера","password":"Admin123!"}'

Скопируйте токен из ответа (после Token:) и вставьте в docker-compose.yml
Переменные окружения
Переменная	Описание	Пример
TOKEN	Токен администратора Mattermost	r561ao5u57nnidj3cq6ynimo9c
MATTERMOST_HOST	Адрес Mattermost API	http://172.17.0.1:8065

📂 Структура проекта

mattermost-admin/
├── app.py                 # Основное приложение Flask
├── Dockerfile             # Для сборки Docker образа
├── docker-compose.yml     # Для запуска в Docker
├── requirements.txt       # Зависимости Python
├── templates/             # HTML шаблоны
│   ├── login.html         # Страница входа
│   └── index.html         # Главная страница с админкой
└── README.md              # Этот файл


🔧 Требования

    Docker и Docker Compose

    Mattermost (любая версия с API)

    Токен администратора Mattermost

📝 Лицензия

MIT
👨‍💻 Автор

lupetr-ux
