FROM python:3.10

WORKDIR /app

COPY data ./data
COPY src ./src
COPY game.xml game_licensed_assets.xml icon.png pyproject.toml README.md saves setup.cfg .

RUN python -m pip install --upgrade pip
RUN pip install .

CMD ["python", "src/pydw/game.py", "-s"]