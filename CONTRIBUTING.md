Contributions are welcomed. Just follow the same style and common sense

# Running tests
Install and run tox

# Publishing a new version
```bash
python3 setup.py sdist_wheel
python2 setup.py sdist_wheel
python3 -m twine upload dist/*
```

