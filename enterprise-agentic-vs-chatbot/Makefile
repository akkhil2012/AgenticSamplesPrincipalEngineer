PYTHON ?= python
.PHONY: install seed run dashboard test lint
install:
	$(PYTHON) -m pip install -e '.[dev]'
seed:
	$(PYTHON) -m src.seed
run:
	$(PYTHON) -m uvicorn src.main:app --host 0.0.0.0 --port 8000
dashboard:
	$(PYTHON) -m streamlit run dashboard/app.py --server.port 8501 --browser.gatherUsageStats=false
test:
	$(PYTHON) -m pytest -q
lint:
	$(PYTHON) -m ruff check src dashboard tests scripts
	$(PYTHON) -m ruff format --check src dashboard tests scripts
