# With docker compose
docker-compose down
docker-compose up -d
docker-compose exec glue-dev bash

# With just Dockerfile
✅ Step 1: Build the Image
cd aws
docker build -t glue_pyspark_poetry_image .

✅ Step 2: Run the Container with Your Project Mounted
D:\tge\2025\ird-projects\my_pyautomation
# Run below command if use powershell
docker run -it --rm `
    -v C:\Users\erirs\.aws:/home/glue_user/.aws `
    -v D:\tge\2025\ird-projects\my_pyautomation\aws:/home/glue_user/workspace `
    -e AWS_PROFILE=default `
    -e DISABLE_SSL=true `
    --network=host `
    --name glue_pyspark `
    -p 5678:5678 `
    --entrypoint /bin/bash `
    glue_pyspark_poetry_image

# Run below command if use command prompt

# Run below command if use bash(for linux ec2)
docker run -it --rm \
  -v ~/.aws:/home/glue_user/.aws \
  -v ~/tge_projects:/home/glue_user/workspace \
  -e AWS_PROFILE=default \
  -e DISABLE_SSL=true \
  --network=host \
  --name glue_pyspark \
  -p 5678:5678 \
  --entrypoint /bin/bash \
  glue_pyspark_poetry_image

# for tge projects
sudo docker run -it --rm \
    -v /home/ec2-user/.aws:/home/glue_user/.aws \
    -v /home/ec2-user/tge_projects:/home/glue_user/workspace \
    -e AWS_PROFILE=default \
    -e DISABLE_SSL=true \
    -e PYTHONPATH=/home/glue_user/workspace/myteamge-glue-common-utils \
    --network=host \
    -p 4040:4040 \
    -p 18080:18080 \
    --name glue_pyspark \
    amazon/aws-glue-libs:glue_libs_4.0.0_image_01 \
    pyspark

# build and push image to ecr
docker commit bc827f9241a7 my-glue-custom:latest
Note: bc827f9241a7 is container id
# 1. Create ECR repo (do this only once)
aws ecr create-repository --repository-name my-glue-custom --region ap-southeast-2

# 2. Authenticate Docker to ECR
aws ecr get-login-password \
  | docker login --username AWS \
  --password-stdin 927721130786.dkr.ecr.ap-southeast-2.amazonaws.com

# 3. Tag your local image
docker tag my-glue-custom:latest 927721130786.dkr.ecr.ap-southeast-2.amazonaws.com/my-glue-custom:latest

# 4. Push to ECR
docker push 927721130786.dkr.ecr.ap-southeast-2.amazonaws.com/my-glue-custom:latest

# once pushed reuse the image from ecr
docker run -it --rm \
  -v /home/ec2-user/.aws:/home/glue_user/.aws \
  -v /home/ec2-user/tge_projects:/home/glue_user/workspace \
  -e AWS_PROFILE=default \
  -e DISABLE_SSL=true \
  -e PYTHONPATH=/home/glue_user/workspace/myteamge-glue-common-utils \
  --network=host \
  -p 4040:4040 \
  -p 18080:18080 \
  --name glue_pyspark \
  927721130786.dkr.ecr.ap-southeast-2.amazonaws.com/my-glue-custom:latest \
  pyspark

# Below is the full command that we run in wsl amazon linux 2
docker run -it --rm \
  -v /root/.aws:/home/glue_user/.aws \
  -v /root/projects/tge-projects:/home/glue_user/workspace \
  -e AWS_PROFILE=default \
  -e DISABLE_SSL=true \
  -e PYTHONPATH=/home/glue_user/workspace/myteamge-glue-common-utils \
  --network=host \
  -p 4040:4040 \
  -p 18080:18080 \
  --name glue_pyspark \
  927721130786.dkr.ecr.ap-southeast-2.amazonaws.com/my-glue-custom:latest \
  pyspark

NOTE:If you face issue like "Unable to write file" run below command in wsl terminal not inside container
chmod -R a+rwX /root/projects

What this does:
-it: interactive terminal
--rm: remove container on exit
-v: mounts your local project into the container
You’ll land in: /home/glue_user/workspace with your code available

# Start an interactive bash shell inside the container:
docker exec -it glue-poetry-image bash

# To clean up, stop and remove the container:
docker stop glue-poetry-image
docker rm glue-poetry-image

Step 3: Inside the Container
# Install project dependencies from pyproject.toml
poetry install
# Run your Glue script
poetry run python aws/glue_project1/glue_demo.py
OR
python -m aws.glue_project1.glue_demo1.py

# Default python packages inside glue docker container
[glue_user@docker-desktop workspace]$ which python3
/usr/local/bin/python3
[glue_user@docker-desktop workspace]$ pip3 list
Package                   Version       
------------------------- --------------
aiobotocore               2.4.1 
aiohappyeyeballs          2.4.6 
aiohttp                   3.8.3 
aioitertools              0.11.0
aiosignal                 1.3.1 
anyio                     4.8.0 
argon2-cffi               23.1.0
argon2-cffi-bindings      21.2.0
arrow                     1.3.0 
asn1crypto                1.5.1 
asttokens                 3.0.0 
async-lru                 2.0.4 
async-timeout             4.0.2 
asynctest                 0.13.0
attrs                     23.2.0
autovizwidget             0.22.0
avro-python3              1.10.2
babel                     2.17.0
beautifulsoup4            4.13.3
bleach                    6.2.0
boto                      2.49.0
boto3                     1.34.84
botocore                  1.34.162
certifi                   2025.1.31
cffi                      1.17.1
chardet                   3.0.4
charset-normalizer        3.4.1
click                     8.1.3
cloudpickle               2.2.1
comm                      0.2.2
cryptography              44.0.1
cycler                    0.10.0
Cython                    0.29.32
debugpy                   1.8.13
decorator                 5.2.1
defusedxml                0.7.1
dill                      0.3.9
docker                    7.1.0
docutils                  0.17.1
enum34                    1.1.10
exceptiongroup            1.2.2
executing                 2.2.0
fastjsonschema            2.21.1
fqdn                      1.5.1
frozenlist                1.3.3
fsspec                    2021.8.1
google-pasta              0.2.0
gssapi                    1.9.0
h11                       0.14.0
hdijupyterutils           0.22.0
httpcore                  1.0.7
httpx                     0.28.1
idna                      3.10
importlib-metadata        6.11.0
iniconfig                 2.0.0
ipykernel                 6.29.5
ipython                   8.32.0
ipywidgets                8.1.5
isoduration               20.11.0
jedi                      0.19.2
Jinja2                    3.1.5
jmespath                  1.0.1
joblib                    1.0.1
json5                     0.10.0
jsonpointer               3.0.0
jsonschema                4.23.0
jsonschema-specifications 2024.10.1
jupyter                   1.1.1
jupyter_client            8.6.3
jupyter-console           6.6.3
jupyter_core              5.7.2
jupyter-events            0.12.0
jupyter-lsp               2.2.5
jupyter_server            2.15.0
jupyter_server_terminals  0.5.3
jupyterlab                4.2.5
jupyterlab_pygments       0.3.0
jupyterlab_server         2.27.3
jupyterlab_widgets        3.0.13
kaleido                   0.2.1
kiwisolver                1.4.4
krb5                      0.7.0
lxml                      5.3.1
MarkupSafe                3.0.2
matplotlib                3.4.3
matplotlib-inline         0.1.7
mistune                   3.1.2
mpmath                    1.2.1
multidict                 6.0.4
multiprocess              0.70.17
narwhals                  1.28.0
nbclient                  0.10.2
nbconvert                 7.16.6
nbformat                  5.10.4
nest-asyncio              1.6.0
nltk                      3.7
notebook                  7.2.3
notebook_shim             0.2.4
numpy                     1.26.4
overrides                 7.7.0
packaging                 24.2
pandas                    2.1.4
pandocfilters             1.5.1
parso                     0.8.4
pathos                    0.3.3
patsy                     0.5.1
pexpect                   4.9.0
Pillow                    9.4.0
pip                       23.0.1
platformdirs              4.3.7
plotly                    5.16.0
pluggy                    1.5.0
pmdarima                  2.0.1
pox                       0.3.5
ppft                      1.7.6.9
prometheus_client         0.21.1
prompt_toolkit            3.0.50
propcache                 0.3.0
protobuf                  4.25.6
psutil                    7.0.0
ptvsd                     4.3.2
ptyprocess                0.7.0
pure_eval                 0.2.3
pyarrow                   14.0.0
pycparser                 2.22
pydevd                    2.5.0
Pygments                  2.19.1
pyhocon                   0.3.58
PyMySQL                   1.0.2
pyparsing                 2.4.7
pyspnego                  0.11.2
pytest                    8.3.4
python-dateutil           2.9.0.post0
python-json-logger        3.2.1
pytz                      2025.1
PyYAML                    6.0.2
pyzmq                     26.2.1
redshift-connector        2.0.918
referencing               0.36.2
regex                     2022.10.31
requests                  2.31.0
requests-kerberos         0.15.0
responses                 0.18.0
rfc3339-validator         0.1.4
rfc3986-validator         0.1.1
rpds-py                   0.23.1
s3fs                      2022.11.0
s3transfer                0.10.1
sagemaker                 2.212.0
schedule                  1.2.2
schema                    0.7.7
scikit-learn              1.1.3
scipy                     1.9.3
scramp                    1.4.5
seaborn                   0.12.2
Send2Trash                1.8.3
setuptools                77.0.3
six                       1.17.0
smdebug-rulesconfig       1.0.1
sniffio                   1.3.1
soupsieve                 2.6
sparkmagic                0.21.0
stack-data                0.6.3
statsmodels               0.13.5
subprocess32              3.5.4
sympy                     1.8
tbats                     1.1.0
tblib                     2.0.0
tenacity                  9.0.0
terminado                 0.18.1
threadpoolctl             3.1.0
tinycss2                  1.4.0
tomli                     2.2.1
tornado                   6.4.2
tqdm                      4.67.1
traitlets                 5.14.3
types-python-dateutil     2.9.0.20241206
typing_extensions         4.12.2
tzdata                    2025.1
uri-template              1.3.0
urllib3                   2.3.0
wcwidth                   0.2.13
webcolors                 24.11.1
webencodings              0.5.1
websocket-client          1.8.0
wheel                     0.37.0
widgetsnbextension        4.0.13
wrapt                     1.14.1
yarl                      1.8.2
zipp                      3.21.0