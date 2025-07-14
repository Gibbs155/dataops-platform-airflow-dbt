FROM bitnami/airflow:3.0.2-debian-12-r3
USER root
ENV AIRFLOW_COMPONENT_TYPE=worker

# Install aws cli
RUN apt-get update -yqq && apt-get install -y unzip wget
RUN wget "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -O "awscliv2.zip"
RUN unzip awscliv2.zip
RUN ./aws/install

COPY scripts/entrypoint.sh /entrypoint.sh
COPY scripts/sync_dags.sh /sync_dags.sh
COPY requirements.txt /bitnami/python/requirements.txt

ENTRYPOINT [ "/entrypoint.sh" ]
CMD [ "/run.sh" ]