FROM python:3.10

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

# Font setup for container
RUN mkdir -p /usr/share/fonts/truetype/sharetechmono && \
    wget -O /usr/share/fonts/truetype/sharetechmono/ShareTechMono-Regular.ttf https://github.com/google/fonts/raw/main/ofl/sharetechmono/ShareTechMono-Regular.ttf && \
    fc-cache -fv

EXPOSE 8501
CMD ["streamlit", "run", "ui.py", "--server.port=8501", "--server.enableCORS=false"]