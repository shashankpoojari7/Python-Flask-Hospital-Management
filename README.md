# 🐍 Python Flask Project

A simple Flask-based web application integrated with **Cloudinary** for media management and **MySQL** for database handling using **SQLAlchemy** ORM.

---

### ⚙️ Setup Instructions

Follow these steps to run the project locally:

#### 1. Clone the Repository

```bash
git clone https://github.com/shashankpoojari7/Python-Flask-Hospital-Management.git
cd Python-Flask-Hospital-Management
```
---
#### 2.  Create and Activate Virtual Environment

Windows:
```bash
python -m venv env
env\Scripts\activate
```

macOS/Linux:
```bash
python3 -m venv env
source env/bin/activate
```
---
#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```
---
#### 4. Configure Environment Variables
```bash
Create a `.env` file in the project root (you can copy the `.env.sample` file).  
Update it with your Cloudinary credentials and database connection string.

Required variables:
- `CLOUDINARY_CLOUD_NAME`
- `CLOUDINARY_API_KEY`
- `CLOUDINARY_API_SECRET`
- `DATABASE_URL`

Never commit your `.env` file — it contains sensitive data.
```
---
#### 5. Run the Application
```bash
Start the Flask server using `python app.py`.  
By default, it will run on `http://127.0.0.1:5000`.

If using Flask’s environment-based runner, you can also use `flask run`.
```
---

#### 🧠 Notes
```bash
- Always activate your virtual environment before running the project.
- Update `requirements.txt` after installing any new packages by running `pip freeze > requirements.txt`.

````
---

#### Technologies Used

- Flask – Web framework  
- SQLAlchemy – ORM for database handling  
- MySQL – Database  
- Cloudinary – Cloud media storage  
- Jinja2 – Template engine  
- python-dotenv – Environment variable management

---

#### 📁 Project Structure

- `static/` – Static files (CSS, JS, images)
- `templates/` – HTML templates
- `.env` – Environment variables (not tracked in Git)
- `.env.sample` – Sample environment variable file
- `app.py` – Main Flask application file
- `requirements.txt` – Python dependencies
- `.gitignore` – Files and folders to ignore in Git

---

#### 📄 License

This project is open source and available under the **MIT License**.

---

#### 👤 Author : 
***Shashank Poojari*** 

🌐 [GitHub Profile](https://github.com/shashankpoojari7)
