
> poetry init
> poetry install
build with tag:
> docker build -t mod4:latest .

> docker images
REPOSITORY                   TAG                    IMAGE ID       CREATED          SIZE
mod4                         latest                 39dec42253a2   36 seconds ago   209MB
run app in container:
>  docker run -v $(pwd)/storage:/my_app/storage -p 3000:3000 39dec42253a2
 