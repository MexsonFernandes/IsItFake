# IsItFake

Django based app containing QuotExaminer, FakeNews, FaceSwap and Clickbait detection services.

## Demo

    https://isitfake.co.in

## Features
* Exposed RESTful APIs.
* Cluster based analysis of clickbaits.
* Video analysis as per user selection of frames(taken per second).


## Requirements

* Google vision API key
* Google vision

## How to contribute or use?
* Clone repository.

    `git clone https://github.com/robomx/isitfake && cd isitfake`
* Setup environment

    `pip3 install pipenv && pipenv shell`
* Install requirements

    `pip3 install -r requirements.txt`
* Install dependencies
    
    `python -m nltk.downloader punkt words averaged_perceptron_tagger maxent_ne_chunker`
    `sudo apt-get install libsm6 libxrender1 libfontconfig1`
    `sudo apt-get install build-essential libglib2.0-0 libsm6 libxext6 libxrender-dev`
    Note: Make sure Java is installed.



    ## How to consume our project?
    * Use API template
        * <service_name.domain>/?format=api
    * Use HTML template
        * <service_name.domain>/?format=html
    * Use JSON Response
        * <service_name.domain>/?format=json
    Note: By default HTML reponse is rendered


## Request on server with API key
Client request must have the API key in the POST data:

    `'api_key': '***********'`
Test API key: Qr1iZXvm.Y71IaYQZ372mLxyjmIFxtZYmGMR9iBiU
