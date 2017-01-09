test:
	tox

release:
	python -c "import pandoc"
	python setup.py sdist upload -r pypi

.PHONY: test release
