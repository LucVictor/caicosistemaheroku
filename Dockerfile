FROM python:3.9
COPY ./ /app
ENV SQLALCHEMY_DATABASE_URI=""
WORKDIR /app
RUN ls -a
RUN pip3 install -r requirements.txt
CMD [ "gunicorn", "wsgi:app", "--bind", "0.0.0.0:8000"]
