test:
	tox

release:
	FORCE_PANDOC_GENERATION='y' python setup.py sdist upload -r pypi

.PHONY: test release
