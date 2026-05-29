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

#################### CLOUD RUN ####################
deploy_api:
	gcloud run deploy taxifare-api \
		--image ${GAR_IMAGE}:dev \
		--project ${GCP_PROJECT} \
		--region ${GCP_REGION} \
		--memory ${GAR_MEMORY} \
		--set-env-vars MODEL_TARGET=${MODEL_TARGET},BUCKET_NAME=${BUCKET_NAME},GCP_PROJECT=${GCP_PROJECT},DATA_SIZE=${DATA_SIZE},CHUNK_SIZE=${CHUNK_SIZE} \
		--allow-unauthenticated

# Fetch the live Cloud Run URL and write it to .streamlit/secrets.toml
# so the Streamlit app picks it up both locally and on Streamlit Cloud
streamlit_secrets:
	@mkdir -p .streamlit
	@URL=$$(gcloud run services describe taxifare-api \
		--project ${GCP_PROJECT} \
		--region ${GCP_REGION} \
		--format 'value(status.url)') && \
	echo "API_URL = \"$$URL\"" > .streamlit/secrets.toml && \
	echo "Written to .streamlit/secrets.toml: API_URL = $$URL" && \
	echo "" && \
	echo "→ Copy the line above into Streamlit Cloud: App settings > Secrets"

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
