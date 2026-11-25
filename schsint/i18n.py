"""Localized user-facing text. English is the default language."""

from __future__ import annotations

SUPPORTED_LANGUAGES = ("en", "es", "de", "ru")

TEXT = {
    "en": {
        "welcome": "Welcome to Schsint. Choose your language:",
        "ready": "Schsint is ready. Use /scan to start a permitted demo scan.",
        "help": "Schsint only runs its offline demo module right now. It does not search the web or enumerate accounts. Scans are restricted to configured admins. Commands: /scan /history /settings /delete_history.",
        "restricted": "Access denied. Ask the operator to add your Telegram ID to ADMIN_IDS.",
        "consent_prompt": "Enter the username for an account you own or are explicitly authorized to check. The current demo makes no network requests.",
        "consent": "I confirm this is my account or I have explicit permission to check it.",
        "cancel": "Cancelled.",
        "working": "Preparing a local-only demo report…",
        "done": "Demo report ready. No websites were queried and no account matches were collected.",
        "history_empty": "No scan history.",
        "history": "Recent local demo scans:",
        "settings": "Language: English. Change it with the buttons below.",
        "deleted": "Deleted {count} history record(s).",
        "invalid": "That username is invalid. Use up to 64 letters, numbers, dots, underscores or hyphens.",
        "error": "Something went wrong. Please try again later.",
    },
    "es": {
        "welcome": "Bienvenido/a a Schsint. Elige tu idioma:",
        "ready": "Schsint está listo. Usa /scan para iniciar un análisis de demostración autorizado.",
        "help": "Schsint solo ejecuta su módulo de demostración sin conexión. No busca en la web ni enumera cuentas. Los análisis están restringidos a administradores configurados. Comandos: /scan /history /settings /delete_history.",
        "restricted": "Acceso denegado. Pide al operador que añada tu ID de Telegram a ADMIN_IDS.",
        "consent_prompt": "Introduce el nombre de usuario de una cuenta propia o que tengas permiso explícito para comprobar. La demostración no realiza solicitudes de red.",
        "consent": "Confirmo que es mi cuenta o que tengo permiso explícito para comprobarla.",
        "cancel": "Cancelado.",
        "working": "Preparando un informe local de demostración…",
        "done": "Informe listo. No se consultaron sitios web ni se recopilaron coincidencias.",
        "history_empty": "No hay historial de análisis.",
        "history": "Análisis locales recientes:",
        "settings": "Idioma: español. Cámbialo con los botones.",
        "deleted": "Se eliminaron {count} registro(s) del historial.",
        "invalid": "Nombre no válido. Usa hasta 64 letras, números, puntos, guiones bajos o guiones.",
        "error": "Ha ocurrido un error. Inténtalo más tarde.",
    },
    "de": {
        "welcome": "Willkommen bei Schsint. Bitte Sprache wählen:",
        "ready": "Schsint ist bereit. Mit /scan einen autorisierten Demolauf starten.",
        "help": "Schsint führt derzeit nur das Offline-Demomodul aus. Es durchsucht nicht das Web und enumeriert keine Konten. Scans sind auf konfigurierte Admins beschränkt. Befehle: /scan /history /settings /delete_history.",
        "restricted": "Zugriff verweigert. Bitte den Betreiber, deine Telegram-ID zu ADMIN_IDS hinzuzufügen.",
        "consent_prompt": "Gib den Benutzernamen eines eigenen Kontos oder eines Kontos ein, für das du ausdrücklich berechtigt bist. Die Demo sendet keine Netzwerkanfragen.",
        "consent": "Ich bestätige, dass es mein Konto ist oder ich ausdrücklich zur Prüfung berechtigt bin.",
        "cancel": "Abgebrochen.",
        "working": "Lokalen Demobericht wird erstellt…",
        "done": "Demobericht fertig. Es wurden keine Websites abgefragt und keine Kontotreffer gesammelt.",
        "history_empty": "Kein Scan-Verlauf.",
        "history": "Letzte lokale Demoscans:",
        "settings": "Sprache: Deutsch. Mit den Schaltflächen ändern.",
        "deleted": "{count} Verlaufseinträge gelöscht.",
        "invalid": "Ungültiger Benutzername. Bis zu 64 Buchstaben, Zahlen, Punkte, Unterstriche oder Bindestriche.",
        "error": "Ein Fehler ist aufgetreten. Bitte später erneut versuchen.",
    },
    "ru": {
        "welcome": "Добро пожаловать в Schsint. Выберите язык:",
        "ready": "Schsint готов. Используйте /scan для разрешённой демо-проверки.",
        "help": "Сейчас Schsint запускает только офлайн-демомодуль. Он не ищет в интернете и не перечисляет аккаунты. Проверки доступны только администраторам из настроек. Команды: /scan /history /settings /delete_history.",
        "restricted": "Доступ запрещён. Попросите оператора добавить ваш Telegram ID в ADMIN_IDS.",
        "consent_prompt": "Введите ник собственного аккаунта или аккаунта, на проверку которого у вас есть явное разрешение. Демо не отправляет сетевые запросы.",
        "consent": "Подтверждаю, что это мой аккаунт или у меня есть явное разрешение на проверку.",
        "cancel": "Отменено.",
        "working": "Готовлю локальный демо-отчёт…",
        "done": "Демо-отчёт готов. Сайты не запрашивались, совпадения аккаунтов не собирались.",
        "history_empty": "История проверок пуста.",
        "history": "Последние локальные демо-проверки:",
        "settings": "Язык: русский. Измените его кнопками ниже.",
        "deleted": "Удалено записей истории: {count}.",
        "invalid": "Некорректный ник. Допустимо до 64 букв, цифр, точек, подчёркиваний и дефисов.",
        "error": "Произошла ошибка. Попробуйте позже.",
    },
}


def get_text(language: str, key: str, **values: object) -> str:
    language = language if language in TEXT else "en"
    return TEXT[language][key].format(**values)
