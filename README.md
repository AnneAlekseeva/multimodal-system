venv\Scripts\activate
uvicorn backend.main:app --reload
cd frontend
npm run dev
npm install -g cline