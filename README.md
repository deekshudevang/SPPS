# 🎓 EduPredict AI - Student Performance Intelligence SaaS

A production-ready, machine learning-powered SaaS platform that predicts student academic performance and provides AI-driven recommendations for improvement.

## 🚀 Key Features
- **Predictive Analytics:** Neural inference engine to forecast academic outcomes.
- **AI Recommendation Engine:** Automated, tailored advice for students across different risk tiers.
- **SaaS Infrastructure:** Multi-tenant architecture with role-based access control (RBAC).
- **Subscription Management:** Free and Pro plans with student limits and quota tracking.
- **Interactive Dashboards:** Modern visualizations using Chart.js for both Educators and Students.
- **REST API Layer:** Extensible backend powered by Django REST Framework.
- **Export Capabilities:** Generate PDF reports for performance reviews (Coming Soon).

## 🛠 Tech Stack
- **Backend:** Python 3.10+, Django 6.0
- **API:** Django REST Framework
- **Machine Learning:** Scikit-learn (Random Forest / Logistic Regression)
- **Database:** PostgreSQL (Production) / SQLite (Development)
- **Frontend:** HTML5, CSS3, Bootstrap 5.3, Chart.js

## 📂 Project Structure
```
EduPredict/
│── core/           # Project configuration & settings
│── accounts/       # Authentication & Subscription management
│── students/       # Student profiles & Prediction logic
│── api/            # REST API endpoints & Serializers
│── ml/             # ML model, training & inference scripts
│── templates/      # Global templates
│── static/         # CSS/JS assets
│── db.sqlite3      # Demo database
│── manage.py       # Django CLI
```

## ⚙️ Installation & Setup
1. **Clone the repository:**
   ```bash
   git clone https://github.com/deekshudevang/EduPredict-AI.git
   cd EduPredict-AI
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Environment Setup:**
   Create a `.env` file from the template:
   ```bash
   cp .env.example .env
   ```
4. **Run the server:**
   ```bash
   python manage.py runserver
   ```

## 📊 ML Architecture
**Algorithm:** Random Forest Classifier
**Inference Flow:** 
Academic Record -> Scaler -> Neural Model -> Label Decoder -> Risk Classification -> AI Recommendation Engine

## 📸 Dashboard Preview
![Mission Control](docs/dashboard.png)

## 👨‍💻 Author
**Deekshith G**
