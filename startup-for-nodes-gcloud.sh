#! /bin/bash
apt-get update
if [ -f /test ]; then
	exit 0
fi
cat <<EOF > /test
check
EOF

mkdir /distributed
cd /distributed
git clone https://github.com/sh4wn/distributed-ngs.git
git checkout postgreSQL
export LC_ALL=C
apt-get install -y erlang-nox python3-pip libpq-dev python-dev python-sqlalchemy postgresql postgresql-contrib language-pack-en
locale-gen en_US.UTF-8
service postgresql status

wget https://www.rabbitmq.com/releases/rabbitmq-server/v3.6.1/rabbitmq-server_3.6.1-1_all.deb
dpkg -i rabbitmq-server_3.6.1-1_all.deb
apt-get -y -f install
service rabbitmq-server restart
cd distributed-ngs/
export LC_ALL=C
python3 -m pip install aioamqp
python3 -m pip install sqlalchemy
python3 -m pip install psycopg2

sudo -u postgres createdb manager_server
sudo -u postgres psql -U postgres -d manager_server -c "alter user postgres with password 'manager';"
touch /testScriptDone