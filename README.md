# Module 11 – Calculation Model and Validation

## Running Tests Locally

Create and activate a virtual environment:
python3 -m venv venv
source venv/bin/activate

Install dependencies:
pip install -r requirements.txt
playwright install

Run tests:
pytest -q

## Docker Hub Image

You can pull the deployed image using:

[docker pull cas228/module11:latest](https://hub.docker.com/r/cas228/module11)

docker pull cas228/module11:latest
docker run -d -p 8000:8000 cas228/module11:latest