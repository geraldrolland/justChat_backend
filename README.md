
---

### **Backend (`justChat_backend/README.md`)**

```markdown
# JUST_CHAT Backend (justChat_backend)

Welcome to the **JUST_CHAT Backend**, the backbone of our real-time chatting application. This app provides a robust API and handles all server-side operations to support seamless communication.

## About the Developer
**Gerald Onyeka Ujowundu**  
Email: geraldrolland123@gmail.com  

## Features
The backend enables the following functionalities:
- **User Management**: Secure user registration, authentication, and login.
- **Real-Time Communication**: Powered by WebSocket for instant messaging.
- **File Sharing**: Handles file uploads (PDFs, images, and voice notes).
- **Group Chats**: APIs to create, manage, and interact with group chats.
- **Notifications**: Sends real-time notifications for messages and events.

## Technologies Used
- **Django Rest Framework (DRF)**: For building the API backend.
- **Celery**: For asynchronous tasks like notifications and file processing.
- **MySQL**: Relational database for data storage.
- **WebSocket**: Enables real-time communication.

## Installation
Follow these steps to set up the backend locally:

### Prerequisites
- **Python**: v3.9+
- **MySQL**: v8+
- **Docker** (optional): For containerized deployment.

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo-url/justChat_backend.git
   cd justChat_backend
Create a virtual environment and activate it:
bash
Copy
Edit
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies:
bash
Copy
Edit
pip install -r requirements.txt
Configure your .env file with the following details:
makefile
Copy
Edit
SECRET_KEY=your_secret_key
DATABASE_NAME=just_chat_db
DATABASE_USER=root
DATABASE_PASSWORD=password
DATABASE_HOST=localhost
DATABASE_PORT=3306
Run migrations and start the server:
bash
Copy
Edit
python manage.py migrate
python manage.py runserver
Contributing
We welcome contributions! To contribute:

Fork the repository.
Create a new branch for your feature or bug fix.
Submit a pull request with a detailed description of your changes.
License
Contact the developer for licensing information.