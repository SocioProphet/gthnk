# gthnk (c) Ian Dennis Miller

SHELL=/bin/bash
PROJECT_NAME=gthnk
MOD_NAME=gthnk

install:
	python setup.py install

requirements:
ifeq ($(OS),Windows_NT)
	easy_install -U mr.bob==0.1.2
endif
	pip install -r requirements.txt

develop:
	pip install -r .dev/requirements.txt

clean:
	rm -rf build dist *.egg-info src/*.egg-info
	find . -name '*.pyc' -delete
	find . -name __pycache__ -delete
	rm -f .coverage coverage.xml

server:
	mkdir -p var/log

	export SETTINGS=$$PWD/.dev/conf/dev.conf && \
	cd src/gthnk && \
		FLASK_ENV=development \
		FLASK_APP=server.py \
		flask run

shell:
	SETTINGS=$$PWD/.dev/conf/dev.conf bin/manage.py shell

test: clean
	SETTINGS=$$PWD/.dev/conf/testing.conf nosetests $(MOD_NAME) -c .dev/nose/test.cfg

single:
	SETTINGS=$$PWD/.dev/conf/testing.conf nosetests $(MOD_NAME) -c .dev/nose/test-single.cfg

db:
ifeq ($(OS),Windows_NT)
	set SETTINGS=%cd%\.dev\conf\dev-win.conf & python bin\manage.py init_db
	set SETTINGS=%cd%\.dev\conf\dev-win.conf & python bin\manage.py user_add --email "guest@example.com" --password "guest"
	set SETTINGS=%cd%\.dev\conf\dev-win.conf & python bin\manage.py user_add --email "admin@example.com" --password "aaa" --admin
else
	SETTINGS=$$PWD/.dev/conf/dev.conf bin/manage.py init_db
	SETTINGS=$$PWD/.dev/conf/dev.conf bin/manage.py user_add --username "guest" --password "guest"
endif

dropdb:
	SETTINGS=$$PWD/.dev/conf/dev.conf bin/manage.py drop_db

upgradedb:
	SETTINGS=$$PWD/.dev/conf/dev.conf bin/manage.py db upgrade

migratedb:
	SETTINGS=$$PWD/.dev/conf/dev.conf bin/manage.py db migrate

watch:
	watchmedo shell-command -R -p "*.py" -c 'echo \\n\\n\\n\\nSTART; date; \
		SETTINGS=$$PWD/.dev/conf/testing.conf nosetests $(MOD_NAME) \
		-c .dev/nose/test-single.cfg; date' .

docs:
	rm -rf build/sphinx
	SETTINGS=$$PWD/.dev/conf/testing.conf sphinx-build -b html docs build/sphinx

coverage:
	SETTINGS=$$PWD/.dev/conf/testing.conf nosetests --with-xcoverage \
		--cover-package=$(MOD_NAME) --cover-tests -c .dev/nose/test.cfg

lint:
	pylint src/gthnk

release:
	python setup.py sdist bdist_wheel
	# twine upload --config-file ~/.pypirc dist/*

.PHONY: clean install test server watch lint docs all single release homebrew develop coverage
