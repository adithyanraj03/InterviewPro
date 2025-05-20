# <img src="static/images/logo.png" alt="InterviewPro Logo" width="32" height="32"> InterviewPro - Professional Interview Portal

![License](https://img.shields.io/github/license/adithyanraj03/InterviewPro)
![Flask](https://img.shields.io/badge/Flask-2.0%2B-lightgrey)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-1.4%2B-red)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Jinja2](https://img.shields.io/badge/Jinja2-3.0%2B-green)
![Issues](https://img.shields.io/github/issues/adithyanraj03/InterviewPro)
![Forks](https://img.shields.io/github/forks/adithyanraj03/InterviewPro)
![Last Commit](https://img.shields.io/github/last-commit/adithyanraj03/InterviewPro)



## 📋 Overview

InterviewPro is a comprehensive, professional interview management system built with Flask and SQLAlchemy. This application provides a secure platform for administering technical assessments, evaluating candidate performance, and streamlining the recruitment process.

The platform supports complex technical assessments including code-based questions, multiple-choice evaluations, and customizable test parameters. With robust authentication, anti-cheating measures, and detailed reporting, InterviewPro provides everything needed to identify top technical talent efficiently.

<img src="https://github.com/user-attachments/assets/531d9a6f-3f08-4959-b81c-4c7fa160c9ea" alt="Image 1" width="25%" style="display:inline-block;">
<img src="https://github.com/user-attachments/assets/738525fa-5711-4294-80eb-80c5f9ab4a89" alt="Image 2" width="60%" style="display:inline-block;">




## ✨ Features

### For Administrators 👨‍💼

- 🔐 Secure admin dashboard with detailed analytics
- 📝 Create custom technical assessments with MCQs
- 💻 Support for questions with code snippets and syntax highlighting
- 🧩 Flexible test creation with customizable duration, passing scores, and attempt limits
- 📊 Comprehensive candidate performance tracking and reporting
- 🔄 Generate unique test access codes for controlled distribution

#### Admin Dashboard Tabs

1. **Dashboard** 📊
   - View test statistics and recent activity
   - Monitor candidate performance metrics and completion rates
   - Quick access to all administrative functions

2. **Tests** 📋
   - Create, edit, and manage assessment tests
   - Set test parameters (duration, passing score, attempts)
   - Generate unique access codes for test distribution
   - Preview tests before publishing

3. **Questions** 🧩
   - Create individual questions with multiple-choice options
   - Import questions in bulk from JSON format
   - Sample JSON template available at `static/data/questions.json` or `./questions.json`
   - Support for code snippets with syntax highlighting
   - Organize questions by categories for easy management

4. **Candidates** 👥
   - View all registered candidates and their profiles
   - Monitor test attempts, scores, and completion status
   - Access detailed candidate performance reports
   - Verify candidate credentials and authentication history

  <img src="https://github.com/user-attachments/assets/49eeef37-f443-43a8-8c4e-ca150c837b1d" alt="Image 3" width="45%" style="display:inline-block;">
  <img src="https://github.com/user-attachments/assets/7dc5a895-71f8-4dec-b473-7d5b0fa16495" alt="Image 4" width="45%" style="display:inline-block;">


### For Candidates 👨‍💻

- 📱 Responsive, user-friendly test-taking interface
- 🔒 Secure assessment environment with anti-cheating measures
- ⏱️ Real-time test timer and progress tracking
- 📋 Immediate feedback on test completion
- 📈 Historical test performance review

#### Candidate Features

1. **Test Access** 🎫
   - Enter test access codes to unlock assessments
   - View available tests with descriptions and time limits
   
2. **Test Environment** 💻
   - Distraction-free interface optimized for focus
   - Code snippets displayed with proper syntax highlighting
   - Real-time countdown timer visible throughout the test
   - Auto-save functionality to prevent data loss
   
3. **Results & Review** 📈
   - Immediate scoring and performance feedback
   - Review correct answers and explanations
   - View historical test attempts and progress

## 🛠️ Technology Stack

- **Backend**: Python Flask, SQLAlchemy ORM
- **Database**: SQLite (development), PostgreSQL (production-ready)
- **Frontend**: HTML5, CSS3, JavaScript, Jinja2 Templates
- **Authentication**: Flask-Login with password hashing
- **Deployment**: IIS-ready with wfastcgi support

Project Structure : 

```
interview_app/
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
├── templates/
│   ├── admin/
│   │   ├── dashboard.html
│   │   ├── create_test.html
│   │   ├── candidates.html
│   │   └── analytics.html
│   ├── candidate/
│   │   ├── dashboard.html
│   │   └── take_test.html
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   └── base.html
├── models/
│   ├── __init__.py
│   ├── user.py
│   ├── test.py
│   └── question.py
├── utils/
│   ├── __init__.py
│   ├── create_admin.py
│   └── check_admin.py
├── config.py
├── __init__.py
├── app.py
├── run.py
└── requirements.txt 
```

## 🔧 Technical Details

### System Architecture

- **MVC Pattern**: Follows the Model-View-Controller architecture for clean separation of concerns
- **RESTful API**: JSON endpoints for test submissions and result retrieval
- **Security**: Session management, CSRF protection, and password hashing
- **Responsive Design**: Mobile-friendly interfaces using modern CSS frameworks

### Key Files and Directories

- **app.py**: Main application logic and route definitions
- **models/**: Database models for users, tests, questions, and answers
- **templates/**: Jinja2 HTML templates organized by user roles
- **static/data/questions.json**: Sample question bank ready for import
- **utils/**: Helper scripts for admin creation and maintenance tasks

## 📦 Installation

### Prerequisites

- Python 3.9+
- pip package manager
- Virtual environment (recommended)

### Setup Instructions

1. Clone the repository
   ```
   git clone https://github.com/adithyanraj03/InterviewPro.git
   cd InterviewPro
   ```

2. Create and activate a virtual environment
   ```
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies
   ```
   pip install -r requirements.txt
   ```

4. Set up the database
   ```
   python reset_db.py
   ```

5. Create an admin user
   ```
   python utils/create_admin.py
   ```

6. Start the application
   ```
   python run.py
   ```

7. Access the application at `http://127.0.0.1:5000`

## 🚀 Deployment

### IIS Deployment (Windows)

1. Install wfastcgi:
   ```
   pip install wfastcgi
   wfastcgi-enable
   ```

2. Configure the web.config file with the correct paths for your environment
3. Set up an IIS site pointing to the project directory
4. Ensure IIS has the necessary permissions to execute Python

## 📊 Database Schema

The application uses a relational database with the following key models:

- **User**: Authentication and user profile (admin/candidate)
- **Test**: Assessment configuration and metadata
- **Question**: Test questions with multiple-choice options and code samples
- **TestAnswer**: Candidate responses and scoring
- **TestLog**: Security and event logging

## 👤 Default Login

- **Admin**:
  - Username: admin
  - Password: admin123

## 📝 License

This project is under [MIT License](LICENSE)

## 👨‍💻 Author

[Adithya N Raj](https://github.com/adithyanraj03)


