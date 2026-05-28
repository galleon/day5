.DEFAULT_GOAL := default
export VIRTUAL_ENV := $(CURDIR)/.venv310
PYTHON := $(CURDIR)/.venv310/bin/python
STREAMLIT := $(CURDIR)/.venv310/bin/streamlit

#################### STREAMLIT ####################
run_local:
	$(STREAMLIT) run app/app.py

#################### DOCKER ####################
run:
	docker compose up --build

docker_build:
	docker build -t day5-streamlit:dev .

docker_down:
	docker compose down

##################### CLEANING #####################
clean:
	@rm -f */version.txt
	@rm -f .coverage
	@rm -fr **/__pycache__ **/*.pyc
	@rm -fr **/build **/dist
	@rm -fr proj-*.dist-info
	@rm -fr proj.egg-info
	@rm -f **/.DS_Store
	@rm -f **/*Zone.Identifier
	@rm -f **/.ipynb_checkpoints

default: run
