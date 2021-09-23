if [[ $1 == 'DEBUG' ]]; then
python3 server.py
else
gunicorn -w 4 wsgi:app
fi