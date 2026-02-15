VENV ?= .venv
PYTHON ?= $(VENV)/bin/python
PIP ?= $(VENV)/bin/pip

.PHONY: venv bootstrap deps deps-upgrade check-venv run-curvature run-ricci run-reliability run-all quality

venv:
	python3 -m venv $(VENV)

bootstrap: venv
	$(PYTHON) -m pip install --upgrade pip
	$(PIP) install -r requirements.txt

deps: bootstrap

deps-upgrade: venv
	$(PYTHON) -m pip install --upgrade pip
	$(PIP) install --upgrade -r requirements.txt

check-venv:
	@test -x "$(PYTHON)" || (echo "Missing $(PYTHON). Run 'make bootstrap' first."; exit 1)

run-curvature: check-venv
	$(PYTHON) src/multiple_spatial_curvature.py

run-ricci: check-venv
	$(PYTHON) src/ollivier_ricci.py

run-reliability: check-venv
	$(PYTHON) src/curvature_reliability_gate.py

run-all: run-curvature run-ricci run-reliability

quality:
	bash scripts/run_full_quality.sh
