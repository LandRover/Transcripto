clean:
	@rm -rf ./output
	@rm -f .coverage
	@rm -rf */__pycache__ */*.pyc __pycache__
	@find . -name "__pycache__" -type d -exec rm -r {} +
	@find . -name "*.pyc" -exec rm -f {} +

packages:
	@pip install -e .
