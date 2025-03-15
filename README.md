# 🍔 Flava

A deliciously simple API that connects food lovers to share, swap, and savor recipes!

## 🚀 Overview

Flava is a RESTful API designed to bring together food enthusiasts, enabling them to share and explore a variety of recipes. The platform allows users to create, update, and browse recipes while leveraging caching for fast responses.

## 🛠️ Tech Stack

Flava is built using the following technologies:

- **FastAPI** - For building a high-performance backend  
- **PostgreSQL** - As the primary database  
- **Alembic** - For database migrations  
- **Redis** - For caching and improving response times  
- **Docker** - For containerized deployment  

## 📌 Features

- 📜 **Recipe Management**: Users can create, update, delete, and retrieve recipes.  
- 🔍 **Search & Filter**: Search recipes by name, ingredients, or category.  
- 🏷 **Categories & Tags**: Organize recipes for easier discovery.  
- ⚡ **Caching with Redis**: Speeds up responses for frequently requested data.  
- 🔑 **User Authentication**: Secure user authentication and authorization.

## 📡 API Endpoints

Below are the available API endpoints for interacting with the Flava API:

### 🥘 Recipe Endpoints

| Method | Endpoint          | Description               |
|------- |------------------ |--------------------------|
| GET    | `/recipes/`         | Retrieve all recipes      |
| POST   | `/recipes/`         | Create a new recipe       |
| GET    | `/recipes/{id}`    | Retrieve a recipe by ID   |
| PUT    | `/recipes/{id}`    | Update a recipe by ID     |
| DELETE | `/recipes/{id}`    | Delete a recipe by ID     |

---

### 🔍 Search & Filter Endpoints

| Method | Endpoint             | Description                          |
|------- |---------------------|-------------------------------------|
| GET    | `/recipes/search`    | Search recipes by keyword            |
| GET    | `/recipes/filter`    | Filter recipes by category or tag    |

---

### ⚙️ Authentication Endpoints

| Method | Endpoint         | Description                      |
|------- |----------------- |---------------------------------|
| POST   | `/users/`  | Register a new user              |
| POST   | `/users/login`     | Login user & retrieve token     |
| GET   | `/users/verify-email`     | Verify user via email    |
| POST   | `/users/password-reset-request`     | Request password reset     |
| PUT   | `/users/reset-password`     | Reset user password     |
| GET   | `/users/{id}`     | Get user with ID     |

---

## 🔧 Installation & Setup

1. **Clone the repository**
   ```sh
   git clone https://github.com/nksarps/flava
   cd flava


2. **Create a virtual environment and activate it**
   ```sh
   python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`

3. **Create a virtual environment and activate it**
   ```sh
   pip install -r requirements.txt

4. **Set up environment variables**

5. **Run database migrations**
    ```sh 
    alembic upgrade head

6. **Start the FastAPI server**
    ```sh
    @uvicorn app.main:app --reload


## 🛠 Contributing 
Contributions are welcome! Feel free to open issues or submit pull requests.