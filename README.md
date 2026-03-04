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
  -d '{"login_id":"Email админа","password":"пароль админа"}'

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

## 🌿 Версии проекта

### main (стабильная версия)
Базовая админка Mattermost без Keycloak.

### feature/keycloak-integration (с Keycloak)
Версия с интеграцией Keycloak для синхронизации пользователей.

**Использование версии с Keycloak:**
```bash
git clone https://github.com/lupetr-ux/mattermost-admin.git
cd mattermost-admin
git checkout feature/keycloak-integration

## 🔑 Интеграция с Keycloak

Эта версия поддерживает синхронизацию пользователей из Keycloak с Mattermost.

### Настройка Keycloak (пошагово)

#### Шаг 1: Создайте клиента в Keycloak

1. Войдите в админку Keycloak (https://auth.alpha.kg/admin)
2. Выберите ваш realm (например, `mattermost`)
3. В левом меню перейдите в **Clients**
4. Нажмите **Create client**

![Создание клиента](screenshots/keycloak-create-client.png)

**Настройки клиента:**

| Вкладка | Поле | Значение |
|---------|------|----------|
| **General** | Client ID | `mattermost-admin-api` |
| | Name | `Mattermost Admin API` |
| | Description | `Для синхронизации с админкой` |
| **Capability config** | Client authentication | **ON** |
| | Authorization | OFF |
| | Service accounts roles | **ON** |
| | Standard flow | OFF |
| | Direct access grants | OFF |
| **Login settings** | Root URL | (оставить пустым) |
| | Valid redirect URIs | (оставить пустым) |

![Настройки клиента](screenshots/keycloak-client-settings.png)

#### Шаг 2: Настройте Service Account Roles

1. После создания клиента перейдите на вкладку **Service account roles**
2. В разделе **Client Roles** выберите **realm-management**
3. В списке **Available Roles** найдите и добавьте:
   - ✅ `view-users` (просмотр пользователей)
   - ✅ `query-users` (поиск пользователей)
   - ✅ `view-realm` (просмотр realm)
   - ✅ `query-groups` (опционально)

![Service account roles](screenshots/keycloak-service-roles.png)

4. Нажмите **Add selected**

#### Шаг 3: Получите Client Secret

1. Перейдите на вкладку **Credentials**
2. Нажмите кнопку **Regenerate** (если нужно)
3. **Скопируйте Client Secret** (длинная строка)

![Client Secret](screenshots/keycloak-credentials.png)

### Настройка приложения

#### Шаг 4: Добавьте переменные в docker-compose.yml

Отредактируйте файл `docker-compose.yml` и добавьте секцию `environment`:

```yaml
services:
  webapp:
    build: .
    container_name: mattermost-admin
    restart: always
    ports:
      - "5000:5000"
    environment:
      # Mattermost
      - TOKEN=ваш_токен_mattermost
      - MATTERMOST_HOST=http://172.17.0.1:8065
      
      # Keycloak (ЗАМЕНИТЕ НА СВОИ ЗНАЧЕНИЯ)
      - KEYCLOAK_URL=https://адрес сервераkeycloak
      - KEYCLOAK_REALM=mattermost
      - KEYCLOAK_CLIENT=mattermost-admin-api
      - KEYCLOAK_SECRET=вставьте_скопированный_секрет_сюда



📝 Лицензия
MIT
👨‍💻 Автор
lupetr-ux
