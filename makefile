
revision: 
	alembic revision --autogenerate -m=$(ARGS)

upgrade:
	alembic upgrade head

start:
	python -m app

up:
	docker-compose up --force-recreate --build -d

stop:
	docker-compose stop
