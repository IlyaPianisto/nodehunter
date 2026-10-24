from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Admin(Base):
    """Администраторы Web-панели"""
    __tablename__ = 'admins'

    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Client(Base):
    """Пользователи VPN (кому выдаем подписки)"""
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True)
    tg_username = Column(String(100), nullable=True)  # @username
    phone = Column(String(20), nullable=True)
    sub_token = Column(String(100), unique=True)  # Секретный токен для ссылки /sub/<token>
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class TGSession(Base):
    """Telegram-аккаунты для парсинга (добавляются из панели)"""
    __tablename__ = 'tg_sessions'

    id = Column(Integer, primary_key=True)
    phone = Column(String(20), unique=True, nullable=False)
    session_file = Column(String(255), nullable=False)  # Путь к файлу .session
    is_active = Column(Boolean, default=True)  # Участвует ли в парсинге
    status = Column(String(50), default="working")  # working, banned, sleeping


class Source(Base):
    """Источники: ТГ-каналы, сайты, Github"""
    __tablename__ = 'sources'

    id = Column(Integer, primary_key=True)
    url_or_username = Column(String(255), unique=True, nullable=False)
    source_type = Column(String(50))  # 'telegram', 'github', 'website'
    is_active = Column(Boolean, default=True)
    description = Column(Text, nullable=True)


class Node(Base):
    """Сами VPN-серверы (Outbounds)"""
    __tablename__ = 'nodes'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)  # Например: "🇳🇱 Netherlands | LTE"
    config_json = Column(JSON, nullable=False)  # Готовый Xray JSON outbound
    source_id = Column(Integer, nullable=True)  # Откуда вытащили (id из Source)

    # Статусы проверки
    status = Column(String(50), default="pending")  # pending, dead, wifi_only, bypass_rf
    ping_ms = Column(Integer, nullable=True)

    expire_date = Column(DateTime, nullable=True)  # Дата смерти (если известна)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_checked = Column(DateTime, nullable=True)


class AbuseTask(Base):
    """Инструкции 'Заабузить!' от ИИ"""
    __tablename__ = 'abuse_tasks'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)  # Название сервиса/бота
    link = Column(String(255), nullable=True)  # Ссылка t.me/...
    priority = Column(String(50), default="normal")  # today, tomorrow, normal
    description = Column(Text, nullable=True)  # Сама инструкция от Gemini
    status = Column(String(50), default="active")  # active, done, expired


class ApiKey(Base):
    """Ключи от Gemini и прочего"""
    __tablename__ = 'api_keys'

    id = Column(Integer, primary_key=True)
    service = Column(String(50), default="gemini")  # gemini, openai и т.д.
    key_value = Column(String(255), unique=True, nullable=False)
    rpm_limit = Column(Integer, default=15)  # Лимит запросов в минуту
    rpd_limit = Column(Integer, default=1500)  # Дневной лимит
    requests_today = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    last_used = Column(DateTime, nullable=True)