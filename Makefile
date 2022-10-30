default: run

lint:
	mypy src --strict --implicit-reexport

run:
	@sh -c "cd src && python3 -m main"

deps:
	pip install -r requirements.txt

savedeps:
	pip freeze > requirements.txt

clean:
	@sh -c "./scripts/clean.sh"

cleanrun: clean run

.PHONY: pyenv