# Some useful common actions
#

# virtualenv config
VIRTUALENV := .virtualenv

# flake8 config
FLAKE8_EXCLUDES := \*_pb2.py
FLAKE8_OPTS := --exclude=$(FLAKE8_EXCLUDES) --ignore=E501 --format=pylint --show-pep8
FLAKE8_STRICT_OPTS := --exclude=$(FLAKE8_EXCLUDES) --format=pylint


.PHONY: all
all: deps


.PHONY: virtualenv
VIRTUALENV_ACTIVATE := $(VIRTUALENV)/bin/activate
virtualenv: $(VIRTUALENV_ACTIVATE)
$(VIRTUALENV_ACTIVATE):
	@which virtualenv || (echo "virtualenv not found" && exit 1)
	@virtualenv $(VENV)


.PHONY: deps
deps: virtualenv
	@. $(VIRTUALENV_ACTIVATE) && pip install -r requirements.txt


.PHONY: pep8
pep8:
	@flake8 $(FLAKE8_OPTS) roboime


.PHONY: pep8-strict
pep8-strict:
	@flake8 $(FLAKE8_STRICT_OPTS) roboime
