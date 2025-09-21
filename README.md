
# 🔧 Band Box Backend – Django REST API for Drycleaning App

This is the **backend API** for the [Band Box Drycleaners](https://github.com/rahules24/bandboxdrycleaners) project. It manages orders, billing, and user authentication for a local dry cleaning business, built with **Django** and **Django REST Framework**, using **PostgreSQL** for data storage.

---

## 📦 Tech Stack

- **Framework:** Django, Django REST Framework (DRF)
- **Database:** PostgreSQL
- **Authentication:** Django's built-in auth system (with optional token/session support)
- **API:** RESTful endpoints for orders, billing, and users
- **Hosting:** [Fly.io](https://fly.io/)

---

## 📁 Project Structure

```
bandboxbackend/
├── bandbox/              # Django project config
├── orders/               # Orders app (models, serializers, views)
├── manage.py
├── requirements.txt
└── README.md
```

---

## 📌 Core Features

- 🧾 Order creation and billing logic
- 📊 API endpoints for managing services and pricing
- 🔐 Admin and staff login (customizable roles)
- 🧩 Designed to connect with the React frontend via REST

---

## 🌐 Related Repositories

- **Frontend App:** [Band Box Drycleaners (React TypeScript)](https://github.com/rahules24/bandboxdrycleaners)

---

## 🧠 What I Learned

- Creating modular Django apps for scalable business tools
- Building production-grade REST APIs with DRF
- Managing PostgreSQL schema for real-world use cases
- Deploying Django APIs on Fly.io
