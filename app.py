import sqlite3
import pandas as pd
from flask import Flask, jsonify, g, abort

DATABASE = 'bank_data.db'
CSV_FILE = 'bank_branches.csv'

app = Flask(__name__)



def get_db():
    """connects to the database and stores the connection in the app context."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  
    return db

@app.teardown_appcontext
def close_connection(exception):
    """closes the database connection when the request ends."""
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
        
        try:
            print("loading data from CSV....")
            df = pd.read_csv(CSV_FILE)
            
            banks = df[['bank_id', 'bank_name']].drop_duplicates()
            cursor.executemany('INSERT OR IGNORE INTO banks (id, name) VALUES (?, ?)', 
                               banks.values.tolist())
            
            branches_df = df[['ifsc', 'bank_id', 'branch', 'address', 'city', 'district', 'state']]
            branches_df = branches_df.where(pd.notnull(branches_df), None)
            cursor.executemany('INSERT OR IGNORE INTO branches VALUES (?, ?, ?, ?, ?, ?, ?)', 
                               branches_df.values.tolist())
            
            db.commit()
            print("DB initialized")
        except FileNotFoundError:
            print(f"Error: {CSV_FILE} not found. Please make sure the file is in the project folder.")
        except Exception as e:
            print(f"Error initializing database: {e}")


@app.route('/', methods=['GET'])
def home():
    """Simple health check endpoint."""
    return jsonify({
        "status": "online",
        "message": "welcome to the bank API. Use /api/banks to start."
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
    
    query = '''
        SELECT b.ifsc, b.branch, b.address, b.city, b.district, b.state, bk.name as bank_name
        FROM branches b
        JOIN banks bk ON b.bank_id = bk.id
        WHERE b.ifsc = ?
    '''
    cursor.execute(query, (ifsc.upper(),)) # handling case insensitivity
    row = cursor.fetchone()
    
    if row is None:
        abort(404, description=f"Branch with IFSC {ifsc} not found.")
        
    return jsonify(dict(row))

init_db()

if __name__ == '__main__':
    app.run(debug=True)
