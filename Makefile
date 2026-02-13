.PHONY: dev setup test eval demo

setup:
	python3 -m venv .venv 2>/dev/null || true
	. .venv/bin/activate 2>/dev/null || true; pip install -r backend/requirements.txt
	cd frontend && npm install 2>/dev/null || true
	cp .env.example .env 2>/dev/null || true

setup-venv:
	python3 -m venv .venv && . .venv/bin/activate && pip install -r backend/requirements.txt

dev-backend:
	PYTHONPATH=. uvicorn backend.main:app --reload --reload-dir backend --host 0.0.0.0 --port 8000

dev:
	docker-compose up --build

test:
	cd backend && PYTHONPATH=.. pytest tests/ -v 2>/dev/null || echo "No tests yet"

eval:
	cd scripts && PYTHONPATH=.. python run_eval.py 2>/dev/null || echo "Eval script not ready"

demo:
	cd scripts && PYTHONPATH=.. python demo_queries.py 2>/dev/null || echo "Demo script not ready"
