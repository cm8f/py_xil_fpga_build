all: unittest

unittest:
	python3 -m unittest discover -v -s ./tests -p '*test*.py'