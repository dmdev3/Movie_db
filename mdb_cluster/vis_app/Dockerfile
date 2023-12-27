FROM python:3.11-slim

# set vars
ENV DB_USER=$DB_USER
ENV DB_PASSWORD=$DB_PASSWORD
ENV DB_HOST=$DB_HOST
ENV DB_PORT=$DB_PORT
ENV DB_NAME=$DB_NAME
ENV API_KEY=$API_KEY

USER root

RUN mkdir /app
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

EXPOSE 8501
EXPOSE 8502
EXPOSE 8503
EXPOSE 8504

WORKDIR /app

CMD streamlit run visapp_list_data.py


