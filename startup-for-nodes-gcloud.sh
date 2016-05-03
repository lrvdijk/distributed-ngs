#! /bin/bash
apt-get update
if [ -f /test ]; then
	exit 0
fi
cat <<EOF > /test
check
EOF
# Redirect stdout ( > ) into a named pipe ( >() ) running "tee"
exec > >(tee -i logfile.txt)
exec 2>&1

mkdir /distributed

cd /distributed
mkdir dataFiles

git clone https://github.com/sh4wn/distributed-ngs.git
#TMP go to postgresql branch
cd distributed-ngs
git checkout postgreSQL

IP="$(ip -4 addr show ens4 | grep -oP '(?<=inet\s)\d+(\.\d+){3}')"
USED="$(df / | grep / | cut -d ' ' -f9)"
TOTAL="$(df / | grep / | cut -d ' ' -f12)"
FREE=$(expr $TOTAL - $USED)
echo "IP=$IP" >> "node_settings.py"
echo "TOTAL=$TOTAL" >> "node_settings.py"
echo "FREE=$FREE" >> "node_settings.py"

export LC_ALL=C
apt-get install -y erlang-nox python3-pip libpq-dev python-dev python-sqlalchemy postgresql postgresql-contrib
locale-gen en_US.UTF-8
cd ..
wget https://www.rabbitmq.com/releases/rabbitmq-server/v3.6.1/rabbitmq-server_3.6.1-1_all.deb
dpkg -i rabbitmq-server_3.6.1-1_all.deb
apt-get -y -f install
cd distributed-ngs/
export LC_ALL=C
echo "LC_ALL=en_GB.utf8" >> /etc/environment
python3 -m pip install aioamqp
python3 -m pip install sqlalchemy
python3 -m pip install psycopg2

echo "restarting services"
service rabbitmq-server start
service postgresql restart
service postgresql start
echo "done restarting services"


sudo -u postgres createdb manager_server
sudo -u postgres psql -U postgres -d manager_server -c "alter user postgres with password 'manager';"

echo "restarting services"
service rabbitmq-server start
service postgresql restart
service postgresql start
/etc/init.d/postgresql restart
echo "done restarting services"

sleep 20

sudo -u postgres createdb manager_server
sudo -u postgres psql -U postgres -d manager_server -c "alter user postgres with password 'manager';"
python3 add_test_data.py

touch /testScriptDone

#// listen_addresses='localhost' 