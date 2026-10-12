# Data Science Laboratory (DS LAB) Portal

A simple, clean, and professional digital laboratory record website for college Data Science experiments.

## 🔗 Live Local Link
Open the website directly in your browser:
**[http://127.0.0.1:5000](http://127.0.0.1:5000)** or **[http://localhost:5000](http://localhost:5000)**

---

## 🌟 Key Features

1. **Light Academic Theme (Inspired by [Data Science Digital Laboratory](https://datalab-pyya.onrender.com/))**:
   - Clean serif headings (`Playfair Display` & `Source Serif 4`) and crisp body typography (`Inter`).
   - Ivory/white surfaces, subtle borders, navy & gold accents, and simple blue buttons.
   - Zero visual clutter, no unnecessary analytics cards or charts.

2. **Student ID Card**:
   - Displays Student Photo, Name, Roll Number, Section, Branch, Assistant Professor, and GitHub Repo.
   - Built-in **Edit ID Card** modal allows updating all details and uploading a photo with instant local and permanent database storage.

3. **Experiment Listing & Live Search**:
   - Experiments displayed in simple cards with experiment number, cover image, title, short description, and GitHub links.
   - Real-time search by experiment number, title, or description without page reloads.

4. **Add Experiment Flow**:
   - Simple modal for experiment number, title, short description (D1), cover image upload (JPG, PNG, WEBP), D2 heading, comprehensive D2 long content (Aim, Procedure, Explanation, Observations, Output, Conclusion), optional video clip (MP4, WebM, MOV), and optional GitHub link.
   - Immediately saves to MySQL and reflects in the UI.

5. **Read More (Experiment Details)**:
   - Full-view modal showing complete documentation, cover image, HTML5 video player with standard browser controls, and repository links.

6. **Delete Experiment**:
   - Confirmation dialog before deletion.
   - Automatically cleans up uploaded media files from disk and removes records from the database.

---

## 📁 Project Structure

```text
DS-Lab-Portal/
├── app.py                  # Flask backend & API routes
├── database.py             # Database connection layer (MySQL + auto-fallback)
├── database.sql            # MySQL table schemas & initial seed data
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── .env                    # Active environment configuration
├── templates/
│   └── index.html          # Semantic light-theme home page
└── static/
    ├── css/
    │   └── style.css       # Clean, academic light-theme stylesheet
    ├── js/
    │   └── app.js          # Interactive UI and API controller
    ├── images/             # Default avatars and placeholder graphics
    └── uploads/
        ├── images/         # Uploaded experiment cover & profile images
        └── videos/         # Uploaded experiment video clips
```

---

## 🗄️ Database Setup (MySQL)

1. Create the MySQL database using the provided `database.sql`:
   ```bash
   mysql -u root -p < database.sql
   ```

2. Configure your MySQL credentials in `.env`:
   ```env
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=YOUR_PASSWORD
   DB_NAME=ds_lab
   PORT=5000
   ```

> **Note:** If MySQL server is offline or credentials are not yet configured, the application automatically uses an embedded SQLite database (`ds_lab.db`) so the portal is always functional out-of-the-box. When you start MySQL, it connects automatically!

---

## 🚀 Running the Server

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the Flask application
python app.py
```
Open **[http://127.0.0.1:5000](http://127.0.0.1:5000)** in your browser.
