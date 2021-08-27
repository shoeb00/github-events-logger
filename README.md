# Github logger

A simple webserver listens that listens to github actions for a selected repository and stores the events in structured logs in MongoDB.

<br/>

### Installation steps

Install all dependencies using python pip3 

```python
$ pip3 install requirements.txt
```

You can start the webserver by using python3
```python
$ python3 main.py
```

### Webhook
Github webhook accepts https link for which used ngrok to expose the local server to internet.
You can download it from https://ngrok.com/download and start the ngrok service by following the below commands.

```shell
$ ./ngrok http 3000
```


