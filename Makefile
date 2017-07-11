test:
	tox

release:
	rm -rf build dothub.egg-info dist
	python setup.py bdist_wheel upload -r pypi

.PHONY: test release
