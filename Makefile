clean:
	@rm -rf ./output
	@rm -f .coverage
	@rm -rf */__pycache__ */*.pyc __pycache__
	@find . -name "__pycache__" -type d -exec rm -r {} +
	@find . -name "*.pyc" -exec rm -f {} +

run:
	@python -m transcripto --telegram-bot

build:
	@pip install -e .

docker_build:
	@docker build -t transcripto-app .

docker_run:
	@docker run -d \
		--name transcripto-bot \
		-v $$(pwd)/output:/app/output \
		-v $$(pwd)/.env:/app/.env \
		--gpus all \
		--env-file .env \
		transcripto-app python -m transcripto --telegram-bot

docker_up:
	@docker-compose up -d
