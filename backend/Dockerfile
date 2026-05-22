FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system deps + Microsoft ODBC Driver 18 for SQL Server (Debian 12 / Bookworm)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       curl \
       gnupg \
       apt-transport-https \
       unixodbc-dev \
       build-essential \
    # Download and store Microsoft's GPG key in the new keyring location
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc \
       | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    # Add the Microsoft SQL Server ODBC repo with the signed-by attribute
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" \
       > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY backend/ ./backend/

# Ensure uploads directory exists
RUN mkdir -p /app/backend/uploads

# Copy and prepare entrypoint
COPY backend/docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh \
    && sed -i 's/\r$//' /app/docker-entrypoint.sh

EXPOSE 5000

CMD ["/app/docker-entrypoint.sh"]
