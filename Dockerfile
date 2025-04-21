FROM amazon/aws-glue-libs:glue_libs_4.0.0_image_01

# Set working directory
WORKDIR /home/glue_user/workspace

# Install Poetry
ENV POETRY_HOME="/home/glue_user/.local"
ENV PATH="$POETRY_HOME/bin:$PATH"
RUN curl -sSL https://install.python-poetry.org | python3 -

# Prevent Poetry from creating new venvs (we want system-level)
ENV POETRY_VIRTUALENVS_CREATE=false

# Install project dependencies
COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-root

# Copy all source code
COPY . .

CMD ["bash"]
