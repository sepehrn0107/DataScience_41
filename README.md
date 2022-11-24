# Reducing Vacancy of Airbnb Listings
This is the code for group 41's final project delivery in [TDT4259 - Applied Data Science](https://www.ntnu.edu/studies/courses/TDT4259) at NTNU.

## Installing dependenices
The project code is written in Python (both notebooks and code) and thus requires some dependencies to get running.

To install the dependencies needed to run the code, run `make deps` in the project root folder. A **pyenv** is not set up by default in this project, so it is adviced that you set this up prior to avoid polluting global dependencies.

As SpaCy is used in the project, you will also have to run `python -m spacy download en_core_web_sm` to install the NLP model.

## Configuration
The program execution can be configured in the  `config.yaml`  file in root. This file specifies **which city** to analyze.

## Running the code
To run the code and analyze the configured city, run `make` in the root folder of the project.
