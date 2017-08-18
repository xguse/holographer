.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help
SHELL := /bin/bash


#################################################################################
# CONDA                                                                         #
#################################################################################

CONDA_ENV_NAME = holographer
CONDA_ROOT = $(shell conda info --root)
CONDA_ENV_DIR = $(CONDA_ROOT)/envs/$(CONDA_ENV_NAME)
CONDA_ENV_PY = $(CONDA_ENV_DIR)/bin/python

error_if_active_conda_env:
ifeq (True,$(PROJECT_CONDA_ACTIVE))
$(error "This project's conda env is active." )
endif

serve_nb:
	source activate $(CONDA_ENV_NAME); \
	jupyter notebook --notebook-dir dev/notebooks


uninstall: error_if_active_conda_env uninstall_conda_env


install_conda_env:
ifeq ($(CONDA_ENV_PY), $(shell which python))
	@echo "Project conda env already installed."
else
	conda create -n $(CONDA_ENV_NAME) --file requirements_conda_env.txt --yes  && \
	source activate $(CONDA_ENV_NAME) && \
	python -m ipykernel install --sys-prefix --name $(CONDA_ENV_NAME) --display-name "$(CONDA_ENV_NAME)" && \
	pip install -e .
endif


uninstall_conda_env: error_if_active_conda_env
	rm -rf $(CONDA_ENV_DIR)

#################################################################################
# dev                                                                           #
#################################################################################
clean-dev-targets:
	rm -rf dev/testing/targets/*


#################################################################################
# Original                                                                      #
#################################################################################


define BROWSER_PYSCRIPT
import os, webbrowser, sys
try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT
BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts


clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/

lint: ## check style with flake8
	flake8 holographer tests

test: ## run tests quickly with the default Python
	py.test


test-all: ## run tests on every Python version with tox
	tox

coverage: ## check code coverage quickly with the default Python
	coverage run --source holographer -m pytest
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

docs: ## generate Sphinx HTML documentation, including API docs
	rm -f docs/holographer.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ holographer
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

servedocs: docs ## compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

release: clean ## package and upload a release
	python setup.py sdist upload
	python setup.py bdist_wheel upload

dist: clean ## builds source and wheel package
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

install: clean ## install the package to the active Python's site-packages
	python setup.py install
