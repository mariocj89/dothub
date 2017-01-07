test:
	tox

release:
	python setup.py sdist upload -r pypi

.PHONY: test release
