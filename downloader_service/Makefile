install:
	pip install -r downloader_service/requirements.txt
	pip install -r tests/requirements-test.txt

test-unit:
	pytest tests/unit

test-integration:
	pytest tests/integration

test-e2e:
	pytest tests/e2e

coverage:
	pytest --cov=downloader_service --cov-report=xml --cov-report=html

all-tests: test-unit test-integration test-e2e coverage
