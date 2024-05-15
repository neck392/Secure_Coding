# Secure_Coding
> WHS

Dynamic Website coding using secure coding techniques

## Skill stack
<ul>
  <li>Language : python</li>
  <li>Front-end : streamlit</li>
  <li>Back-end : FastApi</li>
  <li>Database : SQLite3</li>
</ul>

## Build Environment
Required Program : https://docs.anaconda.com/free/miniconda/index.html
```
git clone https://github.com/neck392/Secure_Coding.git

conda create -n secure_coding python=3.9
conda activate secure_coding
pip install streamlit
pip install fastapi uvicorn
pip install passlib
```

## Run
Change to the cloned secure_coding directory on the Anaconda Prompt
```
streamlit run streamlit_app.py
uvicorn fastapi_app:app --reload
```

## Database
Database information for testing<br>
It can be executed by deleting the db extension file and pycache directory.

**Administrator account**
<ul>
  <li>ID : admin</li>
  <li>PW : admin </li>
</ul>

**User account**
<ul>
  <li>ID : test</li>
  <li>PW : test</li>
</ul>
