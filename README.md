# docker-deploy-skeleton

#### Preparation
Install docker and docker-compose.
`$ sudo mkdir /srv/webapp /srv/webapp/webapp.git /srv/webapp/src /srv/webapp/services/ /srv/webapp/services/mongo /srv/webapp/services/gunicorn`
`$ sudo chown -R owner:owner /srv/webapp`
`$ cd /srv/webapp/webapp.git`
`$ git init --bare`
`$ scp .env.prod user@server.ip:/srv/webapp`
`$ git remote add production user@server.ip:/srv/webapp/webapp.git`
`$ scp post-receive user@server.ip:/srv/webapp/webapp.git/hooks`

##### Database
The following steps requires you to ssh into your server.
We will create admin user and a regular user with read/write permissions that is dedicated for the web application.

Create a new admin user
`$ docker exec -i -t <container_id> /bin/bash`
`$ mongo`
`> use admin`
`> db.createUser({user: "<admin_user>", pwd: "<strong_password>", roles: [ {role: "userAdminAnyDatabase", db: "admin"} ]})`

Create a regular (not an admin) user dedicated for the database this application will talk to.
NOTE: You must specify same credentials as in defined in .env.prod file (DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD).
`db.auth(<admin_user>, <admin_password>)`
`$ use <database_name>`
`> db.createUser({user: "<user>", pwd: "<strong_password>", roles: [ {role: "readWrite", db: "<database_name>"} ]})`
