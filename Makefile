

doctest:
	venv/bin/python -m pytest --doctest-modules fec.py

t: doctest
