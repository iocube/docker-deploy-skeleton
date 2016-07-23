# Introduction
This project is an example of how to setup and deploy a web application with docker and git post-receive hook, this is an attempt 
to make deployment process simple as push & forget for my pet projects.

As an example, I'll use dummy Flask application `app.py` alongside with mongodb nginx and gunicorn services.

So, how it suppose to work?  
You push your `master` branch to a remote repository (see [bare repository](https://git-scm.com/book/en/v2/Git-on-the-Server-Getting-Git-on-a-Server)) 
which is located on production server, once your commit is received, 
[post-receive](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks) hook will be executed and
 docker will start re-building your services according to your configuration in `docker-compose.yml` and `docker-compose.prod.yml`.

# Preparation
## Production Machine
Install [docker](https://docs.docker.com/engine/installation/linux/ubuntulinux/), [docker-compose](https://docs.docker.com/compose/install/) and git.

Create directory to hold our application source code, bare git repository where the code will be pushed to and directory for 
each service we will be using (nginx, gunicorn and mongodb) to store logs or any other related data:  

Our folder structure will look like this:
```
/srv/webapp
├── services
│   ├── gunicorn
│   ├── mongo
│   └── nginx
├── src
└── webapp.git
```

- `/srv/webapp/services` -- services that project depends on (nginx, gunicorn, mongo etc)
- `/srv/webapp/src` -- application source code.
- `/srv/webapp/webapp.git` -- git repository where the code will be pushed. once the code is pushed, `post-receive` script will be 
executed and docker build process will start.

`$ sudo mkdir /srv/webapp /srv/webapp/webapp.git /srv/webapp/src /srv/webapp/services/`  
`$ sudo mkdir /srv/webapp/services/mongo /srv/webapp/services/gunicorn /srv/webapp/services/nginx`  
`$ sudo chown -R owner:owner /srv/webapp`  
`$ cd /srv/webapp/webapp.git`  
`$ git init --bare`  

## Developer's Machine
This project includes an example of environment file `.env.example`,  create `.env.prod` based on the example.  
The purpose of this file is to store secrets, for example, database credentials, API keys and etc, it should not be
 in your git repository (use .gitignore to exclude them).  
Since production environment file is not included in your git repository we have to copy the file manually to the production server:
`$ scp .env.prod user@server.ip:/srv/webapp`  

Adding new remote git repository:  
`$ git remote add production user@server.ip:/srv/webapp/webapp.git`  
This repository is actually your production server, that's the reason we created `webapp.git`, your application source code will be pushed there.
 
Copy `post-receive` hook to your repository, make sure it is executable (+x) otherwise after you pushed your code nothing will happen:  
`$ scp post-receive user@server.ip:/srv/webapp/webapp.git/hooks`  

## Push & Build
In order to configure some of the services and to test it we will build our project and run it so that we can do
some initial configuration in the next section, for example, to create users in our database.

Let's start by switching to our `master` branch and pushing master to production.
```
$ git checkout master
$ git push production
```

This push will initiate execution of `post-receive` hook on server which looks like this:
```
#!/bin/bash

# checkout master branch
git --work-tree /srv/webapp/src --git-dir /srv/webapp/webapp.git/ checkout -f master

echo "Deploying commit: `git rev-parse HEAD`"

cd /srv/webapp/src
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
docker-compose logs
```

## Service configuration
### MongoDB
We will create admin user and a regular user with read/write permissions that is dedicated for the web application.
The following steps requires you to ssh into your production server.  

Create a new admin user  
NOTE: container id can be obtained by running `docker ps`.
```
$ docker exec -i -t <container_id> /bin/bash
$ mongo
> use admin
> db.createUser({user: "<admin_user>", pwd: "<strong_password>", roles: [ {role: "userAdminAnyDatabase", db: "admin"} ]})
db.auth(<admin_user>, <admin_password>)
```

Create a regular user dedicated for the database this application will talk to.  
NOTE: You must specify same credentials as in defined in .env.prod file (DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD).  
`$ use <database_name>`
`> db.createUser({user: "<user>", pwd: "<strong_password>", roles: [ {role: "readWrite", db: "<database_name>"} ]})`
i.e
`> db.createUser({user: "webappuser", pwd: "webapppassword", roles: [ {role: "readWrite", db: "webapp"} ]})`

## Commands
Commands you might find useful.

##### Making remote connection to MongoDB:
`$ mongo <container_ip>:<port>/<database_name> -u <username> -p <password>`

##### Creating containers:
```
$ docker-compose -f docker-compose.yml -f docker-compose.prod.yml create
$ docker-compose start
```
NOTE: make sure to specify needed docker-compose files with `-f` flag otherwise you might find that your configuration
is not applied.

## Possible Issues
gunicorn fails to start and exits with an error:
```
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
```
Might be problem with application source code, for example, it may contain syntax errors.  
Another reason, it can happen if environment file with all the credentials does not exist and then your database driver might
fail to connect to a database and exits with an error.  
Navigate to `/srv/webapp/services/gunicorn` and check logs there.