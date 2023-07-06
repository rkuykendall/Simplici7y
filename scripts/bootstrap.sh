python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
./scripts/migrate.sh
python manage.py createsuperuser
