# nl2sql-366 — Natural Language to SQL

A lightweight Python-based system that converts plain English questions into SQL queries and returns database results — without manual SQL writing.

**Course:** CSE366 Artificial Intelligence  
**Section:** 5 & 6  
**Milestone:** 2  

---

## 🚀 What It Does

Users can ask questions in natural language:

```
show female students
how many students from Dhaka
average salary by department
top 3 highest salary
maximum gpa
total salary of all students
```

The system automatically:

1. Detects user intent
2. Identifies required columns and values
3. Generates SQL query
4. Validates the query
5. Executes SQL
6. Displays the result

---

# ⚙️ System Workflow

```
User Question
      ↓
Load Dataset (CSV → SQLite)
      ↓
Read Schema (Columns, Types, Sample Values)
      ↓
Detect Intent (SELECT / COUNT / AVG / MAX / MIN / SUM)
      ↓
Match Columns + Operators + Values
      ↓
Generate SQL
      ↓
Validate SQL
      ↓
Execute SQL → Display Result
```

---

# 📂 Project Structure

```
nl2sql-366/
│
├── main.py                       # CLI entry point
│
├── core/                         # Core NL2SQL modules
│   ├── dataset_loader.py         # Load CSV into SQLite
│   ├── schema_reader.py          # Extract column names and types
│   ├── intent_detector.py        # TF-IDF + Naive Bayes classifier
│   ├── attribute_matcher.py      # Fuzzy column matching
│   ├── operator_detector.py      # Detect SQL operators
│   ├── value_matcher.py          # Extract values from questions
│   ├── sql_generator.py          # Generate SQL queries
│   ├── sql_validator.py          # SQL safety validation
│   └── sql_executor.py           # Execute SQL on SQLite
│
├── models/
│   ├── train_intent.py           # Model training script
│   ├── intent_model.pkl          # Trained Naive Bayes model
│   └── vectorizer.pkl             # TF-IDF vectorizer
│
├── knowledge/
│   ├── operators.json             # Phrase → SQL operator mapping
│   └── synonyms.json              # Column synonym dictionary
│
├── training_data/
│   └── intent_dataset.csv         # 5,000 labeled examples
│
├── data/
│   └── sample.csv                 # Sample student dataset
│
└── requirements.txt
```

---

# 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3 |
| Intent Detection | TF-IDF + Multinomial Naive Bayes |
| Column Matching | RapidFuzz |
| Database | SQLite |
| Data Processing | Pandas |
| Machine Learning | Scikit-learn |
| Interface | Command Line Interface (CLI) |

---

# 📦 Installation

## 1. Clone Repository

```bash
git clone https://github.com/your-username/nl2sql-366.git

cd nl2sql-366
```

---

## 2. Create Virtual Environment

Windows:

```bash
python -m venv .venv

.venv\Scripts\activate
```

Linux / Mac:

```bash
python -m venv .venv

source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 3. Train Intent Model (Optional)

```bash
python models/train_intent.py
```

---

## 4. Run Application

```bash
python main.py
```

---

# 📌 Sample Output

### Example 1

**Question**

```
show female students
```

**Output**

```
Intent : SELECT

SQL:
SELECT * FROM "data" 
WHERE "Gender" = 'Female'
```

Result:

```
+-------+-----+--------+------------+--------+-----+----------+
| Name  | Age | Gender | Department | Salary | GPA | District |
+-------+-----+--------+------------+--------+-----+----------+
| Alice | 22  | Female | CSE        | 35000  | 3.8 | Dhaka    |
| Carol | 21  | Female | CSE        | 31000  | 3.9 | Dhaka    |
| Eva   | 23  | Female | EEE        | 38000  | 3.7 | Dhaka    |
+-------+-----+--------+------------+--------+-----+----------+

5 row(s) returned
```

---

### Example 2

**Question**

```
average salary by department
```

**Output**

```
Intent : AVG

SQL:
SELECT "Department", AVG("Salary")
FROM "data"
GROUP BY "Department"
```

Result:

```
+------------+---------------+
| Department | AVG(Salary)   |
+------------+---------------+
| BBA        | 52666.67      |
| CSE        | 44500.00      |
| EEE        | 37666.67      |
+------------+---------------+
```

---

### Example 3

**Question**

```
maximum gpa
```

**Output**

```
Intent : MAX

SQL:
SELECT MAX("GPA")
FROM "data"
```

Result:

```
+------------+
| MAX(GPA)   |
+------------+
| 3.9        |
+------------+
```

---

# ✅ Supported Query Types

| Intent | Example |
|--------|---------|
| SELECT | show all students |
| SELECT | show female students |
| SELECT | show students older than 23 |
| SELECT | top 3 highest salary |
| COUNT | how many students from Dhaka |
| AVG | average salary by department |
| MAX | maximum GPA |
| MIN | lowest salary |
| SUM | total salary of all students |

---

# 🤖 Model Performance

| Metric | Result |
|--------|--------|
| Training Examples | 5,000 |
| Number of Intents | 6 |
| Algorithm | Multinomial Naive Bayes |
| Features | TF-IDF |
| Test Accuracy | 99.4% |

---

# 🔮 Future Plans (Milestone 3)

- OR / IN filtering  
  Example: `students from Dhaka or Sylhet`

- Multiple AND conditions  
  Example: `age > 22 and salary < 50000`

- GROUP BY with HAVING clause

- Larger WikiSQL dataset (80,000+ examples)

- HMM and MLP classifier comparison

- Flask web interface

- PostgreSQL database support

- Multi-table JOIN queries

- Automated pytest testing

---

# 📊 Dataset

Sample dataset:

```
data/sample.csv
```

Contains 10 student records with columns:

```
Name
Age
Gender
Department
Salary
GPA
District
```

To use your own dataset:

1. Replace `data/sample.csv`
2. Run:

```bash
python main.py
```

---

# 📜 License

This project was developed for academic purposes as part of **CSE366 Artificial Intelligence Course**.
