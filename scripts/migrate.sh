source venv/bin/activate
heroku pg:backups:capture --app simplici7y
python manage.py makemigrations
python manage.py migrate
