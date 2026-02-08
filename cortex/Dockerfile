FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# install dependencies first (before copying code)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# vopy code into a 'cortex' subfolder to avoid cluttering the root of the container
COPY . ./cortex

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "cortex.app.main:app", "--host", "0.0.0.0", "--port", "8000"]