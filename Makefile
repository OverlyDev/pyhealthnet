# define the name of the virtual environment directory
VENV := venv

# default target, when make executed without arguments
all: $(VENV)

# install required packages from .txt files
$(VENV): $(VENV)/bin/activate
	$(VENV)/bin/pip3 install pip-tools
	$(VENV)/bin/pip-sync pip/*.txt

# shortcut target
$(VENV)/bin/activate:
	python3 -m venv $(VENV)

# generate requirements .txt files
reqs:
	$(VENV)/bin/pip-compile --resolver=backtracking pip/requirements.in
	$(VENV)/bin/pip-compile --resolver=backtracking pip/dev-requirements.in
	$(VENV)/bin/pip-compile --resolver=backtracking pip/client-requirements.in
	$(VENV)/bin/pip-compile --resolver=backtracking pip/server-requirements.in

# upgrade requirements versions
reqs_upgrade:
	$(VENV)/bin/pip-compile --resolver=backtracking --upgrade pip/requirements.in
	$(VENV)/bin/pip-compile --resolver=backtracking --upgrade pip/dev-requirements.in
	$(VENV)/bin/pip-compile --resolver=backtracking --upgrade pip/client-requirements.in
	$(VENV)/bin/pip-compile --resolver=backtracking --upgrade pip/server-requirements.in

# formatters
format:
	$(VENV)/bin/black src
	$(VENV)/bin/importanize src

# run the client
run_client: format
	$(VENV)/bin/python3 -m src.client.main

# run the server
run_server: format
	$(VENV)/bin/uvicorn --app-dir src/server main:app --reload

# delete the venv
clean:
	rm -rf $(VENV)

# build the client docker image
docker_client:
	rm -rf docker/_context
	mkdir docker/_context
	cp docker/Dockerfile.client docker/_context/.
	cp docker/entrypoint-client.sh docker/_context/.
	$(VENV)/bin/pip-compile --resolver=backtracking pip/requirements.in pip/client-requirements.in --output-file docker/_context/requirements.txt
	cp -r src/client docker/_context/.
	cd docker/_context; docker build -t overlydev/pyhealthnet-client:latest -f Dockerfile.client .

# build the server docker image
docker_server:
	rm -rf docker/_context
	mkdir docker/_context
	cp docker/Dockerfile.server docker/_context/.
	cp docker/entrypoint-server.sh docker/_context/.
	$(VENV)/bin/pip-compile --resolver=backtracking pip/requirements.in pip/server-requirements.in --output-file docker/_context/requirements.txt
	cp -r src/server docker/_context/.
	cd docker/_context; docker build -t overlydev/pyhealthnet-server:latest -f Dockerfile.server .

test_models:
	$(VENV)/bin/python3 src/models/models.py

test_args:
	$(VENV)/bin/python3 src/models/args.py --help

.PHONY: all venv reqs reqs_upgrade format run_client run_server clean docker_client docker_server test_models