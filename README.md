<p align="center">
<img align="center" width="479" height="98" src="https://github.com/NoDataFound/IDrawAPT/raw/main/res/IDA.png"></p>


![header-logos](https://img.shields.io/static/v1?label=🏴‍☠️|NameSource:&logo=cn&message=apt.threattracking.com&color=red)

![header-logos](https://img.shields.io/static/v1?label=InProgress&logo=cn&message=🇨🇳|🇷🇺&color=blue)


#### `Description`

I am a simple script that leverages `https://github.com/jina-ai/dalle-flow` to visualize `Common` & `Vendor` based APT group names.

#### `Dependancies`


```python
pip3 install "docarray[common]>=0.13.5" jina
pip3 install jax==0.2.10 #M1 Mac Only
```


### `Run script against external webserver`

![header-logos](https://img.shields.io/static/v1?label=Option0&logo=nintendo&message=hosted:DALL-E-Flow&color=blue)

`Example Usage `
```bash
python3 ../IDrawAPT.py
[Actor File to Draw] Enter Filename: CN.txt

Plotting ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╺━━━━━━━━━  75% -:--:--
```
### Sample Output

`Meet 'Anchor Panda' `

![header-logos](https://github.com/NoDataFound/IDrawAPT/raw/main/China/AnchorPanda.png) 

### `Run script against local Docker image`

![header-logos](https://img.shields.io/static/v1?label=Option1&logo=docker&message=jinaai/dalle-flow:latest&color=blue)
* Modify `IDrawAPT.py` to use docker

```python
server_url = 'grpc://localhost:51005' #Docker Support
#server_url = 'grpc://dalle-flow.jina.ai:51005'
```
* Pull Docker `jinaai/dalle-flow:latest` image 


```bash
docker pull jinaai/dalle-flow:latest

latest: Pulling from jinaai/dalle-flow
#<snip>

894d0771aab5: Downloading [=========> ]  221.3MB/1.116GB
8451e5a9bff2: Download complete
a6b5bd0a44ab: Downloading [======>    ]  181.2MB/1.441GB

#<snip>
```
```
docker run -p 51005:51005 -v $HOME/.cache:/home/dalle/.cache --gpus all jinaai/dalle-flow
```
```bash
python3 ../IDrawAPT.py
[Actor File to Draw] Enter Filename: CN.txt
Currently Drawing: Anchor Panda ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   0% -:--:--
```



