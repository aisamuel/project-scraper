lint:
	@echo "Running flake8..."
	flake8 . --exclude=env,venv,.venv,migrations,__pycache__
	@echo "Running black..."
	black . --check --exclude '(env|venv|\.venv|migrations)'
	@echo "Running isort..."
	isort . --check-only --skip env --skip venv --skip .venv --skip migrations

format:
	black . --exclude '/(env|venv|\.venv|migrations)/'
	isort . --skip env --skip venv --skip .venv --skip migrations

