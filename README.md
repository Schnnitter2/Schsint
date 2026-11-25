# Schsint

**Schsint** is a privacy-first, open-source project scaffold for permitted public-information research. The Telegram bot defaults to English and supports Spanish, German, and Russian, with persistent per-user language selection.

> **Current release is an offline-only MVP.** It does not query websites, enumerate accounts, bypass privacy settings, discover hidden accounts, or infer identity. No Maigret, Sherlock, or WhatsMyName adapter is enabled. Never treat a matching username as proof that accounts belong to one person.

## What is implemented

- Async plugin engine with bounded concurrent scans, progress events, failure isolation, and canonical URL deduplication.
- Pydantic request/result contracts; explicit authorization confirmation and username validation.
- Aiogram 3 bot: `/start`, `/help`, `/scan`, `/history`, `/settings`, `/delete_history`; English, Español, Deutsch, Русский.
- Scan/history commands require Telegram IDs configured in `ADMIN_IDS`; empty allowlist denies access. In-memory per-user rate limit.
- SQLite with SQLAlchemy 2 async: scan/module history and selected language. A user can delete their own scan history.
- Self-contained, responsive dark HTML report with escaped template values, confidence/limitations, source/module status, and no external assets; JSON serialization is provided in the report API.
- Docker image runs as non-root with read-only root filesystem and dropped capabilities.
- Offline tests for engine failure behavior, deduplication, consent, reporting, and localization.

## Quick start

Requires Python 3.12+ and a Telegram bot token.

```bash
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env: set BOT_TOKEN and your numeric Telegram ID in ADMIN_IDS
python main.py
```

In Telegram, send `/start`, choose a language, and use `/scan`. The produced HTML document is a local demo report; no username checks are made. Use `/history` to see your own scan history and `/delete_history` to delete it. Settings are available with `/settings`.

### Docker Compose

```bash
cp .env.example .env
# Configure BOT_TOKEN and ADMIN_IDS in .env
docker compose up --build -d
```

Persistent SQLite data is stored in the `schsint-data` Docker volume. Protect `.env` and the volume. The bot uses polling; only one replica should run per bot token.

## Tests

```bash
pip install -r requirements.txt
pytest -q
```

Tests have not been run as part of this repository change; run them in a Python 3.12 environment after installing requirements.

## Source research and integration policy

Reviewed official repositories and their docs/licenses on 2026-11-25:

- [Maigret](https://github.com/soxoj/maigret): active; MIT. Its README documents CLI, JSON/NDJSON and HTML/PDF outputs, and async library use. Its wide account enumeration, recursive search and anti-blocking features need a distinct safety and privacy review; Schsint does not invoke it.
- [Sherlock](https://github.com/sherlock-project/sherlock): active; MIT. Its documentation describes CLI username searches and JSON output. Schsint does not invoke it.
- [WhatsMyName](https://github.com/WebBreacher/WhatsMyName): archived according to its README dated 2026-11-09; final dataset CC BY-SA 4.0 and explicitly warned to become less accurate. Schsint does not download, bundle, or auto-update that dataset.

The project intentionally does not implement unrestricted username enumeration. Any future source integration must be independently reviewed, respect site terms and privacy controls, avoid circumvention/recursive discovery, use explicit bounded requests, and present results only as unverified public leads. Dataset updates must verify provenance and licensing; no automatic updater is currently present.

## Security and privacy notes

- Set an allowlist of trusted admin Telegram IDs; do not expose the bot publicly with a broad allowlist.
- Telegram IDs, usernames, scan summaries, and language preferences are stored locally. `/delete_history` removes scan/module history but not language preference. Back up or delete the Docker data volume accordingly.
- Rate limiting is process-local and resets on restart; it is not a distributed abuse-control system.
- This project is an MVP, not a production security certification. Add retention policies, operational monitoring, deployment secrets management, and review before production use.

## Roadmap

- Add an explicit retention/expiry policy and tests for data deletion.
- Add optional JSON file delivery and safe report-size handling.
- Consider user-owned / explicitly authorized source adapters only after legal, license, privacy, and technical review; do not add identity resolution or privacy bypass.
- Add CI, migrations, and operational metrics before production deployments.

## License

No project license has been selected yet. Do not assume third-party source licenses apply to Schsint.
