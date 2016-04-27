import os

err = os.system("service postgresql restart")
print(err)
err = os.system("sudo -u postgres createdb manager_server")
print(err)
err = os.system("sudo -u postgres psql -U postgres -d manager_server -c \"alter user postgres with password 'manager';\"")
print(err)