from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import requests
import json
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'mattermost-secret-key-2026')

# Настройки Mattermost из переменных окружения
MATTERMOST_HOST = os.environ.get('MATTERMOST_HOST', 'http://172.17.0.1:8065')
TOKEN = os.environ.get('TOKEN', 'r561ao5u57nnidj3cq6ynimo9c')

print(f"=== MATTERMOST ADMIN PANEL ===")
print(f"MATTERMOST_HOST: {MATTERMOST_HOST}")
print(f"TOKEN: {TOKEN[:10]}...")

# Настройки Keycloak из переменных окружения
KEYCLOAK_URL = os.environ.get('KEYCLOAK_URL', 'https://auth.alpha.kg')
KEYCLOAK_REALM = os.environ.get('KEYCLOAK_REALM', 'mattermost')
KEYCLOAK_CLIENT = os.environ.get('KEYCLOAK_CLIENT', 'admin-cli')
KEYCLOAK_SECRET = os.environ.get('KEYCLOAK_SECRET', '')

print(f"KEYCLOAK_URL: {KEYCLOAK_URL}")
print(f"KEYCLOAK_REALM: {KEYCLOAK_REALM}")
print(f"KEYCLOAK_CLIENT: {KEYCLOAK_CLIENT}")
print(f"KEYCLOAK_SECRET: {'ЗАДАН' if KEYCLOAK_SECRET else 'НЕ ЗАДАН!'}")



headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Проверка авторизации
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ==============================================
# СТРАНИЦЫ
# ==============================================

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == "admin123":
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Неверный пароль")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# ==============================================
# API: ПОЛЬЗОВАТЕЛИ
# ==============================================

@app.route('/api/users')
@login_required
def get_users():
    try:
        response = requests.get(f"{MATTERMOST_HOST}/api/v4/users?per_page=200", headers=headers, timeout=10)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": f"Ошибка {response.status_code}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users/create', methods=['POST'])
