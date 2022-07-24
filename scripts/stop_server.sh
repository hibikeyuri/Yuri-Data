#!/bin/bash

service nginx stop &&
service php7.4-fpm stop &&
service mysql stop &&
echo -e "local server stopped\n"