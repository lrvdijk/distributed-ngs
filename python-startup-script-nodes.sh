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
echo "IP='$IP'" >> "node_settings.py"
echo "TOTAL=$TOTAL" >> "node_settings.py"
echo "FREE=$FREE" >> "node_settings.py"

export LC_ALL=C
apt-get install -y erlang-nox python3-pip libpq-dev python-dev python-sqlalchemy postgresql postgresql-contrib
locale-gen en_US.UTF-8
apt-get -y -f install
cd distributed-ngs/
export LC_ALL=C
echo "LC_ALL=en_GB.utf8" >> /etc/environment
python3 -m pip install aioamqp
python3 -m pip install sqlalchemy
python3 -m pip install psycopg2

python3 register-data-node.py

touch /testScriptDone

#// listen_addresses='localhost' 