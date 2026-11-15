# 🦷 Dental Management System

A web-based **Dental Management System** built using Python Flask. The application aims to simplify dental clinic operations and provide an organized platform for managing dental services and related information.

## 🚀 About the Project

The Dental Management System is designed to provide a user-friendly web application for dental clinic management.

The project uses Flask as its backend framework and HTML, CSS, and JavaScript for the frontend.

## 🛠️ Tech Stack

**Backend**
- Python
- Flask

**Frontend**
- HTML5
- CSS3
- Bootstrap
- JavaScript

**Database**
- SQLite

**Tools**
- Git
- GitHub
- VS Code

## ✨ Features

- User-friendly interface
- Flask-based backend
- Dynamic web pages using Jinja2
- Database integration
- Responsive frontend
- Organized application structure

## 📂 Project Structure

```text
Dental/
│
├── app.py
├── requirements.txt
├── config.py
├── models.py
│
├── templates/
│   └── HTML templates
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── instance/
├── venv/
└── README.md
```


## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone 
```

### 2. Navigate to the Project Directory

```bash
cd Dental
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

### 4. Activate Virtual Environment

**Windows:**

```powershell
venv\Scripts\activate
```

**Linux / macOS:**

```bash
source venv/bin/activate
```

### 5. Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 6. Run the Application

If your main application file is `app.py`:

```bash
python app.py
```

Alternatively, use Flask CLI:

```bash
flask --app app run --debug
```

### 7. Open in Browser

```text
http://127.0.0.1:5000/
```

## 🔐 Environment Variables

If your application uses environment variables, create a `.env` file in the project root.

Example:

```env
SECRET_KEY=your-secret-key
DATABASE_URL=your-database-url
```

## 🔮 Future Improvements

- Improve dashboard functionality
- Add advanced appointment management
- Enhance authentication and authorization
- Improve database management
- Deploy the application to a cloud platform

## 👨‍💻 Author

**Rachit Lahase**

Python Developer | Flask | Django | SQL

- GitHub: [Rachi358](https://github.com/Rachi358)
- LinkedIn: Add your LinkedIn profile

## 📄 License

This project is developed for educational and development purposes.