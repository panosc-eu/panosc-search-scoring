# 
# Docker file to create the image to run PSS (Panosc Search Scoring)
#
# use python3.9 container
FROM python:3.9

# create app folder
RUN mkdir /app
# copy our application
COPY main.py /app/main.py
COPY app /app/app
# copy config file with version
RUN ls docker
RUN cat docker/pss_config.json
COPY docker/pss_config.json /app/config/pss_config.json
# copy script to download stopwords
COPY download_nltk_stopwords.py /app/.
# copy python requirements (for api and test)
COPY requirements.txt /app/requirements.txt

WORKDIR /app

# install python requirements
RUN pip install --no-cache-dir -r /app/requirements.txt

# now downloads the NLTK stopwords
RUN python download_nltk_stopwords.py

CMD ["python", "main.py"]
