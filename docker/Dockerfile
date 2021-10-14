# 
# Docker file to create the image to run PSS (Panosc Search Scoring)
#
# use miniconda container
FROM continuumio/miniconda3 as conda

# create app folder
RUN mkdir /app
# copy our application
COPY main.py /app/main.py
COPY app /app/app
COPY conda_PSS_env.yml /app/.
# copy config file with version
COPY docker/pss_config.json /app/config/pss_config.json
# copy script to download stopwords
COPY download_nltk_stopwords.py /app/.
# copy docker cmd script
COPY docker_cmd.bash /.
RUN chmod +x /docker_cmd.bash

# create the conda environment
RUN conda env create -f /app/conda_PSS_env.yml -n PSS

# now downloads the NLTK stopwords
WORKDIR /app
RUN conda run -n PSS python download_nltk_stopwords.py

CMD [ \
  "conda", "run", "-n", "PSS", "python", "main.py" \
#  "./docker_cmd.bash" \
]
