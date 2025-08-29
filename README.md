# Employee Leave Management (FastAPI)

A backend service built with **FastAPI** for managing employee leaves, roles, and related operations.

---

## 📂 Project Structure

app/
├── api/ # API endpoints
│ └── api_v1/ # Versioned APIs
│ ├── deps.py # Dependencies
│ ├── deps_roles.py
├── core/ # Core configuration
├── crud/ # Database operations
├── models/ # SQLAlchemy models
├── schemas/ # Pydantic schemas
├── main.py # FastAPI entry point
logs/ # Log files
uploads/ # Uploaded files
requirements.txt # Project dependencies

yaml
Copy code

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/sohan418/leave-management-ui.git
cd employee-leave-management
2. Create & activate a virtual environment
bash
Copy code
python -m venv .venv
source .venv/bin/activate   # On Linux/Mac
.venv\Scripts\activate      # On Windows
3. Install dependencies
bash
Copy code
pip install -r requirements.txt
4. Setup environment variables
Create a .env file in the root directory:

env
Copy code
DATABASE_URL=postgresql://user:password@localhost:5432/leave_db
SECRET_KEY=your_secret_key
5. Run the application
bash
Copy code
uvicorn app.main:app --reload
The API will be available at: http://127.0.0.1:8000

📖 API Documentation
FastAPI provides interactive API docs:

Swagger UI → http://127.0.0.1:8000/docs

ReDoc → http://127.0.0.1:8000/redoc

🧪 Running Tests
bash
Copy code
pytest
📦 Deployment
To run in production:

bash
Copy code
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Optionally, you can containerize with Docker.

👨‍💻 Author
Sohan Bisht (@sohan418)
```
