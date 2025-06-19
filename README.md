# <img src="static/img/favicon.svg" alt="HTML Hosting Logo" width="40" height="40"> HTML Hosting Service

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Available-brightgreen)](https://htmlhosting.pythonanywhere.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0%2B-lightgrey.svg)](https://flask.palletsprojects.com/)

A secure, user-friendly web application for hosting and sharing HTML pages with built-in authentication. Perfect for developers, educators, and content creators who need quick HTML hosting solutions.

🔗 **Live Demo:** [https://htmlhosting.pythonanywhere.com/](https://htmlhosting.pythonanywhere.com/)

## 🌟 Key Features

- 🔐 Secure User Authentication (Sign up, Login, Logout)
- 📝 Create & Host HTML pages with instant sharing
- 📊 Personalized Dashboard to manage all hosted pages
- 🎨 Modern UI with responsive design (works on all devices)
- 🚀 Fast page loading with optimized file handling
- 🔒 Security-first approach with password hashing and input validation

## 🖼️ Screenshots

| ![image](https://github.com/user-attachments/assets/9927830b-6e37-41ec-9228-02f2db68edbf) | ![image](https://github.com/user-attachments/assets/976868f5-27cb-48fe-85ad-9be3da4a7e88) |
|:---:|:---:|
| **Home Page** | **User Dashboard** |

## 🛠️ Technology Stack

- **Backend**: Python 3.8+ with Flask microframework
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Database**: JSON-based storage (Lightweight and efficient)
- **Security**: Werkzeug password hashing, input sanitization
- **Icons**: Font Awesome 5
- **Hosting**: PythonAnywhere (for live demo)

## 🚀 Quick Installation Guide

Get your local development environment running in 5 minutes:

```
# Clone repository
git clone https://github.com/jyotiska222/HTML-Hostng.git
cd HTML-Hostng

# Create virtual environment (Python 3.8+ required)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

Visit `http://localhost:5000` in your browser to access the application.

## 📂 Project Structure

```
html_hosting/
├── app.py              # Flask application core
├── requirements.txt    # Python dependencies
├── users.json          # User database (JSON)
├── static/
│   ├── css/            # All stylesheets
│   ├── img/            # Images, logos, favicons
│   └── js/             # JavaScript files
├── templates/          # Jinja2 templates
│   ├── base.html       # Master template
│   ├── auth/           # Authentication templates
│   ├── pages/          # Page management templates
│   └── errors/         # Error handling templates
└── uploads/            # Hosted HTML files storage
```

## 💡 How It Works

1. **User Registration**: Create your free account
2. **Page Creation**: Use our simple editor or upload HTML files
3. **Hosting**: Your page gets a unique, shareable URL
4. **Management**: Edit, update, or delete pages from your dashboard
5. **Sharing**: Share your HTML content with anyone via URL

## 🔒 Security Features

- **Password Protection**: BCrypt hashing for all user credentials
- **Session Management**: Secure cookie-based sessions
- **File Validation**: Strict checks on uploaded content
- **Input Sanitization**: Protection against XSS attacks
- **Error Handling**: Graceful degradation on errors

## 📈 SEO Optimization

This project includes several SEO best practices:
- Semantic HTML5 markup
- Responsive design (mobile-friendly)
- Fast page load times
- Clean URL structures
- Proper heading hierarchy
- Meta tags for social sharing

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

## 📬 Contact

For questions or support:
- GitHub Issues: [https://github.com/jyotiska222/HTML-Hostng/issues](https://github.com/jyotiska222/HTML-Hostng/issues)
- Project Link: [https://github.com/jyotiska222/HTML-Hostng](https://github.com/jyotiska222/HTML-Hostng)

## 🙏 Acknowledgements

- Flask Community for the excellent microframework
- PythonAnywhere for free hosting
- Font Awesome for beautiful icons
- All open source contributors
