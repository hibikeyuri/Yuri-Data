#!/bin/bash

service nginx start &&
service php7.4-fpm start &&
service mysql start &&
echo -e "local server builded\n"
