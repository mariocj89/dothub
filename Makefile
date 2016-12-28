test:
	python -m pytest tests

release:
	python setup.py sdist upload -r pypi

.PHONY: test release
