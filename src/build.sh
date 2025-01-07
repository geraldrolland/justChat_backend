set -o errexit
pip install -r ./src/requirements.txt
python ./src/manage.py collectstatic --no-input
python ./src/manage.py migrates
sudo apt-get install -y redis-server
sudo systemctl start redis-server
