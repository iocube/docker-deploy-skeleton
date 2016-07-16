# docker-deploy-skeleton

#### Preparation
Install docker and docker-compose.
`$ sudo mkdir /srv/webapp /srv/webapp/webapp.git /srv/webapp/src /srv/webapp/services/ /srv/webapp/services/mongo /srv/webapp/services/gunicorn /srv/webapp/services/nginx`
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
`db.auth(<admin_user>, <admin_password>)`

Create a regular (not an admin) user dedicated for the database this application will talk to.
NOTE: You must specify same credentials as in defined in .env.prod file (DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD).
`$ use <database_name>`
`> db.createUser({user: "<user>", pwd: "<strong_password>", roles: [ {role: "readWrite", db: "<database_name>"} ]})`
i.e
`> db.createUser({user: "webappuser", pwd: "webapppassword", roles: [ {role: "readWrite", db: "webapp"} ]})`

Example: Remote connection to mongo
$ mongo <container_ip>:<port>/<database_name> -u <username> -p <password>

##### Issues
gunicorn failed to start.
`
web_1    | Traceback (most recent call last):
web_1    |   File "/usr/local/lib/python3.5/site-packages/gunicorn/arbiter.py", line 196, in run
web_1    |     self.sleep()
web_1    |   File "/usr/local/lib/python3.5/site-packages/gunicorn/arbiter.py", line 346, in sleep
web_1    |     ready = select.select([self.PIPE[0]], [], [], 1.0)
web_1    |   File "/usr/local/lib/python3.5/site-packages/gunicorn/arbiter.py", line 231, in handle_chld
web_1    |     self.reap_workers()
web_1    |   File "/usr/local/lib/python3.5/site-packages/gunicorn/arbiter.py", line 506, in reap_workers
web_1    |     raise HaltServer(reason, self.WORKER_BOOT_ERROR)
web_1    | gunicorn.errors.HaltServer: <HaltServer 'Worker failed to boot.' 3>
web_1    |
web_1    | During handling of the above exception, another exception occurred:
web_1    |
web_1    | Traceback (most recent call last):
web_1    |   File "/usr/local/bin/gunicorn", line 11, in <module>
web_1    |     sys.exit(run())
web_1    |   File "/usr/local/lib/python3.5/site-packages/gunicorn/app/wsgiapp.py", line 74, in run
web_1    |     WSGIApplication("%(prog)s [OPTIONS] [APP_MODULE]").run()
web_1    |   File "/usr/local/lib/python3.5/site-packages/gunicorn/app/base.py", line 192, in run
web_1    |     super(Application, self).run()
web_1    |   File "/usr/local/lib/python3.5/site-packages/gunicorn/app/base.py", line 72, in run
web_1    |     Arbiter(self).run()
web_1    |   File "/usr/local/lib/python3.5/site-packages/gunicorn/arbiter.py", line 218, in run
web_1    |     self.halt(reason=inst.reason, exit_status=inst.exit_status)
web_1    |   File "/usr/local/lib/python3.5/site-packages/gunicorn/arbiter.py", line 331, in halt
web_1    |     self.stop()
web_1    |   File "/usr/local/lib/python3.5/site-packages/gunicorn/arbiter.py", line 381, in stop
web_1    |     time.sleep(0.1)
web_1    |   File "/usr/local/lib/python3.5/site-packages/gunicorn/arbiter.py", line 231, in handle_chld
web_1    |     self.reap_workers()
web_1    |   File "/usr/local/lib/python3.5/site-packages/gunicorn/arbiter.py", line 506, in reap_workers
web_1    |     raise HaltServer(reason, self.WORKER_BOOT_ERROR)
web_1    | gunicorn.errors.HaltServer: <HaltServer 'Worker failed to boot.' 3>
`
Might be problem with source code (errors).
Also, it can happen if env file with all credentials does not exist and then database might
fail to connect.
Check logs in /srv/webapp/services/gunicorn.

When experimenting be sure to specify needed docker-compose files with `-f` flag when creating containers:
`$ docker-compose -f docker-compose.yml -f docker-compose.prod.yml create`
`$ docker-compose start`
