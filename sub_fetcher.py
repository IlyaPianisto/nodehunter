import asyncio
import base64
import json
import httpx

async def fetch_and_parse_subscription(url: str):
    HWID = "52353d7c-94d3-4a39-a563-d839d4c92b45"

    headers = {
        "User-Agent": "Happ/4.3.0/Windows/2309155471943",
        "x-hwid": HWID,
        "x-device-os": "Windows",
        "x-ver-os": "10.0.22631",
        "x-device-model": "Desktop",
        "Accept": "application/json, text/plain, */*",
    }

    print(f"\n[~] Стучимся по ссылке подписки с эмуляцией клиента...")

    try:
        async with httpx.AsyncClient(proxy="socks5://127.0.0.1:10808", timeout=15.0, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            raw_text = response.text.strip()

            print(f"[+] Успешно получено байт: {len(raw_text)}")

            decoded_text = raw_text
            is_base64 = False
            try:
                padding = 4 - (len(raw_text) % 4)
                padded = raw_text + ("=" * padding if padding < 4 else "")

                decoded_bytes = base64.b64decode(padded, validate=True)
                decoded_text = decoded_bytes.decode('utf-8')
                is_base64 = True
                print("[+] Контент расшифрован из Base64 (список ключей/ссылок).")
            except Exception:
                print("[~] Это не Base64, проверяем на JSON/текст...")

            try:
                json_data = json.loads(decoded_text)
                print("[+] Успешно распарсен JSON конфигурации!")

                if isinstance(json_data, dict) and "outbounds" in json_data:
                    outbounds = json_data["outbounds"]
                    print(f"[+] Найдено outbounds: {len(outbounds)} шт.")
                    return {"type": "json_singbox", "outbounds": outbounds, "raw": json_data}

                return {"type": "json_generic", "raw": json_data}

            except json.JSONDecodeError:
                lines = [line.strip() for line in decoded_text.splitlines() if line.strip()]
                print(f"[+] Найдено строк/ключей: {len(lines)}")
                return {"type": "raw_lines", "lines": lines, "raw": decoded_text}

    except Exception as e:
        print(f"[-] Ошибка при запросе подписки: {e}")
        return None


async def main():
    test_url = input("Введи ссылку на подписку: ").strip()
    if not test_url:
        print("Ссылка не введена!")
        return

    result = await fetch_and_parse_subscription(test_url)

    if result:
        print("\n" + "=" * 30 + " РЕЗУЛЬТАТ ПАРСИНГА " + "=" * 30)

        output_filename = "vpn_config.json"
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(result["raw"], f, indent=2, ensure_ascii=False)

        print(f"[+] Полный конфиг ({len(json.dumps(result['raw']))} символов) сохранен в файл: {output_filename}")
        print("[+] Теперь этот файл можно импортировать в VPN-клиент")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())