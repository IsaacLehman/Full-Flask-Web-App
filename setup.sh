# ==============================================================================
# RUN WITH: bash setup.sh
# - Installs Flask, and Flask SQL Alchemy
# - Creates SQLITE3 Database
# - Inserts Dummy Data
#
# BY: Isaac Lehman
# ==============================================================================
# CREATE VIRTUAL ENVIROMENT
python3 -m venv FlaskApp
source FlaskApp/bin/activate
cd FlaskApp
echo "=============================================================================="
echo "Virtual enviroment created"
# CLONE THE REPO
git clone https://github.com/IsaacLehman/Full-Flask-Web-App.git
cd Full-Flask-Web-App
echo "=============================================================================="
echo "Repository cloned"
# SETUP
pip3 -q install flask werkzeug flask-sqlalchemy flask-admin markdown gunicorn pygments
echo "=============================================================================="
echo "PIP installs finished Succesfully!"
# CREATE DB
python3 -c 'from server import db, add_user, generate_password_hash;db.create_all();add_user("test@example.com", "admin", generate_password_hash("admin", "sha256"), privilege="ADMIN")'
echo "=============================================================================="
echo "DB Created Succesfully!"
echo "u: admin"
echo "p: admin"
echo "=============================================================================="
echo "Starting server..."
echo "=============================================================================="
python3 server.py
