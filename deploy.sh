#!/bin/sh

PARAMS='-i stop-bannon.pem'
HOST='ubuntu@ec2-52-15-139-29.us-east-2.compute.amazonaws.com'

if [ -z $DB ]; then
    ssh $PARAMS $HOST rm -rf website
    echo $(git rev-parse HEAD) >website/DEPLOYED
    scp $PARAMS -Cr website $HOST:
    ssh $PARAMS $HOST cp local_settings.py website/website
else
    scp $PARAMS -C website/db.sqlite3 $HOST:website
fi

echo "\n\n"

if [ -z $RESTART ]; then
    echo "not restarting server"
else
    ssh $PARAMS $HOST sudo service nginx restart
    ssh $PARAMS $HOST sudo service uwsgi restart
fi

