# Feel free to change the following variables
export YourUsername = ''
export PORTFOLIO_ID = 1
export TRIG_UPDATE_WEIGHTS = 1
export TRIG_METH_EXP = 1
export DB_USERNAME = %DB_USERNAME
export DB_PASSWORD = %DB_PASSWORD 
export DB_HOST = %DB_HOST
export DB_PORT = %DB_PORT
export DB_NAME = %DB_NAME

install-lin:
	@echo "Downloading and installing Python Poetry"
	curl -sSL https://install.python-poetry.org | python3 -
	poetry env use $(shell which python3.13)
	poetry install

install-win:
# using powershell
	(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
# Add Poetry to PATH
	$(userPath) = [Environment]::GetEnvironmentVariable('Path', 'User')
	$(newPath) = $userPath + ";C:\Users\$(YourUsername)\AppData\Roaming\Python\Scripts"
	[Environment]::SetEnvironmentVariable('Path', $(newPath), 'User')

# Verify installation
	poetry --version

test:
	poetry run pytest tests/

lint:
	poetry run ruff check --fix .

format:
	poetry run ruff format .

run-one-uc:
	poetry run python -m app $(PORTFOLIO_ID) \
						  	 $(TRIG_UPDATE_WEIGHTS) \ 
						  	 $(TRIG_METH_EXP) \
						  	 $(DB_USERNAME) \
						  	 $(DB_PASSWORD) \ 
						  	 $(DB_HOST) \
							 $(DB_PORT) \
							 $(DB_NAME)

all: lint format test run-one-uc