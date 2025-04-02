FROM python:3.10-alpine

WORKDIR /app

# Install build dependencies + GLPK
RUN apk add --no-cache gcc g++ musl-dev glpk glpk-dev

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
