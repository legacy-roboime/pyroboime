# Some useful common actions
#

# Settings
# --------

PROJECT := pyroboime

# virtualenv config
VIRTUALENV := .virtualenv

# flake8 config
FLAKE8_EXCLUDES := \*_pb2.py
FLAKE8_OPTS := --exclude=$(FLAKE8_EXCLUDES) --ignore=E501 --format=pylint --statistics
FLAKE8_STRICT_OPTS := --exclude=$(FLAKE8_EXCLUDES) --format=pylint


# Targets
# -------

.PHONY: all
all: deps


# target to create the virtualenv, based on the presence
# of the activation script
.PHONY: virtualenv
VIRTUALENV_ACTIVATE := $(VIRTUALENV)/bin/activate
virtualenv: $(VIRTUALENV_ACTIVATE)
$(VIRTUALENV_ACTIVATE):
	@which virtualenv || (echo "virtualenv not found" && exit 1)
	@virtualenv --prompt=[$(PROJECT)] $(VIRTUALENV)


# install dependencies inside the virutalenv, naturally will
# require the virtualenv
.PHONY: deps
deps: virtualenv
	@. $(VIRTUALENV_ACTIVATE) && $(MAKE) pip-deps

# install dependencies specified on requirements.txt taking
# into account vialink's pip repository
.PHONY: pip-deps
pip-deps:
	@pip install -r requirements.txt

# wipe out the created virtualenv
.PHONY: clean
clean:
	@rm -rf $(VIRTUALENV)

# check PEP8 compliancy without max column limit
.PHONY: pep8
pep8:
	@flake8 $(FLAKE8_OPTS) roboime

# check PEP8 compliancy more strictly
.PHONY: pep8-strict
pep8-strict:
	@flake8 $(FLAKE8_STRICT_OPTS) roboime

# count the number of lines
.PHONY: count
count:
	@find roboime -type f -exec cat {} \; | wc -l
