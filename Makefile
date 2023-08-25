

_doctest:
	venv/bin/python -m pytest --doctest-modules fec.py

doctest:
	python -m pytest --doctest-modules fec.py

t: _doctest
