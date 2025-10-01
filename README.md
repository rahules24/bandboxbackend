
# 🔧 Band Box Backend – Django REST API for Drycleaning App

This is the **backend API** for the [Band Box Drycleaners](https://github.com/rahules24/bandboxdrycleaners) project. It manages orders, billing, and user authentication for a local dry cleaning business, built with **Django** and **Django REST Framework**, using **PostgreSQL** for data storage.

---

# Local Development

### 1. Setup ```.env```
- Use the same credentials while running the database container

### 2. Run the database container
- ```\bandboxdb>``` Run the docker image to start the local PostgreSQL database

### 3. Run Migrations
- Create tables in the connected databse:
    ```
    \bandboxbackend> python manage.py makemigrations
    \bandboxbackend> python manage.py migrate
    ```

### 4. Run backend server
- ```\bandboxbackend> python manage.py runserver```


---

# Production

### 1. Generate secret key
```
\user> python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
### 2. Set secrets on fly.io using terminal
- From directory containing fly.toml (app = 'bandboxbackend')
```
\bandboxbackend> flyctl secrets set KEY="value"
```
- Pass app name explicitly
```
\user> flyctl secrets set KEY="value" -a bandboxbackend
```

#### 3. Set following secrets
```
flyctl secrets set SECRET_KEY=""
flyctl secrets set DEBUG=False
flyctl secrets set DATABASE_URL="postgres://db_user:db_password@db_host:5432/db_name"
flyctl secrets set ALLOWED_HOSTS="bandboxbackend.fly.dev,rahules24.github.io"
flyctl secrets set CORS_ALLOWED_ORIGINS="https://rahules24.github.io"
flyctl secrets set CSRF_TRUSTED_ORIGINS="https://bandboxbackend.fly.dev"
```
### 4. Re-deploy bandboxbackend
```
\bandboxbackend> flyctl deploy -a bandboxbackend
```

### 5. Test API by sending a GET request
- ```curl https://bandboxbackend.fly.dev/```

#### If response body is empty, get response headers
- ```curl -i https://bandboxbackend.fly.dev/```
  - ```-i``` shows the response headers along with the body. 
```
HTTP/1.1 302 Found
location: /api/bills/
content-length: 0
```
<img src="media/images/setup-curl.png" width="65%" alt="redirect response header explanation">

#### ```curl``` by default does not follow redirects automatically
- use: ```curl -s -L https://bandboxbackend.fly.dev/ | jq```
  - ```-s```  Silent mode (hides progress and extra info).
  - ```-L```  Follow redirects automatically.
  - ``` | jq```  Pipes the output into jq, a tool to pretty-print JSON
  - ```-u username:password``` Sends credentials in base64 encoding.

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
- 📱 WhatsApp notifications for contact form submissions

---

## 🌐 Related Repositories

- **Frontend App:** [Band Box Drycleaners (React TypeScript)](https://github.com/rahules24/bandboxdrycleaners)