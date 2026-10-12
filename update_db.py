import sqlite3

conn = sqlite3.connect('ds_lab.db')
cursor = conn.cursor()

# 1. Update Student
cursor.execute('''
    UPDATE student 
    SET photo_url = '/static/images/shanmukhi-profile.png',
        subject = 'Data Science',
        linkedin_url = '',
        branch = 'Data Science',
        section = 'DS-3',
        name = 'Shanmukhi',
        roll_no = '24102A030132',
        github_url = 'https://github.com/shanmukhi-06'
    WHERE id = 1
''')

# 2. Update Tools descriptions
cursor.execute('''
    UPDATE tools 
    SET description = 'Core programming environment for numerical computing, data analysis, and scientific arrays.'
    WHERE name = 'Python 3 & NumPy'
''')
cursor.execute('''
    UPDATE tools 
    SET description = 'Lightweight development IDE with support for Python, Jupyter extensions, and data science workflows.'
    WHERE name = 'Visual Studio Code'
''')

cursor.execute("SELECT COUNT(*) FROM tools WHERE name LIKE '%Pandas%'")
if cursor.fetchone()[0] == 0:
    cursor.execute('''
        INSERT INTO tools (name, category, description, tool_url)
        VALUES ('Pandas & Scikit-Learn', 'Data Analysis & ML', 'Standard Python libraries for structured dataframe manipulation, preprocessing, and machine learning.', 'https://pandas.pydata.org/')
    ''')

# 3. Update Resources to pure Data Science
cursor.execute('DELETE FROM resources')
resources_ds = [
    ("Python for Data Analysis (Wes McKinney - O'Reilly)", "Textbook", "Standard reference on data manipulation, analysis, and cleaning using NumPy and Pandas.", "https://wesmckinney.com/book/"),
    ("MBU Data Science Laboratory Manual & Guidelines", "Curriculum", "Official Mohan Babu University Department of Data Science curriculum, lab rubrics, and submission protocols.", "#"),
    ("Pandas & Scikit-Learn Data Science Cheat Sheet", "Cheat Sheet", "Quick reference for DataFrame operations, feature scaling, model fitting, and evaluation metrics.", "#"),
    ("Hands-On Machine Learning (Aurélien Géron)", "Reference Book", "Practical guide to building intelligent machine learning and deep learning systems.", "https://www.oreilly.com/library/view/hands-on-machine-learning/9781492032632/")
]
for r in resources_ds:
    cursor.execute('INSERT INTO resources (title, category, description, link_url) VALUES (?, ?, ?, ?)', r)

# 4. Ensure Modules are Data Science modules
cursor.execute('DELETE FROM modules')
modules_ds = [
    ("1", "Module 1: Python for Data Science & Numerical Computing", "Introduction to Python data structures, NumPy arrays, vectorized operations, and scientific computing.", "Python Basics, NumPy Arrays, Vectorization, Matrix Algebra"),
    ("2", "Module 2: Data Cleaning, Preprocessing & EDA", "Techniques for handling missing values, outlier detection, data normalization, and Exploratory Data Analysis.", "Pandas DataFrames, Data Cleaning, Missing Data Imputation, Distribution Analysis"),
    ("3", "Module 3: Statistical Inference & Data Visualization", "Descriptive statistics, hypothesis testing, probability distributions, and visual analytics using Matplotlib & Seaborn.", "Histograms, Correlation Heatmaps, Box Plots, Hypothesis Testing"),
    ("4", "Module 4: Machine Learning & Predictive Modeling", "Supervised and unsupervised learning algorithms including linear regression, classification trees, and clustering.", "Scikit-Learn, Regression, Decision Trees, Model Evaluation, Cross Validation")
]
for m in modules_ds:
    cursor.execute('INSERT INTO modules (module_no, title, description, topics) VALUES (?, ?, ?, ?)', m)

conn.commit()
conn.close()
print("Database updated successfully!")
