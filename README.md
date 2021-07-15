# Amalu crawler

Amazon and magazinevocê scrapper

scrappe Amazon and magazinevocê and returns csv with product

## instalation

### (Optional) install enviroment

make sure that you have python installed

then install:

```python
pip install virtualenv
```

then install the enviroment and activate:

```python
python -m venv venv
.\venv\scripts\activate
```

### Install the dependêncies:

Install chromedriver [click here](https://chromedriver.chromium.org/downloads), and get the path location.

Create .env file with:

- chromedriver location
- token of telegram bot (if you use telegram function)

Example provided in ".env.example"

install the packages:

```python
pip install -r requirements.txt
```
and activate:
 
```python
python index.py
```

## Usage 

```python
python app.py <link do produto>
```