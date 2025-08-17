# New_erp_setup

# Manufacturing ERP System

A simple ERP system for a manufacturing company built with Python, Flask, and PostgreSQL.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd erp_manufacturing
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Set up the PostgreSQL database:**
    - Create a new database (e.g., `erp_manufacturing`).
    - Update the database credentials in `utils/config.py`.
    - Run the `schema.sql` script to create the tables.

4.  **Run the application:**

    export FLASK_APP=app.py
    ```bash
    flask run
    ```
    The application will be available at `http://127.0.0.1:5000`.