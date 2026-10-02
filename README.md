# LevelBot (Discord)

![Python](https://img.shields.io/badge/Python-3.12%2B-blue?style=for-the-badge)
![Nextcord](https://img.shields.io/badge/Nextcord-3.2.0-5865F2?style=for-the-badge)
![MySQL](https://img.shields.io/badge/MySQL-8.4-orange?style=for-the-badge)
![Discord](https://img.shields.io/badge/Discord-Leveling_Bot-5865F2?style=for-the-badge)

Ein **Discord Leveling-Bot in Python** mit XP pro Nachricht und eigenen Leveln auf jedem Server.

---

## Features

- 2 XP pro Nachricht
- Getrennter Fortschritt pro Server
- Eigene und andere Profile über `/rank` ansehen
- Speicherung in MySQL

---

## XP und Level

Start ist bei **Level 1**. Für jeden Aufstieg werden 100 XP mehr benötigt als für den vorherigen.

| Level | XP für diesen Aufstieg | Gesamt-XP |
| --- | --- | --- |
| 1 | – | 0 |
| 2 | 100 | 100 |
| 3 | 200 | 300 |
| 4 | 300 | 600 |
| 5 | 400 | 1.000 |

---

## Commands

| Command | Funktion |
| --- | --- |
| `/help` | Infos zum Bot und eine Übersicht der Commands |
| `/rank` | Eigenen Level und XP anzeigen |
| `/rank member:@Mitglied` | Level und XP eines anderen Mitglieds anzeigen |

---

## Installation

Voraussetzungen:

- Python 3.12 oder neuer
- MySQL 8.4
- Ein Discord-Bot mit Token und Zugriff auf den gewünschten Server

### 1. Repository klonen

```bash
git clone https://github.com/TillKloss/LevelBot.git
cd LevelBot
```

### 2. Python-Umgebung einrichten

```bash
python -m venv .venv
```

Unter Windows in PowerShell aktivieren:

```powershell
.\.venv\Scripts\Activate.ps1
```

Unter Linux:

```bash
source .venv/bin/activate
```

Danach die Abhängigkeiten installieren:

```bash
python -m pip install -r requirements.txt
```

### 3. Discord-Bot einrichten

Im [Discord Developer Portal](https://discord.com/developers/applications) eine Anwendung mit Bot anlegen und den Bot-Token kopieren.

Unter **Bot → Privileged Gateway Intents** die Optionen **Presence Intent**, **Server Members Intent** und **Message Content Intent** aktivieren.

Den Bot mit den Scopes `bot` und `applications.commands` auf den Server einladen. In den gewünschten Kanälen braucht er Zugriff zum Anzeigen der Kanäle sowie zum Senden von Nachrichten und Einbetten von Links.

### 4. Datenbank vorbereiten

Für eine neue Installation einmal in MySQL ausführen:

```sql
CREATE DATABASE IF NOT EXISTS level_bot
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE level_bot;

CREATE TABLE IF NOT EXISTS users (
    guild_id BIGINT UNSIGNED NOT NULL,
    user_id BIGINT UNSIGNED NOT NULL,
    xp INT NOT NULL DEFAULT 0,
    level INT NOT NULL DEFAULT 1,
    PRIMARY KEY (guild_id, user_id)
) ENGINE=InnoDB;
```

Der MySQL-Nutzer braucht die Rechte `SELECT`, `INSERT`, `UPDATE` und `CREATE` für diese Datenbank.

### 5. Zugangsdaten hinterlegen

Im Projektverzeichnis den Ordner `private` und darin eine Datei `.env` erstellen:

```dotenv
TOKEN="DEIN_DISCORD_BOT_TOKEN"
DB_HOST="127.0.0.1"
DB_PORT="3306"
DB_USER="level_bot"
DB_PASSWORD="DEIN_DATENBANK_PASSWORT"
DB_NAME="level_bot"
```

Die Werte an die eigene Datenbank anpassen. `private/.env` nicht mit ins Repository hochladen.

### 6. Bot starten

```bash
python main.py
```
