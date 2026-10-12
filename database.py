import os
import sqlite3
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ds_lab_db")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "ds_lab")

USE_MYSQL = False
pymysql = None

try:
    import pymysql
    import pymysql.cursors
except ImportError:
    pymysql = None


def test_mysql_connection():
    """Attempt to connect to MySQL server and ensure ds_lab database exists."""
    global USE_MYSQL
    if not pymysql:
        return False
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=3
        )
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        conn.close()
        USE_MYSQL = True
        logger.info(f"Connected to MySQL on {DB_HOST}:{DB_PORT}. Database '{DB_NAME}' verified.")
        return True
    except Exception as e:
        logger.warning(f"MySQL connection attempt failed ({e}). Falling back to SQLite for seamless local storage.")
        USE_MYSQL = False
        return False


def get_db():
    """Return a database connection (MySQL if available, otherwise SQLite)."""
    global USE_MYSQL
    if USE_MYSQL and pymysql:
        try:
            return pymysql.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True
            )
        except Exception as e:
            logger.warning(f"Reconnecting to MySQL failed ({e}), using SQLite.")
            USE_MYSQL = False

    # SQLite fallback
    db_path = os.path.join(os.path.dirname(__file__), f"{DB_NAME}.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Initialize student, experiments, experiment_media, modules, tools, and resources tables."""
    test_mysql_connection()
    conn = get_db()
    cursor = conn.cursor()

    if USE_MYSQL:
        # MySQL tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                roll_no VARCHAR(50) NOT NULL,
                section VARCHAR(20) NOT NULL,
                branch VARCHAR(100) NOT NULL,
                subject VARCHAR(100) DEFAULT 'Data Science',
                faculty VARCHAR(100) DEFAULT 'Faculty In-Charge',
                photo_url VARCHAR(255) DEFAULT '/static/images/shanmukhi-profile.png',
                github_url VARCHAR(255) DEFAULT '',
                linkedin_url VARCHAR(255) DEFAULT '',
                website_url VARCHAR(255) DEFAULT ''
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # Add any missing columns dynamically
        for col_def in [
            ("subject", "VARCHAR(100) DEFAULT 'Data Science'"),
            ("faculty", "VARCHAR(100) DEFAULT 'Faculty In-Charge'"),
            ("linkedin_url", "VARCHAR(255) DEFAULT ''"),
            ("website_url", "VARCHAR(255) DEFAULT ''")
        ]:
            try:
                cursor.execute(f"ALTER TABLE student ADD COLUMN {col_def[0]} {col_def[1]};")
            except Exception:
                pass

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS experiments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                experiment_no VARCHAR(20) NOT NULL,
                title VARCHAR(255) NOT NULL,
                short_description TEXT NOT NULL,
                d2_heading VARCHAR(255) DEFAULT 'Long Description',
                long_content LONGTEXT NOT NULL,
                github_url VARCHAR(255) DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS experiment_media (
                id INT AUTO_INCREMENT PRIMARY KEY,
                experiment_id INT NOT NULL,
                media_type VARCHAR(50) NOT NULL,
                media_url VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_exp_media_experiment
                    FOREIGN KEY (experiment_id) REFERENCES experiments(id)
                    ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS modules (
                id INT AUTO_INCREMENT PRIMARY KEY,
                module_no VARCHAR(20) NOT NULL,
                title VARCHAR(255) NOT NULL,
                description TEXT NOT NULL,
                topics TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tools (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                category VARCHAR(100) NOT NULL,
                description TEXT NOT NULL,
                tool_url VARCHAR(255) DEFAULT '',
                icon_url VARCHAR(255) DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resources (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                category VARCHAR(100) NOT NULL,
                description TEXT NOT NULL,
                link_url VARCHAR(255) DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # Student seed
        cursor.execute("SELECT COUNT(*) AS cnt FROM student")
        if cursor.fetchone()["cnt"] == 0:
            cursor.execute("""
                INSERT INTO student (id, name, roll_no, section, branch, subject, faculty, photo_url, github_url, linkedin_url, website_url)
                VALUES (1, 'Shanmukhi', '24102A030132', 'DS-3', 'Data Science', 'Data Science', 'Faculty In-Charge', '/static/images/shanmukhi-profile.png', 'https://github.com/shanmukhi-06', '', 'https://github.com/shanmukhi-06')
            """)

        # Seed modules, tools, resources, experiments
        cursor.execute("SELECT COUNT(*) AS cnt FROM experiments")
        if cursor.fetchone()["cnt"] == 0:
            _seed_sample_experiments(conn, is_mysql=True)

        cursor.execute("SELECT COUNT(*) AS cnt FROM modules")
        if cursor.fetchone()["cnt"] == 0:
            _seed_modules(conn, is_mysql=True)

        cursor.execute("SELECT COUNT(*) AS cnt FROM tools")
        if cursor.fetchone()["cnt"] == 0:
            _seed_tools(conn, is_mysql=True)

        cursor.execute("SELECT COUNT(*) AS cnt FROM resources")
        if cursor.fetchone()["cnt"] == 0:
            _seed_resources(conn, is_mysql=True)

        conn.close()

    else:
        # SQLite tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                roll_no TEXT NOT NULL,
                section TEXT NOT NULL,
                branch TEXT NOT NULL,
                subject TEXT DEFAULT 'Data Science',
                faculty TEXT DEFAULT 'Faculty In-Charge',
                photo_url TEXT DEFAULT '/static/images/shanmukhi-profile.png',
                github_url TEXT DEFAULT '',
                linkedin_url TEXT DEFAULT '',
                website_url TEXT DEFAULT ''
            )
        """)

        # Dynamically add missing columns to SQLite table
        for col_name, col_type in [
            ("subject", "TEXT DEFAULT 'Data Science'"),
            ("faculty", "TEXT DEFAULT 'Faculty In-Charge'"),
            ("linkedin_url", "TEXT DEFAULT ''"),
            ("website_url", "TEXT DEFAULT ''")
        ]:
            try:
                cursor.execute(f"ALTER TABLE student ADD COLUMN {col_name} {col_type};")
            except Exception:
                pass
        conn.commit()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS experiments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_no TEXT NOT NULL,
                title TEXT NOT NULL,
                short_description TEXT NOT NULL,
                d2_heading TEXT DEFAULT 'Long Description',
                long_content TEXT NOT NULL,
                github_url TEXT DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS experiment_media (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id INTEGER NOT NULL,
                media_type TEXT NOT NULL,
                media_url TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (experiment_id) REFERENCES experiments(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS modules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module_no TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                topics TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tools (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                tool_url TEXT DEFAULT '',
                icon_url TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                link_url TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

        cursor.execute("SELECT COUNT(*) FROM student")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO student (id, name, roll_no, section, branch, subject, faculty, photo_url, github_url, linkedin_url, website_url)
                VALUES (1, 'Shanmukhi', '24102A030132', 'DS-3', 'Data Science', 'Data Science', 'Faculty In-Charge', '/static/images/shanmukhi-profile.png', 'https://github.com/shanmukhi-06', '', 'https://github.com/shanmukhi-06')
            """)
            conn.commit()
        else:
            # Ensure Shanmukhi details and subject Data Science are set
            cursor.execute("""
                UPDATE student SET name='Shanmukhi', roll_no='24102A030132', section='DS-3', branch='Data Science',
                                   subject='Data Science', faculty='Faculty In-Charge', github_url='https://github.com/shanmukhi-06',
                                   photo_url='/static/images/shanmukhi-profile.png', linkedin_url=''
                WHERE id = 1
            """)
            conn.commit()

        cursor.execute("SELECT COUNT(*) FROM experiments")
        if cursor.fetchone()[0] == 0:
            _seed_sample_experiments(conn, is_mysql=False)

        cursor.execute("SELECT COUNT(*) FROM modules")
        if cursor.fetchone()[0] == 0:
            _seed_modules(conn, is_mysql=False)

        cursor.execute("SELECT COUNT(*) FROM tools")
        if cursor.fetchone()[0] == 0:
            _seed_tools(conn, is_mysql=False)

        cursor.execute("SELECT COUNT(*) FROM resources")
        if cursor.fetchone()[0] == 0:
            _seed_resources(conn, is_mysql=False)

        conn.close()

    logger.info(f"Database initialized successfully (Mode: {'MySQL' if USE_MYSQL else 'SQLite'}).")


def _seed_sample_experiments(conn, is_mysql=False):
    cursor = conn.cursor()
    exp1_long = """AIM:
To extract, clean, and structure external tabular and text data from web resources and RESTful APIs using Python, Requests, and BeautifulSoup.

PROCEDURE:
1. Initialize HTTP session with appropriate request headers and rate-limiting.
2. Query target endpoints and parse HTML DOM trees using BeautifulSoup.
3. Extract relevant tabular data structures and clean unformatted strings.
4. Normalize structured data into Pandas DataFrames and export to CSV/JSON format.

OBSERVATIONS & OUTPUT:
Successfully collected 500+ records of clean tabular data without data loss or schema corruption.

CONCLUSION:
Automated data harvesting pipeline established for downstream exploratory analysis and modeling."""

    exp2_long = """AIM:
To perform comprehensive Exploratory Data Analysis (EDA), statistical summary generation, missing value imputation, and visual feature distribution analysis.

PROCEDURE:
1. Load dataset into Pandas DataFrame and compute summary statistics (mean, median, IQR, variance).
2. Detect missing values and apply median imputation for numeric attributes and mode for categorical features.
3. Identify outliers using Tukey's Interquartile Range (IQR) method and boxplot visualizations.
4. Generate correlation matrices, pair plots, and feature distribution histograms using Matplotlib & Seaborn.

OBSERVATIONS & OUTPUT:
Identified key feature distributions, detected multi-collinearity between predictor variables, and normalized skewed distributions.

CONCLUSION:
Dataset cleaned, validated, and prepared for high-accuracy predictive machine learning models."""

    exp3_long = """AIM:
To build, evaluate, and compare supervised classification pipelines (Logistic Regression and Decision Tree Classifiers) using Scikit-Learn.

PROCEDURE:
1. Split preprocessed dataset into 80% training and 20% testing partitions using stratified sampling.
2. Standardize features using StandardScaler pipeline.
3. Train Logistic Regression and Decision Tree classification algorithms.
4. Evaluate performance using Accuracy, Precision, Recall, F1-Score, and Confusion Matrix.

OBSERVATIONS & OUTPUT:
Decision Tree Classifier achieved 94.2% accuracy and 0.93 F1-score on held-out test data.

CONCLUSION:
Supervised classification model trained, tuned, and validated with complete evaluation metrics."""

    if is_mysql:
        cursor.execute("""
            INSERT INTO experiments (id, experiment_no, title, short_description, d2_heading, long_content, github_url)
            VALUES (1, '1', 'Data Collection & Web Scraping', 
            'Extraction of structured datasets from web tables and RESTful APIs using Python, BeautifulSoup, and Requests.',
            'Aim & Methodology', %s, 'https://github.com/shanmukhi-06')
        """, (exp1_long,))
        cursor.execute("""
            INSERT INTO experiment_media (experiment_id, media_type, media_url)
            VALUES (1, 'cover_image', 'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=800&q=80')
        """)

        cursor.execute("""
            INSERT INTO experiments (id, experiment_no, title, short_description, d2_heading, long_content, github_url)
            VALUES (2, '2', 'Exploratory Data Analysis (EDA)', 
            'Comprehensive exploratory analysis, statistical summaries, missing value imputation, and visual distribution mapping.',
            'EDA & Statistical Analysis', %s, 'https://github.com/shanmukhi-06')
        """, (exp2_long,))
        cursor.execute("""
            INSERT INTO experiment_media (experiment_id, media_type, media_url)
            VALUES (2, 'cover_image', 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=800&q=80')
        """)

        cursor.execute("""
            INSERT INTO experiments (id, experiment_no, title, short_description, d2_heading, long_content, github_url)
            VALUES (3, '3', 'Supervised Classification Model', 
            'Implementation and comparative evaluation of Logistic Regression and Decision Tree classification pipelines.',
            'Model Training & Evaluation', %s, 'https://github.com/shanmukhi-06')
        """, (exp3_long,))
        cursor.execute("""
            INSERT INTO experiment_media (experiment_id, media_type, media_url)
            VALUES (3, 'cover_image', 'https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3?auto=format&fit=crop&w=800&q=80')
        """)
    else:
        cursor.execute("""
            INSERT INTO experiments (id, experiment_no, title, short_description, d2_heading, long_content, github_url)
            VALUES (1, '1', 'Data Collection & Web Scraping', 
            'Extraction of structured datasets from web tables and RESTful APIs using Python, BeautifulSoup, and Requests.',
            'Aim & Methodology', ?, 'https://github.com/shanmukhi-06')
        """, (exp1_long,))
        cursor.execute("""
            INSERT INTO experiment_media (experiment_id, media_type, media_url)
            VALUES (1, 'cover_image', 'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=800&q=80')
        """)

        cursor.execute("""
            INSERT INTO experiments (id, experiment_no, title, short_description, d2_heading, long_content, github_url)
            VALUES (2, '2', 'Exploratory Data Analysis (EDA)', 
            'Comprehensive exploratory analysis, statistical summaries, missing value imputation, and visual distribution mapping.',
            'EDA & Statistical Analysis', ?, 'https://github.com/shanmukhi-06')
        """, (exp2_long,))
        cursor.execute("""
            INSERT INTO experiment_media (experiment_id, media_type, media_url)
            VALUES (2, 'cover_image', 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=800&q=80')
        """)

        cursor.execute("""
            INSERT INTO experiments (id, experiment_no, title, short_description, d2_heading, long_content, github_url)
            VALUES (3, '3', 'Supervised Classification Model', 
            'Implementation and comparative evaluation of Logistic Regression and Decision Tree classification pipelines.',
            'Model Training & Evaluation', ?, 'https://github.com/shanmukhi-06')
        """, (exp3_long,))
        cursor.execute("""
            INSERT INTO experiment_media (experiment_id, media_type, media_url)
            VALUES (3, 'cover_image', 'https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3?auto=format&fit=crop&w=800&q=80')
        """)
        conn.commit()


def _seed_modules(conn, is_mysql=False):
    cursor = conn.cursor()
    modules_data = [
        ("1", "Module 1: Python for Data Science & Numerical Computing", 
         "Fundamental Python data structures, NumPy arrays, vectorized calculations, and scientific computing foundations.",
         "Python Basics, NumPy Arrays, Vectorization, Matrix Algebra"),
        ("2", "Module 2: Data Cleaning, Preprocessing & EDA", 
         "Techniques for handling missing values, outlier detection, data normalization, and Exploratory Data Analysis.",
         "Pandas DataFrames, Data Cleaning, Missing Data Imputation, Distribution Analysis"),
        ("3", "Module 3: Statistical Inference & Data Visualization", 
         "Descriptive statistics, hypothesis testing, probability distributions, and visual analytics using Matplotlib & Seaborn.",
         "Histograms, Correlation Heatmaps, Box Plots, Hypothesis Testing"),
        ("4", "Module 4: Machine Learning & Predictive Modeling", 
         "Supervised and unsupervised learning algorithms including linear regression, classification trees, and clustering.",
         "Scikit-Learn, Regression, Decision Trees, Model Evaluation, Cross Validation")
    ]
    for mod in modules_data:
        if is_mysql:
            cursor.execute("""
                INSERT INTO modules (module_no, title, description, topics)
                VALUES (%s, %s, %s, %s)
            """, mod)
        else:
            cursor.execute("""
                INSERT INTO modules (module_no, title, description, topics)
                VALUES (?, ?, ?, ?)
            """, mod)
    if not is_mysql:
        conn.commit()


def _seed_tools(conn, is_mysql=False):
    cursor = conn.cursor()
    tools_data = [
        ("Python 3 & NumPy", "Scientific Computing", "Core programming environment for numerical computing, data analysis, and scientific arrays.", "https://www.python.org/"),
        ("Pandas & Scikit-Learn", "Data Analysis & ML", "Standard Python libraries for structured dataframe manipulation, preprocessing, and machine learning.", "https://pandas.pydata.org/"),
        ("Jupyter Lab / Notebook", "Interactive Lab", "Interactive laboratory environment for live code, data visualization, and documentation.", "https://jupyter.org/"),
        ("Visual Studio Code", "Code Editor", "Lightweight development IDE with support for Python, Jupyter extensions, and data science workflows.", "https://code.visualstudio.com/"),
        ("Git & GitHub", "Version Control", "Digital tracking and remote collaboration for lab record experiments and assignments.", "https://github.com/")
    ]
    for tool in tools_data:
        if is_mysql:
            cursor.execute("""
                INSERT INTO tools (name, category, description, tool_url)
                VALUES (%s, %s, %s, %s)
            """, tool)
        else:
            cursor.execute("""
                INSERT INTO tools (name, category, description, tool_url)
                VALUES (?, ?, ?, ?)
            """, tool)
    if not is_mysql:
        conn.commit()


def _seed_resources(conn, is_mysql=False):
    cursor = conn.cursor()
    res_data = [
        ("Python for Data Analysis (Wes McKinney - O'Reilly)", "Textbook", "Standard reference on data manipulation, analysis, and cleaning using NumPy and Pandas.", "https://wesmckinney.com/book/"),
        ("MBU Data Science Laboratory Manual & Guidelines", "Curriculum", "Official Mohan Babu University Department of Data Science curriculum, lab rubrics, and submission protocols.", "#"),
        ("Pandas & Scikit-Learn Data Science Cheat Sheet", "Cheat Sheet", "Quick reference for DataFrame operations, feature scaling, model fitting, and evaluation metrics.", "#"),
        ("Hands-On Machine Learning (Aurélien Géron)", "Reference Book", "Practical guide to building intelligent machine learning and deep learning systems.", "https://www.oreilly.com/library/view/hands-on-machine-learning/9781492032632/")
    ]
    for r in res_data:
        if is_mysql:
            cursor.execute("""
                INSERT INTO resources (title, category, description, link_url)
                VALUES (%s, %s, %s, %s)
            """, r)
        else:
            cursor.execute("""
                INSERT INTO resources (title, category, description, link_url)
                VALUES (?, ?, ?, ?)
            """, r)
    if not is_mysql:
        conn.commit()


# ----------------- STUDENT CRUD -----------------

def get_student():
    """Retrieve the student profile."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM student WHERE id = 1 LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def update_student(name, roll_no, section, branch, assistant_professor="", github_url="", photo_url=None, subject="Data Science", faculty="Faculty In-Charge", linkedin_url="", website_url=""):
    """Update student profile in MySQL / DB."""
    conn = get_db()
    cursor = conn.cursor()
    if photo_url:
        if USE_MYSQL:
            cursor.execute("""
                UPDATE student SET name=%s, roll_no=%s, section=%s, branch=%s,
                                   subject=%s, faculty=%s, github_url=%s, linkedin_url=%s, website_url=%s, photo_url=%s
                WHERE id=1
            """, (name, roll_no, section, branch, subject, faculty, github_url, linkedin_url, website_url, photo_url))
        else:
            cursor.execute("""
                UPDATE student SET name=?, roll_no=?, section=?, branch=?,
                                   subject=?, faculty=?, github_url=?, linkedin_url=?, website_url=?, photo_url=?
                WHERE id=1
            """, (name, roll_no, section, branch, subject, faculty, github_url, linkedin_url, website_url, photo_url))
            conn.commit()
    else:
        if USE_MYSQL:
            cursor.execute("""
                UPDATE student SET name=%s, roll_no=%s, section=%s, branch=%s,
                                   subject=%s, faculty=%s, github_url=%s, linkedin_url=%s, website_url=%s
                WHERE id=1
            """, (name, roll_no, section, branch, subject, faculty, github_url, linkedin_url, website_url))
        else:
            cursor.execute("""
                UPDATE student SET name=?, roll_no=?, section=?, branch=?,
                                   subject=?, faculty=?, github_url=?, linkedin_url=?, website_url=?
                WHERE id=1
            """, (name, roll_no, section, branch, subject, faculty, github_url, linkedin_url, website_url))
            conn.commit()
    conn.close()
    return get_student()


# ----------------- EXPERIMENTS CRUD -----------------

def get_experiments(search=None):
    """Retrieve all experiments with attached media, optionally filtered."""
    conn = get_db()
    cursor = conn.cursor()
    if search:
        pattern = f"%{search.strip()}%"
        if USE_MYSQL:
            cursor.execute("""
                SELECT * FROM experiments 
                WHERE experiment_no LIKE %s OR title LIKE %s OR short_description LIKE %s
                ORDER BY CAST(experiment_no AS UNSIGNED) ASC, id ASC
            """, (pattern, pattern, pattern))
        else:
            cursor.execute("""
                SELECT * FROM experiments 
                WHERE experiment_no LIKE ? OR title LIKE ? OR short_description LIKE ?
                ORDER BY CAST(experiment_no AS INTEGER) ASC, id ASC
            """, (pattern, pattern, pattern))
    else:
        if USE_MYSQL:
            cursor.execute("SELECT * FROM experiments ORDER BY CAST(experiment_no AS UNSIGNED) ASC, id ASC")
        else:
            cursor.execute("SELECT * FROM experiments ORDER BY CAST(experiment_no AS INTEGER) ASC, id ASC")

    rows = cursor.fetchall()
    experiments = [dict(r) for r in rows]

    # Attach media
    for exp in experiments:
        exp_id = exp["id"]
        if USE_MYSQL:
            cursor.execute("SELECT media_type, media_url FROM experiment_media WHERE experiment_id = %s", (exp_id,))
        else:
            cursor.execute("SELECT media_type, media_url FROM experiment_media WHERE experiment_id = ?", (exp_id,))
        media_rows = cursor.fetchall()
        exp["cover_image"] = None
        exp["video"] = None
        for m in media_rows:
            m_dict = dict(m)
            if m_dict["media_type"] == "cover_image" and not exp["cover_image"]:
                exp["cover_image"] = m_dict["media_url"]
            elif m_dict["media_type"] == "video" and not exp["video"]:
                exp["video"] = m_dict["media_url"]

    conn.close()
    return experiments


def get_experiment(exp_id):
    """Retrieve a single experiment by ID with all media."""
    conn = get_db()
    cursor = conn.cursor()
    if USE_MYSQL:
        cursor.execute("SELECT * FROM experiments WHERE id = %s", (exp_id,))
    else:
        cursor.execute("SELECT * FROM experiments WHERE id = ?", (exp_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None

    exp = dict(row)
    if USE_MYSQL:
        cursor.execute("SELECT id, media_type, media_url FROM experiment_media WHERE experiment_id = %s", (exp_id,))
    else:
        cursor.execute("SELECT id, media_type, media_url FROM experiment_media WHERE experiment_id = ?", (exp_id,))
    media_rows = cursor.fetchall()
    exp["cover_image"] = None
    exp["video"] = None
    exp["media_list"] = []
    for m in media_rows:
        m_dict = dict(m)
        exp["media_list"].append(m_dict)
        if m_dict["media_type"] == "cover_image" and not exp["cover_image"]:
            exp["cover_image"] = m_dict["media_url"]
        elif m_dict["media_type"] == "video" and not exp["video"]:
            exp["video"] = m_dict["media_url"]

    conn.close()
    return exp


def add_experiment(experiment_no, title, short_description, d2_heading, long_content, github_url=None, cover_url=None, video_url=None):
    """Add a new experiment with cover and video into MySQL / DB."""
    conn = get_db()
    cursor = conn.cursor()
    d2_heading = d2_heading or "Long Description"
    github_url = github_url or ""

    if USE_MYSQL:
        cursor.execute("""
            INSERT INTO experiments (experiment_no, title, short_description, d2_heading, long_content, github_url)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (experiment_no, title, short_description, d2_heading, long_content, github_url))
        exp_id = cursor.lastrowid
        if cover_url:
            cursor.execute("""
                INSERT INTO experiment_media (experiment_id, media_type, media_url)
                VALUES (%s, 'cover_image', %s)
            """, (exp_id, cover_url))
        if video_url:
            cursor.execute("""
                INSERT INTO experiment_media (experiment_id, media_type, media_url)
                VALUES (%s, 'video', %s)
            """, (exp_id, video_url))
    else:
        cursor.execute("""
            INSERT INTO experiments (experiment_no, title, short_description, d2_heading, long_content, github_url)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (experiment_no, title, short_description, d2_heading, long_content, github_url))
        exp_id = cursor.lastrowid
        if cover_url:
            cursor.execute("""
                INSERT INTO experiment_media (experiment_id, media_type, media_url)
                VALUES (?, 'cover_image', ?)
            """, (exp_id, cover_url))
        if video_url:
            cursor.execute("""
                INSERT INTO experiment_media (experiment_id, media_type, media_url)
                VALUES (?, 'video', ?)
            """, (exp_id, video_url))
        conn.commit()

    conn.close()
    return get_experiment(exp_id)


def delete_experiment(exp_id):
    """Delete experiment from MySQL / DB and return list of media file URLs to clean up."""
    conn = get_db()
    cursor = conn.cursor()
    if USE_MYSQL:
        cursor.execute("SELECT media_url FROM experiment_media WHERE experiment_id = %s", (exp_id,))
    else:
        cursor.execute("SELECT media_url FROM experiment_media WHERE experiment_id = ?", (exp_id,))
    media_urls = [row["media_url"] if isinstance(row, dict) else row[0] for row in cursor.fetchall()]

    if USE_MYSQL:
        cursor.execute("DELETE FROM experiments WHERE id = %s", (exp_id,))
    else:
        cursor.execute("DELETE FROM experiment_media WHERE experiment_id = ?", (exp_id,))
        cursor.execute("DELETE FROM experiments WHERE id = ?", (exp_id,))
        conn.commit()

    conn.close()
    return media_urls


# ----------------- MODULES CRUD -----------------

def get_modules():
    conn = get_db()
    cursor = conn.cursor()
    if USE_MYSQL:
        cursor.execute("SELECT * FROM modules ORDER BY CAST(module_no AS UNSIGNED) ASC, id ASC")
    else:
        cursor.execute("SELECT * FROM modules ORDER BY CAST(module_no AS INTEGER) ASC, id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_module(module_no, title, description, topics):
    conn = get_db()
    cursor = conn.cursor()
    if USE_MYSQL:
        cursor.execute("""
            INSERT INTO modules (module_no, title, description, topics)
            VALUES (%s, %s, %s, %s)
        """, (module_no, title, description, topics))
        mod_id = cursor.lastrowid
    else:
        cursor.execute("""
            INSERT INTO modules (module_no, title, description, topics)
            VALUES (?, ?, ?, ?)
        """, (module_no, title, description, topics))
        mod_id = cursor.lastrowid
        conn.commit()
    conn.close()
    return {"id": mod_id, "module_no": module_no, "title": title, "description": description, "topics": topics}


def delete_module(module_id):
    conn = get_db()
    cursor = conn.cursor()
    if USE_MYSQL:
        cursor.execute("DELETE FROM modules WHERE id = %s", (module_id,))
    else:
        cursor.execute("DELETE FROM modules WHERE id = ?", (module_id,))
        conn.commit()
    conn.close()
    return True


# ----------------- TOOLS CRUD -----------------

def get_tools():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tools ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_tool(name, category, description, tool_url):
    conn = get_db()
    cursor = conn.cursor()
    if USE_MYSQL:
        cursor.execute("""
            INSERT INTO tools (name, category, description, tool_url)
            VALUES (%s, %s, %s, %s)
        """, (name, category, description, tool_url))
        t_id = cursor.lastrowid
    else:
        cursor.execute("""
            INSERT INTO tools (name, category, description, tool_url)
            VALUES (?, ?, ?, ?)
        """, (name, category, description, tool_url))
        t_id = cursor.lastrowid
        conn.commit()
    conn.close()
    return {"id": t_id, "name": name, "category": category, "description": description, "tool_url": tool_url}


def delete_tool(tool_id):
    conn = get_db()
    cursor = conn.cursor()
    if USE_MYSQL:
        cursor.execute("DELETE FROM tools WHERE id = %s", (tool_id,))
    else:
        cursor.execute("DELETE FROM tools WHERE id = ?", (tool_id,))
        conn.commit()
    conn.close()
    return True


# ----------------- RESOURCES CRUD -----------------

def get_resources():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM resources ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_resource(title, category, description, link_url):
    conn = get_db()
    cursor = conn.cursor()
    if USE_MYSQL:
        cursor.execute("""
            INSERT INTO resources (title, category, description, link_url)
            VALUES (%s, %s, %s, %s)
        """, (title, category, description, link_url))
        r_id = cursor.lastrowid
    else:
        cursor.execute("""
            INSERT INTO resources (title, category, description, link_url)
            VALUES (?, ?, ?, ?)
        """, (title, category, description, link_url))
        r_id = cursor.lastrowid
        conn.commit()
    conn.close()
    return {"id": r_id, "title": title, "category": category, "description": description, "link_url": link_url}


def delete_resource(res_id):
    conn = get_db()
    cursor = conn.cursor()
    if USE_MYSQL:
        cursor.execute("DELETE FROM resources WHERE id = %s", (res_id,))
    else:
        cursor.execute("DELETE FROM resources WHERE id = ?", (res_id,))
        conn.commit()
    conn.close()
    return True


# ----------------- OVERVIEW COUNTS -----------------

def get_counts():
    conn = get_db()
    cursor = conn.cursor()
    
    def _count(table):
        cursor.execute(f"SELECT COUNT(*) AS cnt FROM {table}")
        res = cursor.fetchone()
        if res is None:
            return 0
        if isinstance(res, dict):
            return res.get("cnt", 0)
        return res[0]

    modules_count = _count("modules")
    exps_count = _count("experiments")
    tools_count = _count("tools")
    res_count = _count("resources")
    conn.close()

    return {
        "modules": modules_count,
        "experiments": exps_count,
        "tools": tools_count,
        "resources": res_count
    }
