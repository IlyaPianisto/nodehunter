import asyncio
import base64
import binascii
import json
import os
import httpx

PROXY = "socks5://127.0.0.1:10808"
HWID = "52353d7c-94d3-4a39-a563-d839d4c92a45"

OUTPUT_DIR = "configs"
JSON_OUTPUT = "vpn_config.json"
TEXT_OUTPUT = "vpn_links.txt"

def try_decode_base64(text: str):
    """Возвращает расшифрованный текст или None, если это не Base64."""
    compact = "".join(text.split())
    normalized = compact.replace("-", "+").replace("_", "/")
    normalized += "=" * (-len(normalized) % 4)
    try:
        return base64.b64decode(normalized, validate=True).decode("utf-8")
    except (binascii.Error, UnicodeDecodeError, ValueError):
        return None

def parse_content(raw_text: str) -> dict:
    """Определяет формат ответа: JSON (sing-box / generic) или список ссылок."""
    decoded = try_decode_base64(raw_text)
    was_base64 = decoded is not None
    if was_base64:
        print("[+] Контент расшифрован из Base64.")
        text = decoded
    else:
        print("[~] Это не Base64, проверяем на JSON/текст...")
        text = raw_text

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = None

    if isinstance(data, (dict, list)):
        print("[+] Успешно распарсен JSON конфигурации!")
        if isinstance(data, dict) and "outbounds" in data:
            print(f"[+] Найдено outbounds: {len(data['outbounds'])} шт.")
            return {"type": "json_singbox", "data": data}
        return {"type": "json_generic", "data": data}

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    print(f"[+] Найдено строк/ключей: {len(lines)}")
    return {"type": "raw_lines", "lines": lines, "was_base64": was_base64}

async def fetch_and_parse_subscription(url: str):
    headers = {
        "User-Agent": "Happ/4.3.0/Windows/2309155471943",
        "x-hwid": HWID,
        "x-device-os": "Windows",
        "x-ver-os": "10.0.22631",
        "x-device-model": "Desktop",
        "Accept": "application/json, text/plain, */*",
    }

    print("\n[~] Стучимся по ссылке подписки с эмуляцией клиента...")

    try:
        async with httpx.AsyncClient(proxy=PROXY, timeout=15.0, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            raw_text = response.text.strip()

            print(f"[+] Статус: {response.status_code}, получено символов: {len(raw_text)}")
            for name in ("profile-title", "subscription-userinfo", "content-type"):
                if name in response.headers:
                    print(f"    {name}: {response.headers[name]}")

            return parse_content(raw_text)

    except Exception as e:
        print(f"[-] Ошибка при запросе подписки: {e}")
        return None

def unique_path(path: str) -> str:
    """Если файл уже есть, добавляет -2, -3 и т.д. перед расширением."""
    if not os.path.exists(path):
        return path
    base, ext = os.path.splitext(path)
    n = 2
    while os.path.exists(f"{base}-{n}{ext}"):
        n += 1
    return f"{base}-{n}{ext}"

def save_result(result: dict) -> str:
    """JSON сохраняем в .json, всё остальное (ссылки) в .txt. Существующие файлы не перезаписываем."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if result["type"].startswith("json"):
        filename = unique_path(os.path.join(OUTPUT_DIR, JSON_OUTPUT))
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(result["data"], f, indent=2, ensure_ascii=False)
        return filename

    filename = unique_path(os.path.join(OUTPUT_DIR, TEXT_OUTPUT))
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(result["lines"]) + "\n")
    return filename

async def main():
    test_url = input("Введи ссылку на подписку: ").strip()
    if not test_url:
        print("Ссылка не введена!")
        return

    result = await fetch_and_parse_subscription(test_url)
    if not result:
        return

    print("\n" + "=" * 30 + " РЕЗУЛЬТАТ ПАРСИНГА " + "=" * 30)
    filename = save_result(result)

    if result["type"].startswith("json"):
        print(f"[+] JSON-конфиг ({result['type']}) сохранён в файл: {filename}")
    else:
        source = "Base64" if result["was_base64"] else "обычный текст"
        print(f"[+] Список ссылок ({len(result['lines'])} шт., источник: {source}) сохранён в файл: {filename}")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())