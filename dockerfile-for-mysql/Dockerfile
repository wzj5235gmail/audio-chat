# Mysql
FROM mysql:latest

# Copy the initialization script
COPY "C:\Users\Administrator\Desktop\audio-chat\mysql-init-scripts\init.sql" /docker-entrypoint-initdb.d/

# Expose the default MySQL port
EXPOSE 3306

# Start the MySQL service
CMD ["mysqld"]