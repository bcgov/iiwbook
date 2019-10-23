# IIW Book

## Running 

Make sure [Docker](https://docker.com) is installed and running.

Install [ngrok](https://ngrok.com).

1. Run `ngrok http 11000`

1. Copy the `https` url it generates for you (**must be https**)

1. Edit line 24 of `docker/docker-compose.yml` and change the link to the ngrok link you copied.

1. In the `docker` directory run;
     1. `manage build` and `manage up`.  *Refer to `manage -h` for additional usage information.*

Then visit [http://localhost:7070](http://localhost:8080) to see the app running