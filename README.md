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
