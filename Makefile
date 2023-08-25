
PYTHON_1:=venv/bin/python
PYTHON_2:=python

ifeq '$(findstring ;,$(PATH))' ';'
    detected_OS:=Windows

	ifeq ($(exist $(PYTHON_1) && echo yes),yes)
		PYTHON=$(PYTHON_1)
	else
		PYTHON=$(PYTHON_2)
	endif
else
	detected_OS:=Linux

	ifeq ($(shell test -f $(PYTHON_1) && echo -n yes),yes)
		PYTHON=$(PYTHON_1)
	else
		PYTHON=$(PYTHON_2)
	endif
endif

help:
	$(PYTHON) fec.py --help

doctest:
	$(PYTHON) -m pytest --doctest-modules fec.py

t: doctest
