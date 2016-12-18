test:
	python -m pytest tests

release:
	python setup.py sdist upload

.PHONY: test release
