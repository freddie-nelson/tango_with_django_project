del db.sqlite3
python manage.py makemigrations rango
python manage.py migrate
python manage.py createsuperuser --username freddie --email freddie@freddienelson.co.uk
python populate_rango.py