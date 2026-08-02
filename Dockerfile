# ------- Base Image -------
FROM python:3.11

# ------- Working Directory -------
WORKDIR /app

# ------- Copy Project Files -------
COPY . /app

# ------- Install Dependencies -------
RUN pip install --upgrade pip --root-user-action=ignore && \
    pip install --root-user-action=ignore -r requirements.txt

# ------- Start Command -------
CMD ["python", "-m", "FileStream"]