@login_required
def create_user():
    data = request.json
    payload = {
        "email": data.get('email'),
        "username": data.get('username'),
        "first_name": data.get('first_name', ''),
        "last_name": data.get('last_name', ''),
        "password": data.get('password')
    }
    
    try:
        response = requests.post(f"{MATTERMOST_HOST}/api/v4/users", headers=headers, json=payload, timeout=10)
        if response.status_code == 201:
            return jsonify(response.json())
        else:
            return jsonify({"error": response.text}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users/<user_id>/edit', methods=['PUT'])
@login_required
def edit_user(user_id):
    data = request.json
    payload = {
        "first_name": data.get('first_name'),
        "last_name": data.get('last_name')
    }
    
    try:
        response = requests.put(f"{MATTERMOST_HOST}/api/v4/users/{user_id}/patch", headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": response.text}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users/<user_id>/deactivate', methods=['DELETE'])
@login_required
def deactivate_user(user_id):
    try:
        response = requests.delete(f"{MATTERMOST_HOST}/api/v4/users/{user_id}", headers=headers, timeout=10)
        if response.status_code == 200:
            return jsonify({"success": True})
        else:
            return jsonify({"error": response.text}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users/<user_id>/delete-permanent', methods=['DELETE'])
@login_required
def delete_user_permanent(user_id):
    try:
        response = requests.delete(f"{MATTERMOST_HOST}/api/v4/users/{user_id}?permanent=true", headers=headers, timeout=10)
        if response.status_code == 200:
            return jsonify({"success": True})
        else:
            return jsonify({"error": response.text}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==============================================
# API: КОМАНДЫ (TEAMS)
# ==============================================

@app.route('/api/teams')
@login_required
def get_teams():
    try:
        response = requests.get(f"{MATTERMOST_HOST}/api/v4/teams", headers=headers, timeout=10)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": f"Ошибка {response.status_code}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/teams/create', methods=['POST'])
@login_required
def create_team():
    data = request.json
    payload = {
        "name": data.get('name'),
        "display_name": data.get('display_name'),
        "type": data.get('type', 'O')
    }
    
    try:
        response = requests.post(f"{MATTERMOST_HOST}/api/v4/teams", headers=headers, json=payload, timeout=10)
        if response.status_code == 201:
            return jsonify(response.json())
        else:
            return jsonify({"error": response.text}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/teams/<team_id>/delete', methods=['DELETE'])
@login_required
def delete_team(team_id):
    try:
        response = requests.delete(f"{MATTERMOST_HOST}/api/v4/teams/{team_id}", headers=headers, timeout=10)
        if response.status_code == 200:
            return jsonify({"success": True})
        else:
            return jsonify({"error": response.text}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/teams/add-user', methods=['POST'])
@login_required
def add_user_to_team():
    data = request.json
    payload = {
        "team_id": data.get('team_id'),
        "user_id": data.get('user_id')
    }
    
    try:
        response = requests.post(f"{MATTERMOST_HOST}/api/v4/teams/{data.get('team_id')}/members", headers=headers, json=payload, timeout=10)
        if response.status_code == 201:
            return jsonify({"success": True})
        else:
            return jsonify({"error": response.text}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/teams/<team_id>/users')
@login_required
def get_team_users(team_id):
    try:
        response = requests.get(f"{MATTERMOST_HOST}/api/v4/teams/{team_id}/members", headers=headers, timeout=10)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": f"Ошибка {response.status_code}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==============================================
# API: КАНАЛЫ (CHANNELS)
# ==============================================

@app.route('/api/teams/<team_id>/channels')
@login_required
def get_team_channels(team_id):
    try:
        # Получаем публичные каналы
        public_response = requests.get(
            f"{MATTERMOST_HOST}/api/v4/teams/{team_id}/channels", 
            headers=headers, 
            timeout=10
        )
        
        # Получаем приватные каналы
        private_response = requests.get(
            f"{MATTERMOST_HOST}/api/v4/teams/{team_id}/channels/private", 
            headers=headers, 
            timeout=10
        )
        
        all_channels = []
        
        if public_response.status_code == 200:
            public_channels = public_response.json()
            for channel in public_channels:
                channel['channel_type'] = 'public'
            all_channels.extend(public_channels)
        
        if private_response.status_code == 200:
            private_channels = private_response.json()
            for channel in private_channels:
                channel['channel_type'] = 'private'
            all_channels.extend(private_channels)
        
        return jsonify(all_channels)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/channels/create', methods=['POST'])
@login_required
def create_channel():
    data = request.json
    payload = {
        "team_id": data.get('team_id'),
        "name": data.get('name'),
        "display_name": data.get('display_name'),
        "type": data.get('type', 'O'),
        "purpose": data.get('purpose', ''),
        "header": data.get('header', '')
    }
    
    try:
        response = requests.post(f"{MATTERMOST_HOST}/api/v4/channels", headers=headers, json=payload, timeout=10)
        if response.status_code == 201:
            return jsonify(response.json())
        else:
            return jsonify({"error": response.text}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/channels/<channel_id>/delete', methods=['DELETE'])
@login_required
def delete_channel(channel_id):
    try:
        response = requests.delete(f"{MATTERMOST_HOST}/api/v4/channels/{channel_id}", headers=headers, timeout=10)
        if response.status_code == 200:
            return jsonify({"success": True})
        else:
            return jsonify({"error": response.text}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/channels/add-user', methods=['POST'])
@login_required
def add_user_to_channel():
    data = request.json
    payload = {
        "user_id": data.get('user_id')
    }
    
    try:
        response = requests.post(f"{MATTERMOST_HOST}/api/v4/channels/{data.get('channel_id')}/members", headers=headers, json=payload, timeout=10)
        if response.status_code == 201:
            return jsonify({"success": True})
        else:
            return jsonify({"error": response.text}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/channels/<channel_id>/users')
@login_required
def get_channel_users(channel_id):
    try:
        response = requests.get(f"{MATTERMOST_HOST}/api/v4/channels/{channel_id}/members", headers=headers, timeout=10)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": f"Ошибка {response.status_code}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/channels/<channel_id>/remove-user/<user_id>', methods=['DELETE'])
@login_required
def remove_user_from_channel(channel_id, user_id):
    try:
        response = requests.delete(f"{MATTERMOST_HOST}/api/v4/channels/{channel_id}/members/{user_id}", headers=headers, timeout=10)
        if response.status_code == 200:
            return jsonify({"success": True})
        else:
            return jsonify({"error": response.text}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==============================================
# KEYCLOAK ФУНКЦИИ
# ==============================================

# ==============================================
# KEYCLOAK ФУНКЦИИ - УПРОЩЕННАЯ ВЕРСИЯ
# ==============================================

def get_keycloak_token():
    """Получение токена для доступа к Keycloak API"""
    try:
        url = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token"
        print(f"🔄 Получение токена из: {url}")
        
        data = {
            'client_id': KEYCLOAK_CLIENT,
            'client_secret': KEYCLOAK_SECRET,
            'grant_type': 'client_credentials'
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        response = requests.post(url, headers=headers, data=data, timeout=10)
        
        print(f"📊 Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Токен получен!")
            return token_data.get('access_token')
        else:
            print(f"❌ Ошибка: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Исключение: {str(e)}")
        return None

@app.route('/api/keycloak/users')
@login_required
def get_keycloak_users():
    """Получить список пользователей из Keycloak"""
    print("="*50)
    print("Запрос списка пользователей из Keycloak")
    
    token = get_keycloak_token()
    if not token:
        print("❌ Не удалось получить токен")
        return jsonify({"error": "Не удалось получить токен Keycloak"}), 500
    
    try:
        url = f"{KEYCLOAK_URL}/admin/realms/{KEYCLOAK_REALM}/users"
        print(f"📡 Запрос к: {url}")
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        print(f"📊 Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            users = response.json()
            print(f"✅ Получено пользователей: {len(users)}")
            
            formatted_users = []
            for user in users:
                formatted_users.append({
                    'id': user.get('id'),
                    'username': user.get('username'),
                    'email': user.get('email'),
                    'first_name': user.get('firstName', ''),
                    'last_name': user.get('lastName', ''),
                    'enabled': user.get('enabled', False)
                })
            return jsonify(formatted_users)
        else:
            print(f"❌ Ошибка: {response.text}")
            return jsonify({"error": f"Ошибка Keycloak: {response.status_code}"}), 500
            
    except Exception as e:
        print(f"❌ Исключение: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/keycloak/sync', methods=['POST'])
@login_required
def sync_keycloak_users():
    """Синхронизировать пользователей из Keycloak с Mattermost"""
    print("="*50)
    print("Запрос синхронизации пользователей")
    
    token = get_keycloak_token()
    if not token:
        return jsonify({"error": "Не удалось получить токен Keycloak"}), 500
    
    try:
        # Получаем пользователей из Keycloak
        url = f"{KEYCLOAK_URL}/admin/realms/{KEYCLOAK_REALM}/users"
        headers_kc = {'Authorization': f'Bearer {token}'}
        
        response = requests.get(url, headers=headers_kc, timeout=10)
        if response.status_code != 200:
            return jsonify({"error": f"Ошибка Keycloak: {response.status_code}"}), 500
        
        keycloak_users = response.json()
        print(f"📥 Получено {len(keycloak_users)} пользователей из Keycloak")
        
        # Получаем пользователей из Mattermost (используем headers, а не headers_mm)
        mm_response = requests.get(
            f"{MATTERMOST_HOST}/api/v4/users?per_page=200",
            headers=headers,  # ← ИСПРАВЛЕНО!
            timeout=10
        )
        
        if mm_response.status_code != 200:
            return jsonify({"error": "Не удалось получить пользователей из Mattermost"}), 500
        
        mattermost_users = mm_response.json()
        print(f"📥 Получено {len(mattermost_users)} пользователей из Mattermost")
        
        # Создаем словарь пользователей Mattermost по email
        mm_users_by_email = {}
        for u in mattermost_users:
            if u.get('email'):
                mm_users_by_email[u['email'].lower()] = u
        
        results = {
            'created': [],
            'updated': [],
            'skipped': [],
            'errors': []
        }
        
        # Обрабатываем каждого пользователя из Keycloak
        for kc_user in keycloak_users:
            email = kc_user.get('email', '').lower()
            username = kc_user.get('username')
            first_name = kc_user.get('firstName', '')
            last_name = kc_user.get('lastName', '')
            
            if not email:
                results['skipped'].append({
                    'username': username,
                    'reason': 'Нет email'
                })
                continue
            
            if email in mm_users_by_email:
                # Пользователь существует - проверяем, нужно ли обновить
                mm_user = mm_users_by_email[email]
                needs_update = False
                
                if mm_user.get('first_name', '') != first_name:
                    needs_update = True
                if mm_user.get('last_name', '') != last_name:
                    needs_update = True
                
                if needs_update:
                    update_response = requests.put(
                        f"{MATTERMOST_HOST}/api/v4/users/{mm_user['id']}/patch",
                        headers=headers,  # ← ИСПРАВЛЕНО!
                        json={
                            'first_name': first_name,
                            'last_name': last_name
                        },
                        timeout=10
                    )
                    
                    if update_response.status_code == 200:
                        results['updated'].append({
                            'email': email,
                            'username': username,
                            'first_name': first_name,
                            'last_name': last_name
                        })
                    else:
                        results['errors'].append({
                            'email': email,
                            'error': 'Ошибка обновления'
                        })
                else:
                    results['skipped'].append({
                        'email': email,
                        'username': username,
                        'reason': 'Данные актуальны'
                    })
            else:
                # Пользователя нет - создаем нового
                import random
                import string
                temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
                
                create_data = {
                    'email': email,
                    'username': username,
                    'first_name': first_name,
                    'last_name': last_name,
                    'password': temp_password
                }
                
                create_response = requests.post(
                    f"{MATTERMOST_HOST}/api/v4/users",
                    headers=headers,  # ← ИСПРАВЛЕНО!
                    json=create_data,
                    timeout=10
                )
                
                if create_response.status_code == 201:
                    results['created'].append({
                        'email': email,
                        'username': username,
                        'first_name': first_name,
                        'last_name': last_name
                    })
                else:
                    results['errors'].append({
                        'email': email,
                        'error': f"Ошибка создания: {create_response.text}"
                    })
        
        print(f"✅ Синхронизация завершена: создано {len(results['created'])}, обновлено {len(results['updated'])}")
        return jsonify(results)
        
    except Exception as e:
        print(f"❌ Ошибка синхронизации: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
