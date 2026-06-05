# ⚡ Метална База Данни — Docker Compose Project

Каталог за **Thrash** и **Death Metal** албуми, изграден с Flask API + Nginx фронтенд, контейнеризиран с Docker Compose.

---

## Структура на проекта

```
metal-db/
├── compose.yml              # Docker Compose конфигурация
├── README.md
├── backend/
│   ├── Dockerfile           # Python/Flask образ
│   ├── requirements.txt
│   ├── app.py               # REST API (Flask + SQLite)
│   └── entrypoint.sh        # Стартиращ скрипт
└── frontend/
    ├── Dockerfile           # Nginx образ
    ├── nginx.conf           # Reverse proxy конфигурация
    └── index.html           # Single-page приложение
```

---

## Компоненти

### 🔴 Backend (Flask API)
- **Образ:** `python:3.12-alpine`
- **Порт:** `5000` (вътрешен)
- **Технологии:** Flask, Gunicorn, SQLite
- **Функции:**
  - `GET  /api/albums` — списък с всички/филтрирани албуми
  - `POST /api/albums` — добавяне на нов албум
  - `DELETE /api/albums/:id` — изтриване на албум
  - `GET  /api/stats` — статистика (общо, thrash, death)
  - `GET  /api/health` — health check
- Базата данни се съхранява в Docker **volume** (`db_data:/data/albums.db`)
- При първо стартиране се зарежда с 20 класически албума

### 🌐 Frontend (Nginx)
- **Образ:** `nginx:alpine`
- **Порт:** `8080` (публичен)
- **Технологии:** HTML, CSS, Vanilla JS
- Nginx изпълнява ролята на **reverse proxy** — заявките към `/api/*` се препращат към `backend:5000`
- Single-page приложение с филтриране по жанр и форма за добавяне

---

## Комуникация между услугите

```
Браузър (порт 8080)
       │
       ▼
  ┌─────────────┐
  │   frontend  │  nginx:alpine
  │  (nginx)    │  порт 80 вътрешно
  └──────┬──────┘
         │ /api/* → proxy_pass
         ▼
  ┌─────────────┐
  │   backend   │  python:alpine
  │  (gunicorn) │  порт 5000 вътрешно
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐
  │  db_data    │  Docker Volume
  │  albums.db  │  (SQLite файл)
  └─────────────┘
```

Двата контейнера са в обща мрежа `metal-net` (bridge). Фронтендът **никога** не е директно достъпен от задния слой — всичко минава през Nginx.

---

## Изграждане и стартиране

### Изисквания
- Docker >= 24.x
- Docker Compose >= 2.x

### Стартиране

```bash
# Клониране на хранилището
git clone https://github.com/<YOUR_USERNAME>/metal-db.git
cd metal-db

# Изграждане и стартиране на контейнерите
docker compose up --build -d

# Отвори браузър на:
# http://localhost:8080
```

### Спиране

```bash
docker compose down
```

### Спиране и изтриване на данните

```bash
docker compose down -v
```

### Преглед на логове

```bash
docker compose logs -f backend
docker compose logs -f frontend
```

---

## Публикуване на образите в Docker Hub

```bash
# Вход в Docker Hub
docker login

# Билд с таг към твоя профил
docker build -t <USERNAME>/metal-db-backend:latest ./backend
docker build -t <USERNAME>/metal-db-frontend:latest ./frontend

# Качване
docker push <USERNAME>/metal-db-backend:latest
docker push <USERNAME>/metal-db-frontend:latest
```

---

## Използване на готови образи от Docker Hub

В `compose.yml` замени `build:` секциите с:

```yaml
backend:
  image: <USERNAME>/metal-db-backend:latest

frontend:
  image: <USERNAME>/metal-db-frontend:latest
```

След това просто:

```bash
docker compose up -d
```

---

## Технически детайли

| Параметър | Стойност |
|---|---|
| Фронтенд порт | `8080` |
| Backend порт | `5000` (само вътрешен) |
| База данни | SQLite в Docker Volume |
| Мрежа | bridge (`metal-net`) |
| Health check | `GET /api/health` на всеки 10s |
| Restart policy | `unless-stopped` |
