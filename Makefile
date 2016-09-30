# Some useful common actions
#

# Settings
# --------

PROJECT := pyroboime

MAIN ?= ./intel
CORE ?= roboime-next-gui
CORE_FLAGS ?= -p

ifdef AGAINST
CORE_CMD := $(CORE) -b '$(MAIN)' -y $(AGAINST) $(CORE_FLAGS)
else
CORE_CMD := $(CORE) -b '$(MAIN)' $(CORE_FLAGS)
endif

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

.PHONY: run
run:
	@echo Running "'"$(CORE_CMD)"'"
	@source $(VIRTUALENV_ACTIVATE) && $(CORE_CMD)


# target to create the virtualenv, based on the presence
# of the activation script
.PHONY: virtualenv
VIRTUALENV_ACTIVATE := $(VIRTUALENV)/bin/activate
virtualenv: $(VIRTUALENV_ACTIVATE)
$(VIRTUALENV_ACTIVATE):
	@which virtualenv || (echo "virtualenv not found" && exit 1)
	@virtualenv --python=python3 --prompt=[$(PROJECT)] $(VIRTUALENV)


# install dependencies inside the virutalenv, naturally will
# require the virtualenv
.PHONY: deps
deps: virtualenv
	@source $(VIRTUALENV_ACTIVATE) && $(MAKE) pip-deps

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
	@echo All good!!

# check PEP8 compliancy more strictly
.PHONY: pep8-strict
pep8-strict:
	@flake8 $(FLAKE8_STRICT_OPTS) roboime

# count the number of lines
.PHONY: lc
lc:
	@find roboime -type f -name \*.py  -exec cat {} \; | wc -l
