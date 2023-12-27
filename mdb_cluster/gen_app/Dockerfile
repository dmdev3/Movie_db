FROM python as builder

# Fix the value of PYTHONHASHSEED
# Note: this is needed when you use Python 3.3 or greater

# set vars
ENV DB_USER=$DB_USER
ENV DB_PASSWORD=$DB_PASSWORD
ENV DB_HOST=$DB_HOST
ENV DB_PORT=$DB_PORT
ENV DB_NAME=$DB_NAME
ENV API_KEY=$API_KEY

USER root

RUN mkdir /apps
#COPY ./app /apps
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
  
WORKDIR /apps



CMD python gen_list_data.py