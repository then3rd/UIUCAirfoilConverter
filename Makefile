VENV		  = .venv
VENV_BIN	  = $(VENV)/bin
VENV_PYTHON	  = $(VENV_BIN)/python3
SYSTEM_PYTHON = $(or $(shell which python3), $(shell which python))

$(VENV_PYTHON):
	$(SYSTEM_PYTHON) -m venv $(VENV)
	$(VENV_PYTHON) -m pip install --upgrade pip

help: ## Display this help output
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Environment
install: $(VENV_PYTHON) ## Makes venv and installs requirements using pip
	$(VENV_PYTHON) -m pip install -r requirements.txt

clean: ## Clean venv
	rm -rf $(VENV)

hooks: venv ## Install pre-commit git hooks
	$(VENV_BIN)/pre-commit install
