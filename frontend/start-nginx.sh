#!/bin/sh

# Use Railway's PORT environment variable or default to 80
PORT=${PORT:-80}

# Update nginx config to use the PORT
sed -i "s/listen 80;/listen $PORT;/g" /etc/nginx/conf.d/default.conf

# Start nginx
nginx -g "daemon off;"
