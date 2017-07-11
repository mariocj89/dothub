test:
	tox

release:
	python setup.py bdist_wheel upload -r pypi

.PHONY: test release
