# 🚀 TaskFlow – Project Management System

Hi,  
This is **TaskFlow**, a full-stack web application built using Django that helps users manage projects, tasks, and team collaboration efficiently.

The system provides a clean interface for organizing work, assigning tasks, and tracking progress using a Kanban-style workflow.

---

## 🔗 Live Demo

👉 taskflow-django-production.up.railway.app

---

## ✨ Features

- 🔐 User Authentication (Login/Logout)
- 📁 Project Creation & Management
- ✅ Task Management with Status Tracking
- 🔄 Kanban Board (Drag & Drop)
- 👥 Team Collaboration
- 🔔 Notifications System
- 📎 File Upload Support

---

## 🛠️ Tech Stack

- **Backend:** Django  
- **Database:** SQLite (can be extended to PostgreSQL)  
- **Frontend:** HTML, CSS, JavaScript  
- **Deployment:** Railway  
- **Server:** Gunicorn  
- **Static Files:** WhiteNoise  

---

## 🧠 Key Concepts

- **REST-style architecture** using Django views for handling requests and responses  
- **Relational database design** using Django ORM (Projects, Tasks, Users, Teams)  
- **Basic validation** for user inputs and data integrity  
- **Role-based access control** (users can only access their own data)

---

## 📂 Project Structure
accounts/ → Authentication & user profiles
projects/ → Project management
tasks/ → Task handling
teams/ → Team collaboration
chat/ → Messaging
files/ → File uploads
dashboard/ → Main dashboard
templates/ → HTML templates
static/ → CSS, JS files


---

## ⚙️ Installation & Setup

1. Clone the repository:
git clone https://github.com/your-username/taskflow-django.git

cd taskflow-django

2. Create virtual environment:
python -m venv venv

3. Activate environment:
venv\Scripts\activate (Windows)
source venv/bin/activate (Mac/Linux)

4. Install dependencies:
pip install -r requirements.txt


5. Apply migrations:

python manage.py migrate


6. Run the server:
python manage.py runserver

---
## 🌐 Deployment

The application is deployed using **Railway**, with:

- Gunicorn as WSGI server  
- WhiteNoise for static file handling  
- Environment-based configuration  
---

## 🎯 Conclusion

TaskFlow demonstrates full-stack development with Django, including backend logic, UI handling, database relationships, and cloud deployment.
---

## 👩‍💻 Author

Lavanya T