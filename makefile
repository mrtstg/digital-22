.PHONY: tests clean run migrate

venv:
	python3.10 -m venv ./venv
	. ./venv/bin/activate; pip install -r requirements.txt

clean: venv
	rm -rf ./venv
	find -iname "*.pyc" -delete

tests: venv
	set -a;	. ./.env.test; export PYTHONPATH=./source:./; . ./venv/bin/activate; cd ./source; pytest ../tests

run: venv
	set -a;	. ./.env; . ./venv/bin/activate; cd ./source; python main.py

migrate: venv
	set -a; . ./.env; . ./venv/bin/activate; alembic upgrade head
