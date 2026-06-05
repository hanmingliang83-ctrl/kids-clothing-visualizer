FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV BAILIAN_API_KEY=""
ENV PORT=58080

EXPOSE $PORT

CMD ["python", "-m", "http.server", "58080"]
