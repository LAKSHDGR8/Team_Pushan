.PHONY: first run, run, git

first:
	@echo "Installing requirements..."
	pip install -r requirements.txt
	@echo "Starting application..."
	python3 dbms_Laksh/app.py

run:
	@echo "Starting application..."
	python3 dbms_Laksh/app.py

git:
	@echo "Auto add..."
	git add .
	@echo "Auto commit..."
	git commit -m "Auto-commit"
	@echo "Auto push"
	git push origin main
