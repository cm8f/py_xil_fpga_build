all: unittest

unittest:
	python3 -m unittest discover -v -s ./tests -p '*test*.py'

lint:
	flake8 . --extend-exclude=dist,build --show-source --statistics