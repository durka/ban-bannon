#!/bin/sh

PARAMS='-i stop-bannon.pem'
HOST='ubuntu@ec2-52-15-139-29.us-east-2.compute.amazonaws.com'

ssh $PARAMS $HOST rm -rf website
scp $PARAMS -Cr website $HOST:
ssh $PARAMS $HOST sed -i -e "'s/DEBUG = True/DEBUG = False/'" website/website/settings.py
ssh $PARAMS $HOST sudo service nginx restart
ssh $PARAMS $HOST sudo service uwsgi restart

