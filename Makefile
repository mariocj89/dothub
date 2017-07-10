test:
	tox

release:
	python setup.py sdist_wheel upload -r pypi

.PHONY: test release
