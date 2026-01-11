# Bank branches API Service

i put together this REST API to serve up data for about 120,000 bank branches in India. i used Python, Flask and SQLite to build it.

# how it works:

this project is basically a bridge between a raw data file and the user who needs the info.

loading data: when you start the app, it reads a big CSV file that has all the raw banking data.

building the db: it converts that text data into a structured SQL database. i did this so searching and filtering happens way faster than just reading lines from a file.

serving requests: the Flask server listens for web requests. if you ask for details about a specific branch, it queries the database and sends back the result as JSON.

# the approach:

my goal was to code clean and keep the logic simple:

data normalization: the raw data had a lot of repetition, so i split it into two tables: banks and branches. this keeps the architecture clean and avoids duplicate text.

REST style: i stuck to standard REST principles. different resources have their own URLs and i used standard HTTP methods like GET to retrieve data.

SQLite database: i chose SQLite because it doesn't need a separate server installation. it makes the project really easy to set up locally but still lets me do complex stuff like joins.


## Setup Instructions

Follow these steps to run the project on your local machine.

1.  **Install Dependencies:**
    Open your terminal in the project folder and run:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the Server:**
    Start the application by running:
    ```bash
    python app.py
    ```

3.  **Verify the API:**
    Open your web browser and navigate to:
    `http://127.0.0.1:5000/api/banks`

4.  **Run Automated Tests:**
    To verify the system integrity, you can run the test suite:
    ```bash
    python test_app.py
    ```
