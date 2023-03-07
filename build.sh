#!/bin/sh -e

docker build . -t registry1.ctdn.net/library/tweetreplies-web-api:latest

docker push registry1.ctdn.net/library/tweetreplies-web-api:latest
