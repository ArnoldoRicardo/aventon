aventon
=============

### build project

    docker-compose -f local.yml build


### and run

    docker-compose -f local.yml run

### debug

    docker-compose -f local.yml ps
    docker rm -f aventon_django_1
    docker-compose -f local.yml run --rm --service-ports django

### migrations

    docker-compose run --rm django python manage.py makemigrations