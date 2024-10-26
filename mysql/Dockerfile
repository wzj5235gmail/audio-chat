# Mysql
FROM mysql:latest

# Copy the initialization script
COPY ./init.sql /docker-entrypoint-initdb.d/

# Expose the default MySQL port
EXPOSE 3306

# Start the MySQL service
CMD ["mysqld"]