# Linux Server Configuration

## Application details
* IP: 54.93.187.195
* URL: http://ec2-54-93-187-195.eu-central-1.compute.amazonaws.com/
* SSH port: 2200

## Grader login
`ssh -i graderKey.pem grader@54.93.187.195 -p 2200`

## Steps performed for server setup
### Upgrade packages
`sudo apt-get upgrade`

### Create new user
* create new user with `sudo adduser grader`
* create directory `mkdir /home/grader/.ssh`
* generate new key pair and copy the public key into a file `/home/grader/.ssh/authorized_keys` (see [AWS documentation](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html#having-ec2-create-your-key-pair))
* set permissions `chmod 700 /home/grader/.ssh` and `chmod 644 /home/grader/.ssh/authorized_keys`
* grant sudo access to grader by creating a new file
`/etc/sudoers.d/grader` with the content `grader ALL=(ALL) NOPASSWD:ALL`

### Configure firewall
* configure ufw settings
```
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 2200/tcp
sudo ufw allow www
sudo ufw allow ntp
sudo ufw enable
```
* configure amazon lightsail firewall settings by adding custom application for ssh on port 2200
* configure `/etc/ssh/sshd_config` to listen on ports 2200, 80 and 123
* disable password login (`PasswordAuthentication no`) and root login (`PermitRootLogin no`) in `/etc/ssh/sshd_config`
* after restarting ssh `sudo service ssh restart`, a private key is needed to login

### Check timezone
* check `/etc/timezone` to see if timezone is set to Etc/UTC by default

### Install apache
* install apache `sudo apt-get install apache2`
* install mod_wsgi `sudo apt-get install libapache2-mod-wsgi-py3`
* configure apache by adding `WSGIScriptAlias / /var/www/app.wsgi` to the file `/etc/apache2/sites-enabled/000-default.conf`
* restart apache with new settings `sudo service apache2 restart`

### Setup database
* install postgresql
`sudo apt-get install postgresql`
* check if remote login is disabled in `sudo nano /etc/postgresql/9.1/main/pg_hba.conf`
* create database role `catalog` with rights to create a database (connect to postgresql as user `postgres`)
```
sudo su - postgres
psql
CREATE ROLE catalog WITH CREATEDB LOGIN ENCRYPTED PASSWORD "catalog";
```
* create database `tolearn` with `catalog` as owner
```
SET ROLE catalog;
CREATE DATABASE tolearn WITH OWNER catalog
```
### Prepare application for deployment
* create new file `/var/www/app.wsgi` with the following content:
```#!/usr/bin/env python3
import sys
sys.path.insert(0,"/var/www/ItemCatalog")
from application import app as application
```
* install missing packages
```
sudo apt install python3-pip
sudo apt-get install git
```
* clone application into the directory `/var/www/`
```
cd /var/www/
git clone https://github.com/ViviLearns2Code/ItemCatalog.git
```
* install python libraries
```
sudo pip3 install flask_httpauth
sudo pip3 install flask
sudo pip3 install sqlalchemy
sudo pip3 install oauth2client
sudo pip3 install httplib2
sudo pip3 install google-api-python-client
sudo pip3 install psycopg2
```
* change source code of app:
	* change sqlite engine uri `sqlite:///tolearn.db` to postgresql engine uri `postgresql://catalog:catalog@localhost/tolearn` in the two files `database_setup.py` and `application.py`
	* set `app.secret_key` at beginning of `application.py`
	* use absolute path to client secrets file `/var/www/ItemCatalog/json/client_secrets.json`
* setup database
```
cd /var/www/ItemCatalog/
python3 database_setup.py
```
* change google client secrets file: Add `http://ec2-54-93-187-195.eu-central-1.compute.amazonaws.com/` and `54.93.187.195` to list of allowed javascript origins in the google developer console
* download client secrets json file and replace the content of `/var/www/ItemCatalog/json/client_secrets.json` with the downloaded content

### Launch application
The app is now ready to use: http://ec2-54-93-187-195.eu-central-1.compute.amazonaws.com/

## Resources
* [AWS documentation](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html)
* Digital Ocean [[1]](https://www.digitalocean.com/community/tutorials/how-to-use-roles-and-manage-grant-permissions-in-postgresql-on-a-vps--2), [[2]](https://www.digitalocean.com/community/tutorials/how-to-secure-postgresql-on-an-ubuntu-vps)
* Udacity forums