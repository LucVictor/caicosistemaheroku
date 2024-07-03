FROM python:3.12.4-alpine
COPY ./ /app
WORKDIR /app
RUN ls -a
RUN pip3 install -r requirements.txt
CMD [ \"gunicorn\", \"wsgi:app\", \"--workers\", \"4\" ]