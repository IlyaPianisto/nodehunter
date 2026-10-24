from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    stats = {
        'cpu': '30%', 'ram': '45%', 'ssd': '60%',
        'servers_total': 24, 'servers_wifi': 14, 'servers_lte': 10,
        'active_nodes': '51/75', 'checker_status': 'active (5 days)'
    }

    # Полный список всех найденных абузов с подробными инструкциями
    all_tasks = [
        {'id': 1, 'link': 't.me/vpn_bot1', 'priority': 'сегодня', 'desc': 'Нажать старт, получить 5гб',
         'full_desc': '1. Перейди в бота.\n2. Подпишись на 3 спонсорских канала.\n3. Нажми кнопку "Получить бонус".\n4. Бот выдаст vless ключ на 5 ГБ, скопируй его.'},
        {'id': 2, 'link': 't.me/free_vpn2', 'priority': 'сегодня', 'desc': 'Переслать промокод',
         'full_desc': 'Скопируй промокод FREE2026. Открой их приложение, зайди в настройки и введи код. Дадут месяц премиума.'},
        {'id': 3, 'link': 't.me/proxy_3', 'priority': 'завтра', 'desc': 'Зарегать новый акк',
         'full_desc': 'Включи любой рабочий VPN. Зайди на их сайт через инкогнито, используй временную почту (temp-mail). Зарегай аккаунт, скопируй URL подписки.'},
        {'id': 4, 'link': 't.me/vpn_drop_4', 'priority': 'на неделе', 'desc': 'Сбор ключей',
         'full_desc': 'Канал постит пачки ключей раз в неделю. Нужно просто зайти и скопировать последний пост.'},
        {'id': 5, 'link': 'github.com/free-nodes', 'priority': 'когда-нибудь', 'desc': 'Форкнуть репозиторий',
         'full_desc': 'Перейти по ссылке, открыть файл nodes.txt, там лежит base64 строка. Раскодировать не нужно, просто вставить в парсер.'}
    ]

    # На главной показываем только первые 3 (самые срочные)
    tasks = all_tasks[:3]

    return render_template('index.html', stats=stats, tasks=tasks, all_tasks=all_tasks)


@app.route('/users')
def users():
    users_data = [
        {'id': 214, 'username': 'pians4u228', 'status': 'active', 'expire': '∞', 'created': '21.10.26 17:00', 'last_conn': '22.10.26 00:00'},
        {'id': 305, 'username': 'drop_hunter', 'status': 'expired', 'expire': '22.10.26 17:00', 'created': '15.09.26 12:00', 'last_conn': '22.10.26 16:55'},
        {'id': 89, 'username': 'test_client', 'status': 'active', 'expire': '01.01.27 12:00', 'created': '24.10.26 09:00', 'last_conn': '-'}
    ]
    return render_template('users.html', users=users_data)


@app.route('/hosts')
def hosts():
    # Теперь передаем и "цель" (target), и реальное количество (actual)
    stats = {
        'target_regular': 150,
        'actual_regular': 158,
        'target_lte': 100,
        'actual_lte': 107
    }

    templates = ['default', 'bypass_dpi', 'shadowsocks_only', 'vless_reality']

    hosts_data = [
        {'id': 1, 'name': '🇳🇱 Netherlands | U', 'template': 'default', 'expire': '25.09.2027 16:00', 'status': 'active',
         'ping': '45ms'},
        {'id': 2, 'name': '🇵🇱 LTE | Poland', 'template': 'bypass_dpi', 'expire': '12.06.2027 10:00', 'status': 'active',
         'ping': '112ms'},
        {'id': 3, 'name': '🇩🇪 Germany | Main', 'template': 'default', 'expire': '01.01.2028 00:00',
         'status': 'disabled', 'ping': 'timeout'},
        {'id': 4, 'name': '🇺🇸 USA | Free', 'template': 'vless_reality', 'expire': '15.11.2026 12:00',
         'status': 'active', 'ping': '180ms'},
    ]

    return render_template('hosts.html', stats=stats, hosts=hosts_data, templates=templates)

@app.route('/tg_users_settings')
def tg_users_settings():
    # Фейковые данные юзеров
    tg_users = [
        {'id': 1, 'username': '@p_ivanov', 'phone': '+79865259781', 'status': 'Парсит', 'abused': 25},
        {'id': 2, 'username': '@drop_hunter', 'phone': '+79991234567', 'status': 'Спит', 'abused': 12}
    ]

    # Фейковые папки и чаты для мини-мессенджера
    chat_folders = ['Все', 'Новые', 'Боты', 'Абуз VPN']

    chats = [
        {'name': 'VPN Bot Free', 'last_msg': 'Ваш промокод: XYZ...', 'is_bot': True, 'active': True},
        {'name': 'Халява ТГ', 'last_msg': 'Новые ключи vless!', 'is_bot': False, 'active': False},
        {'name': 'Proxy Robot', 'last_msg': 'Выберите сервер', 'is_bot': True, 'active': False},
    ]

    return render_template('tg_users_settings.html', tg_users=tg_users, chats=chats, folders=chat_folders)


@app.route('/settings')
def settings():
    admins = [
        {'id': 1, 'login': 'pians4u228', 'date': '21.08.26 17:00'},
        {'id': 2, 'login': 'PPR_Zik', 'date': '27.02.26 13:00'}
    ]

    xray_templates = ['default', 'for_obxod_w', 'dns_obxod']

    checkers = [
        {'id': 1, 'name': 'Huawei Y6', 'date': '25.07.26 17:00', 'status': 'active'}
    ]

    config = {
        'admin_path': 'squezi/app/13667/q',
        'sub_path': 'api/sub/xyz/q/hu',
        'tg_bot_api': '123456789:ABCdefGHIjklMNOpqrsTUVwxyz'
    }

    return render_template('settings.html', admins=admins, templates=xray_templates, checkers=checkers, config=config)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')


if __name__ == '__main__':
    app.run(debug=True, port=5000)