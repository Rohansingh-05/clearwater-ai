# Water Quality Index Using Artificial Intelligence

Full-stack educational project based on the supplied PPT. Includes all five inputs (pH, dissolved oxygen, turbidity, TDS, contamination indicators), traditional weighted WQI, Decision Tree and Random Forest predictions, four categories, confidence, model evaluation, history, and CSV export.

## Important assumptions
The PPT does not specify a WQI formula, weights, category thresholds, contamination encoding, or labelled dataset. `backend/app/wqi.py` therefore contains a transparent demonstration formula and configurable demonstration bands, not an official WHO/CPCB formula. The bundled dataset is synthetic; its accuracy is not real-world evidence. Contamination is encoded as 0=no indicator reported, 1=suspected, 2=detected. Do not use this application to certify drinking-water safety.

## Run backend (Python 3.10+)
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m app.train_model
uvicorn app.main:app --reload
```
API docs: http://127.0.0.1:8000/docs

## Run frontend (Node 18+)
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:5173.

## Included
- WQI weighted score with visible parameter sub-scores
- Decision Tree + Random Forest classifier, confidence and held-out metrics
- SQLite analysis history
- PPT illustrative sample preloaded: pH 6.4, DO 4.2 mg/L, turbidity 8 NTU, TDS 720 mg/L
- CSV report export and responsible-use notices

Before real-world use, choose and validate an accepted WQI methodology, confirm local standards with qualified experts, and train/test on representative laboratory-labelled data.
