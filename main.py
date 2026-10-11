import asyncio
import os
import time
from dotenv import load_dotenv
from telethon import TelegramClient
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
GEMINI_KEY = os.getenv("GEMINI_KEY")

ai_client = genai.Client(
    api_key=GEMINI_KEY,
    http_options=types.HttpOptions(
        client_args={'proxy': 'socks5://127.0.0.1:10808'},
        async_client_args={'proxy': 'socks5://127.0.0.1:10808'}
    )
)
client = TelegramClient('session_test', API_ID, API_HASH)


# Схема JSON-ответа
class VpnResult(BaseModel):
    has_vpn: bool = Field(description="True, если найдены VPN-ключи, промокоды или боты, иначе False")
    vpn_bots: list[str] = Field(default_factory=list, description="Список ссылок на Telegram-ботов (t.me/...)")
    promo_codes: list[str] = Field(default_factory=list, description="Список промокодов")
    config_keys: list[str] = Field(default_factory=list, description="Список конфигурационных ключей (vless://, ss:// и т.д.)")
    subscription_links: list[str] = Field(default_factory=list, description="Список ссылок на подписки v2ray/clash/sing-box")
    instructions: list[str] = Field(default_factory=list, description="Если нужно что-то заабузить, то здесь все инструкции, что надо делать.")


async def analyze_with_gemini(text, max_retries=3):
    prompt = f"""
    Проанализируй текст сообщения из Telegram-канала и извлеки VPN-данные:
    ---
    {text}
    ---
    """

    for attempt in range(1, max_retries + 1):
        print(f"Отправка запроса в Gemini (Попытка {attempt}/{max_retries})...")
        start_time = time.time()
        try:
            response = await ai_client.aio.models.generate_content(
                model='gemini-3.1-flash-lite',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=VpnResult,
                )
            )
            print(f"Ответ получен за {time.time() - start_time:.2f} сек.")
            return response.text

        except Exception as e:
            err_msg = str(e)
            print(f"Ошибка на попытке {attempt}: {err_msg}")

            if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                print("Превышен лимит API (429). Ждем 30 секунд...")
                await asyncio.sleep(30)
            else:
                await asyncio.sleep(3)

    print("Не удалось получить ответ от Gemini после всех попыток.")
    return None


async def main():
    await client.start()
    print("Telethon успешно запущен!")

    channel_username = 'vpndrops'

    async for message in client.iter_messages(channel_username, limit=50):
        if message.text:
            print(f"\n--- Сообщение ID {message.id} ---")
            print(f"Содержание сообщения: {message.text}")
            json_result = await analyze_with_gemini(message.text)
            print(f"JSON от Gemini:\n{json_result}")

        await asyncio.sleep(4)

with client:
    client.loop.run_until_complete(main())