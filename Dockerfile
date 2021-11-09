# Dockerize the gca-calc-api

From python:3.8

RUN mkdir /app

WORKDIR /app

COPY application/engine.py application/binary_questions.py application/scalar_questions.py application/app.py application/default_questionnaire_v2.csv requirements2.txt ./

RUN pip install -r ./requirements2.txt

EXPOSE 5000
CMD ["gunicorn", "-b", ":5000", "app:app"]

