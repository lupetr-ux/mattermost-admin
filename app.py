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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
