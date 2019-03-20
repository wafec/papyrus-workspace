Examples:

  Generate tests folder:
    python statemutest.py param params tests

  Generate StateMutest's:
    # without saving
    python statemutest.py statemutest tests 1 --clean
    python statemutest.py statemutest tests 4

    # with saving
    python statemutest.py statemutest tests 1 --clean --app app.log
    python statemutest.py statemutest tests 4 --app app.log