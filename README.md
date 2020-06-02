# Conway's Game of Life

In a conducto pipeline!

## Prerequisites

Ensure that [docker is installed](https://docs.docker.com/engine/install/).

You'll want python 3.6.1 or higher.  It's also often a good idea to work in a virtual environment:

Clone the code:

    git clone https://github.com/MatrixManAtYrService/conducto_life.git
    cd conducto_life

You'll want python 3.6.1 or higher.  It's also often a good idea to work in a virtual environment:

    python3 -m venv pipeline
    source ./pipeline/bin/activate

## Play with it

    pip install conducto
    python pipeline.py --local

Two things should happen:

- Docker will create a container that will connect to conducto.com and prepare it to visualize your pipeline
- A browser will open and take you to the pipeline as viewed though conducto.com


By the way, `--local` indicates that your local docker daemon will be used to execute the pipeline.  `--cloud` will be available in a future release.
