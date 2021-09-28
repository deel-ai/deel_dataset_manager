.PHONY: help prepare-dev test doc
.DEFAULT: help

help:
	@echo "make prepare-dev"
	@echo "       create and prepare development environment, use only once"
	@echo "make test"
	@echo "       run tests and linting on py36, py37, py38"
	@echo "make doc"
	@echo "       build Sphinx docs documentation"
	
prepare-dev:
	python3 -m pip install virtualenv
	python3 -m venv ddm_dev_env
	. ddm_dev_env/bin/activate && pip install --upgrade pip
	. ddm_dev_env/bin/activate && pip install -r requirements.txt
	. ddm_dev_env/bin/activate && pip install -r requirements_dev.txt	

test:
	. ddm_dev_env/bin/activate && tox 

doc:
	. ddm_dev_env/bin/activate && cd docs && make clean html && cd -
