test:
	tox

release:
	python -m pip install wheel
	rm -rf build dothub.egg-info dist
	python setup.py check --restructuredtext
	python setup.py bdist_wheel
	python setup.py sdist
	twine upload dist/* -r pypi
	rm -rf build dothub.egg-info dist

.PHONY: test release
