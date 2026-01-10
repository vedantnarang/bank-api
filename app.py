import sqlite3
import pandas as pd
from flask import Flask, jsonify, g, abort

# Configuration
# We use an in-memory database for speed and simplicity.
# In a real production app, this would be a file path or database URL.
DATABASE = ':memory:'
CSV_FILE = 'bank_branches.csv'

app = Flask(__name__)

# --- Database Helper Functions ---

def get_db():
    """Connects to the database and stores the connection in the app context."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # Allows accessing columns by name (row['id'])
    return db

@app.teardown_appcontext
def close_connection(exception):
    """Closes the database connection when the request ends."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    """
    PHASE 2: Data Engineering
    Initializes the database structure and loads data from CSV.
    """
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        
        # 1. Create Tables (Clean Code: Normalized Design)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS banks (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS branches (
                ifsc TEXT PRIMARY KEY,
                bank_id INTEGER,
                branch TEXT,
                address TEXT,
                city TEXT,
                district TEXT,
                state TEXT,
                FOREIGN KEY(bank_id) REFERENCES banks(id)
            )
        ''')
        
        # 2. Load and Normalize Data
        try:
            print("⏳ Loading data from CSV... this might take a moment.")
            df = pd.read_csv(CSV_FILE)
            
            # Insert Banks (Distinct list of banks)
            banks = df[['bank_id', 'bank_name']].drop_duplicates()
            cursor.executemany('INSERT OR IGNORE INTO banks (id, name) VALUES (?, ?)', 
                               banks.values.tolist())
            
            # Insert Branches (Details linked to bank_id)
            branches_df = df[['ifsc', 'bank_id', 'branch', 'address', 'city', 'district', 'state']]
            # Handle empty values (NaN) by replacing them with None (SQL NULL)
            branches_df = branches_df.where(pd.notnull(branches_df), None)
            cursor.executemany('INSERT OR IGNORE INTO branches VALUES (?, ?, ?, ?, ?, ?, ?)', 
                               branches_df.values.tolist())
            
            db.commit()
            print("✅ Database initialized successfully.")
        except FileNotFoundError:
            print(f"❌ Error: {CSV_FILE} not found. Please make sure the file is in the project folder.")
        except Exception as e:
            print(f"❌ Error initializing database: {e}")

# --- API Endpoints (PHASE 3) ---

@app.route('/', methods=['GET'])
def home():
    """Simple health check endpoint."""
    return jsonify({
        "status": "online",
        "message": "Welcome to the Bank API. Use /api/banks to start."
    })

@app.route('/api/banks', methods=['GET'])
def get_banks():
    """Returns a list of all banks."""
    cursor = get_db().cursor()
    cursor.execute('SELECT id, name FROM banks ORDER BY name')
    banks = cursor.fetchall()
    return jsonify([dict(row) for row in banks])

@app.route('/api/branches/<ifsc>', methods=['GET'])
def get_branch_details(ifsc):
    """Returns details for a specific branch by IFSC."""
    cursor = get_db().cursor()
    
    # SQL JOIN: Fetches branch details AND the matching bank name
    query = '''
        SELECT b.ifsc, b.branch, b.address, b.city, b.district, b.state, bk.name as bank_name
        FROM branches b
        JOIN banks bk ON b.bank_id = bk.id
        WHERE b.ifsc = ?
    '''
    cursor.execute(query, (ifsc.upper(),)) # Handle case-insensitivity
    row = cursor.fetchone()
    
    if row is None:
        abort(404, description=f"Branch with IFSC {ifsc} not found.")
        
    return jsonify(dict(row))

# Initialize the DB when the application starts
init_db()

if __name__ == '__main__':
    app.run(debug=True)