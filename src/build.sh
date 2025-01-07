set -o erroexit

pip install -r requirementts.txt
python manage.py collectstatic --no-input
python manage.py migrate