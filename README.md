# CS348-EnviroShare

CS 348 - Fall 2022: Ride Sharing Relational Database Group Project

## Development Notes

- venv and .idea are ignored by git, if you are using a different IDE than PyCharm please add files like .vscode to the
  .gitignore
- To setup environment: Python 3.9, and install with pip: flask, flask-login, flask-sqlalchemy, and mysqlclient
- Bootstrap template used (with class info): https://bootswatch.com/cerulean/
- To run application, run main.py to start server and navigate to http://127.0.0.1:5000/ in a web browser (localhost).
- Your MySql needs a database called 'enviroshare' with a user called 'Enviroshare' that has a password 'Enviroshare'.
  This user needs to be a superuser (same permissions as root). To do this, run the following in your MySql Command
  Line from the root user:

```
CREATE USER 'Enviroshare'@'127.0.0.1' BY 'Enviroshare';
GRANT ALL PRIVILEGES ON *.* TO 'Enviroshare'@'127.0.0.1' WITH GRANT OPTION;
```

Then, connect to your local connection with this new user on MySql Workbench and run:

```
CREATE DATABASE enviroshare;
USE enviroshare;
```