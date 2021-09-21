# ==============================================================================
# RUN WITH: bash setup.sh
# - Installs Flask, and Flask SQL Alchemy
# - Creates SQLITE3 Database
# - Inserts Dummy Data
#
# BY: Isaac Lehman
# ==============================================================================
# SETUP
pip3 -q install flask werkzeug flask_monitoringdashboard flask-sqlalchemy flask-admin markdown
echo "=============================================================================="
echo "PIP installs finished Succesfully!"
# CREATE DB
python3 -c 'from server import db, add_user, generate_password_hash;db.create_all();add_user("test@example.com", "admin", generate_password_hash("admin", "sha256"), privilege="ADMIN")'
echo "=============================================================================="
echo "DB Created Succesfully!"
echo "u: admin"
echo "p: admin"