install:
	pip install .

test:
	pytest tests

setup_dev:
	pip install -r requirements_dev.txt

build:
	python setup.py sdist

lint:
	pylint sclib tests
