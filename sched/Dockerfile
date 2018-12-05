
FROM continuumio/miniconda3
EXPOSE 3000

RUN apt-get update -y
COPY sched/requirements.txt /
RUN pip install --upgrade pip
RUN python3 -m pip install -r requirements.txt

COPY sched/submit_jobs.py /
COPY sched/bai_pred_config.json /
COPY batchai/predict.py /
