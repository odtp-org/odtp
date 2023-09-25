# odtp

## How to install the ODTP in Conda

```
conda create --name odtp-main python=3.10
conda activate odpt-main
pip install streamlit streamlit-aggrid 
pip install st_pages barfi boto3 pymongo
pip install pygwalker streamlit-card
```

For running the GUI
```
cd odtp/gui
streamlit run app.py --server.port 8502
```

## How to run the odtp in docker
```
docker build -t caviri/odtp .
```

```
docker run -it --rm -p 8501:8501 caviri/odtp
```


## Individual Dockers

### MongoDB

```
docker run -d -p 2717:27017 -v /odtp/mongodb:/data/db --name odtp-mongo mongo:latest
```

Test:
```
docker exect -it odtp-mongo bash
mongo
show dbs
use test
db.user.insert({"name":"odtp"})
db.user.find()
exit
```

```
show collections
```

To explore:

- API Endpoint

### MinIO 

- https://www.youtube.com/watch?v=mg9NRR6Js1s&list=PLFOIsHSSYIK3h-ckBmtbFEtxNajnA5Txu&ab_channel=MinIO
- CREATE ENV VAR FILE

```
docker run -dt -p 9000:9000 -p 9090:9090 -v PATH:/mnt/data 
-v /etc/default/minio:/config.env
-e "MINIO_CONFIG_ENV_FILE=/etc/config.env"
--name "odtp-minion" minio server --console-address ":9090"


## Steps

- [] Make como


```
NOTES:

the connection string is :
mongodb://user-caviri:nm3qg68elc586iy5b73n@mongodb-0.mongodb-headless:27017,mongodb-1.mongodb-headless:27017/defaultdb?authSourcedefaultdb

example for python :
from pymongo import MongoClient
client = MongoClient('mongodb://user-caviri:nm3qg68elc586iy5b73n@mongodb-0.mongodb-headless:27017,mongodb-1.mongodb-headless:27017/defaultdb')
db=client.defaultdb
example for mongosh :

as user in defaultdb mongo -u user-caviri -p nm3qg68elc586iy5b73n --authenticationDatabase defaultdb
as root mongo -u root -p nm3qg68elc586iy5b73n
```



```

```