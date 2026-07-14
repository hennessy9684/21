# Project Overview

Django + Vue 前后端分离项目，包含 SimpleUI 管理后台。

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 6.0.7 + Django REST Framework 3.17.1 |
| Frontend | Vue 3 + Vite 8 |
| Database | SQLite (默认) |
| Admin | SimpleUI (中文) |
| API | REST Framework |

## Project Structure

```
/
├── config/            # Django 项目配置
│   ├── settings.py    # 配置文件
│   ├── urls.py        # URL 路由
│   ├── wsgi.py
│   └── asgi.py
├── polls/             # Django 应用（示例）
│   ├── admin.py
│   ├── models.py
│   ├── views.py
│   └── ...
├── frontend/          # Vue 前端项目
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.js
│   │   ├── components/
│   │   └── assets/
│   ├── vite.config.js  # Vite 配置（含代理）
│   └── package.json
├── manage.py
└── .venv/             # Python 虚拟环境
```

## Setup

### Backend

```powershell
.venv\Scripts\Activate.ps1
python manage.py migrate
python manage.py runserver
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

## Running Servers

| Service | URL | Port |
|---------|-----|------|
| Django Backend | http://localhost:8000/ | 8000 |
| Vue Frontend | http://localhost:5173/ | 5173 |
| Admin Panel | http://localhost:8000/admin/ | 8000 |

Vite dev server proxies `/api` and `/admin` requests to Django backend.

## Admin

- URL: `/admin/`
- Superuser: `lls` / `zzjsgLLS1@`
- UI: SimpleUI (Chinese locale)

## Django Apps

- `polls` — 已创建的示例应用
- 新应用通过 `python manage.py startapp <name>` 创建，需注册到 `INSTALLED_APPS`

## API Conventions

- API routes should be prefixed with `/api/` in `config/urls.py`
- DRF viewsets and routers are preferred for CRUD endpoints

## Key Dependencies

### Python
- django
- djangorestframework
- django-cors-headers
- django-simpleui

### Node
- vue 3
- vite
- @vitejs/plugin-vue
