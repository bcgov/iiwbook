# IIW Book

## Running 

Make sure [Docker](https://docker.com) is installed and running.

Install [ngrok](https://ngrok.com).

1. Run `ngrok http 11000`

2. Copy the `https` url it generates for you (**must be https**)

3. Edit line 13 of `docker/docker-compose.yml` and change the link to the ngrok link you copied.

4. In the `docker` directory run `docker-compose build` and `docker-compose up`.


Then visit [http://localhost:7000](http://localhost:7000) to see the app running