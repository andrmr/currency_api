#!/usr/bin/env bash
docker build -t "$1" . && docker push "$1"
