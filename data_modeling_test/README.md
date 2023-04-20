
#  Weather Data Exercise using Python

## Technologies / Libraries
    1. Python
    2. django rest framework
    3. SQLLite
    4. Swagger

## Installation
    1. Python 3.6+ any version
    2. create virtualenv
    3. activate virtualenv
    4. pip install -r requirements.txt
    5. run django using `python manage.py runserver`

### Use Swagger to verify API
    1. http://localhost:8000/swagger/

### Deployment:
    * If we want to go live, we can use below configuration. 
        > EC2 instance with linux server
        > Postgres as a Database using RDS Service
        > Nginx as a server
        > s3 to store static and media files
    