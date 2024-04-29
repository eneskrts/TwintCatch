FROM python:3.7.3
ENV PYTHONUNBUFFERED 1 
RUN mkdir /django-twint
WORKDIR /django-twint
ADD requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
RUN python manage.py makemigrations
RUN python manage.py migrate



