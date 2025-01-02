FROM mysql:8.0
COPY ./nozomi.sql /docker-entrypoint-initdb.d/

ENV MySQL_DATABASE=nozomi
ENV MYSQL_ROOT_PASSWORD=myrootpass
ENV MYSQL_USER=yuri000kun
ENV MYSQL_PASSWORD=yuripass

# 设置 MySQL 服务器字符集和排序规则
CMD ["mysqld", "--character-set-server=utf8mb4", "--collation-server=utf8mb4_unicode_ci", "--default-authentication-plugin=mysql_native_password"]