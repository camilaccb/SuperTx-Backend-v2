# Base image
FROM python:3.10

# Do not create virtualenvs (recommended for Docker)
ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    POETRY_HOME="/opt/poetry"

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="$POETRY_HOME/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy only the dependencies files first (for caching)
COPY pyproject.toml poetry.lock* ./

# Install project dependencies
RUN poetry install --no-root

# Now copy the rest of the application
COPY . .

# Expose port (optional)
EXPOSE 5000

# Start Flask
CMD ["flask", "run", "--host", "0.0.0.0", "--port", "5000"]
