# searxng-mcp-lite

Минимальный MCP-сервер в одном файле: инструмент `web_search` через ваш
локальный SearXNG. Только официальный MCP Python SDK (`mcp`) + httpx — без
сторонних обёрток, авторизации и лишних зависимостей.

## Требования

- Python >= 3.10
- Запущенный SearXNG с включённым JSON-форматом (`search.formats: [html, json]`)
  и выключенным лимитером (`server.limiter: false`), если доступ нужен из сети.

## Установка

```bash
git clone https://github.com/<USER>/searxng-mcp-lite.git
cd searxng-mcp-lite
uv venv --python 3.12 .venv          # или: python3 -m venv .venv
uv pip install -r requirements.txt  # или: .venv/bin/pip install -r requirements.txt
```

## Запуск

```bash
SEARXNG_URL=http://127.0.0.1:8080 .venv/bin/python server.py --host 0.0.0.0 --port 8765
```

- `SEARXNG_URL` — адрес SearXNG (по умолчанию `http://127.0.0.1:8080`)
- `--host` / `--port` — адрес прослушивания (можно через `MCP_HOST` / `MCP_PORT`)

Сервер отдаёт Streamable HTTP MCP на пути `/mcp`.

## Подключение клиента

В конфиге MCP-клиента (Claude Desktop, Open WebUI и т.п.):

```json
{
  "mcpServers": {
    "searxng": {
      "url": "http://<HOST>:8765/mcp"
    }
  }
}
```

## Инструмент

| Инструмент | Параметры |
|---|---|
| `web_search` | `query` (обязательный), `categories`, `language`, `pageno` |

Возвращает JSON: `number_of_results` + список `{title, url, content, engine}`.

## Windows

Обёртка — чистый Python, работает на Windows без изменений.

**Как клиент** (обычный случай): ничего устанавливать не нужно — в MCP-клиенте
укажите URL сервера, например `http://<SEARXNG_HOST>:8765/mcp`.

**Запуск обёртки на Windows:**

```powershell
git clone https://github.com/strikebox/searxng-mcp-lite.git
cd searxng-mcp-lite
uv venv --python 3.12 .venv
.venv\Scripts\pip install -r requirements.txt
$env:SEARXNG_URL="http://<SEARXNG_HOST>:8080"
.venv\Scripts\python server.py --host 0.0.0.0 --port 8765
```

Нюансы:
- при первом запуске разрешите доступ в сети в брандмауэре Windows;
- для автозапуска вместо systemd — Планировщик заданий или NSSM.

## systemd (пример)

```ini
[Unit]
Description=SearXNG MCP lite server
After=network-online.target docker.service

[Service]
User=strike
WorkingDirectory=/opt/searxng-mcp-lite
Environment=SEARXNG_URL=http://127.0.0.1:8080
ExecStart=/opt/searxng-mcp-lite/.venv/bin/python /opt/searxng-mcp-lite/server.py --host 0.0.0.0 --port 8765
Restart=always

[Install]
WantedBy=multi-user.target
```

## Лицензия

MIT
