FROM python:3.14-slim
# les versions alpine de python sont plus légères que les versions debian, mais elles posent des problèmes de compatibilité avec playwright, notamment pour l'installation de chromium, c'est pourquoi on utilise une image debian

WORKDIR /app

ENV PLAYWRIGHT_BROWSERS_PATH="/ms-playwright"
ENV HOME="/tmp"

COPY requirements.txt ./

# dépendances python
RUN pip install --no-cache-dir -r ./requirements.txt

# dépendances playwright: le browser Chromium et ses dépendances pour fonctionner dans un environnement Debian slim
RUN playwright install chromium --with-deps \
    && chmod -R a+rX "$PLAYWRIGHT_BROWSERS_PATH"

COPY ./src ./src

ENV ENV="prod"
ENV LOG_LEVEL="INFO"

ENTRYPOINT ["python"]
CMD ["src/main.py"]
