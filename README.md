[![img](https://img.shields.io/badge/Lifecycle-Dormant-ff7f2a)](https://github.com/bcgov/repomountie/blob/master/doc/lifecycle-badges.md)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

# IIW Book

## Pre-Requisites

- [Docker](https://www.docker.com/products/docker-desktop)

- [s2i](https://github.com/openshift/source-to-image/releases)

- [jq](https://stedolan.github.io/jq)

- [ngrok](https://ngrok.com)

`jq` and `ngrok` are available on package manager systems for different platforms such as [Homebrew](https://brew.sh/) (Mac), [Chocolatey](https://chocolatey.org/) (Windows) and various Linux distribution package managers.

## Running

Open two shell/terminal sessions:

1. From within the [scripts](./scripts) folder execute `./start-ngrok.sh`. This will create a tunnel for the agent.

2. From within the [docker](./docker) folder:
    - run `./manage build` to assemble the runtime images for the services
    - when the build completes, run `./manage up`

_Refer to `manage -h` for additional usage information._

Once services are started, visit [http://localhost:7070](http://localhost:7070) to see the app running.

## Deploy to Openshift
navigate to the openshift folder. To avoid docker pull rate limiting create pull credentails. [Here](https://developer.gov.bc.ca/Artifact-Repositories) is an example using artifactory. Once your pull credentials are set up follow the deployment process on a similar project [here](https://github.com/wadeking98/indy-email-verification#deploy). The process is exactly the same except the admin-api route and the names of the pods will be different.