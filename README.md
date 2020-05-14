# monalert

A framework with Python scripts for monitoring events of interest and notify the user upon its occurance. Note that the framework for now triggers an one-time query only, and therefore, relies on the host machine for task scheduling.

The framework as of now only supports monitoring USCIS case status. More are on the way, and ideas are welcomed! 

## Environment Vairables
Please be sure to create the `.env` file from `.env.template` and populate the values as they are used by the framework to perform critical tasks such as sending notifications. Please see the **MongoDB** and **Notifications** sections for more information.

## MongoDB
MongoDB is used for some scripts that rely on a persistent storage for status change. The following environment variables are needed. Feel free to provide them as they are if you don't intend to change anything else.

MongoDB | Default
------- | -------
MONGO_HOST | mongo
MONGO_PORT | 27017
MONGO_INITDB_ROOT_USERNAME | monalert
MONGO_INITDB_ROOT_PASSWORD | monalert

## Notifications
Notifications are sent via [Pushover](https://pushover.net/). To enable it, you'll need to register an account, install the [app](https://pushover.net/clients) on your phone, and provide the following values to `.env`. These values are provided by Pushover once you have an account. Please see https://pushover.net/api for more information.

Pushover |
---------|
PUSHOVER_TOKEN
PUSHOVER_USER
PUSHOVER_DEVICE

## Run With Docker
#### Bring up the containers
```
$ docker-compose up --build
```
#### Trigger an one-off query
```
$ docker exec monalert sh -c "python monalert.py [command] [args] [options] > /proc/1/fd/1 2>/proc/1/fd/2"
```
Please be advised that
- `> /proc/1/fd/1 2>/proc/1/fd/2` is to redirect the output to `STDOUT` so that you can see the logs via `docker logs`.
- `sh -c "[command]"` is needed because otherwise the above redirect will be applied to `docker exec`.
- You'll need to rely on your host machine for triggering the above command periodically such as Linux's `crontab`.
- For more what you can do, please refer to the help doc via `docker exec monalert python monalert.py --help`.
