# PersonalCapitalService

This is an extension of the great work that Haochi did in this repo. https://github.com/haochi/personalcapital

Personal Capital's API setup allows you to authenticate with its backend services and make requests to it pretty easily. This is merely a wrapper API to allow capturing your data in a more friendly manner.

For example, I use it in combination with some Java code to track my spending, investments, and passive income in an Excel sheet every month.

This is currently designed to work for a single user at a time, but I have a separate local branch that I'm working on for people to use it publicly. 

## Setup

In order to get started you'll want to do a few things.

### Update the Basic Auth

I use Basic Auth because I want to be able to access this from outside my network while keeping others out. You can forgo using Basic Auth, but in case you want to keep it in, you can simply change the values in `pers-cap-svc.py`

Note: This is likely not how you want to handle secrets. You'd probably want to store them elsewhere and reference them here. If you're using some sort of CI/CD building like Jenkins, you can use secrets through that application and pass them in as environment variables

```python
api.config['BASIC_AUTH_USERNAME'] = 'ENTER_A_USER'
api.config['BASIC_AUTH_PASSWORD'] = 'ENTER_A_PASSWORD'
```

### Update your Personal Capital credentials

Included in this repo is an `encryptor.py` script. You'll first want to create yourself a secret key by following the steps from this link. https://www.geeksforgeeks.org/how-to-encrypt-and-decrypt-strings-in-python/ 

You would then add that in the SEC_KEY variable in your `encyrptor.py` script.  Once this is done, you can start to create your encrypted credentials. Simply run the `encryptor.py` script:

```shell
py encryptor.py
```

Then enter in the text you want to encrypt. Add the encrypted forms of your credentials to the `creds.json` file.

```json
{"user":"USER_ENCRYPTED","pass":"PASS_ENCRYPTED"}
```

### First execution

In order to start the service simply run:

```shell
py pers-cap-svc.py
```

Upon first execution, the script will ask you for a code. This is the Two Factor Auth you've likely set up with Personal Capital. Enter the code here and the script will generate a `session.json` file which is preserved across executions. The API will load this session instead of asking for a new one so  you don't need to authenticate everytime.

### Running as a docker

I've included a Dockerfile because I generally use this in a cluster of dockers on a home server. Because I use Jenkins for CI/CD I like to have the docker execute like so.

```shell
docker stop pers-cap-cntnr || true
docker rm pers-cap-cntnr || true
docker build -t pers-cap-svc:latest .
docker image prune -f || true
docker container prune -f || true
docker run --publish DESIREDHOSTPORT:DESIREDDOCKERPORT --detach --name pers-cap-cntnr pers-cap-svc
```

The above may do a few unnecessary things from your point og view so you can modify it to fit your needs.

### Available Endpoints

There are a bunch of different endpoints available which you can see by reading `pers-cap-svc.py`

All endpoints are GET Requests, so no inputs from a POST Body are required. 

Here are a few examples:

`/` : Hello World Endpoint. I had this to check whether or not the service is actually up. You could probably get rid of this.

`/accounts` : Returns a list of the accounts linked to your Personal Capital Account

`/trans/{numDays}` : Returns a list of transactions going back *numDays* days

    Example: `/trans/30`

`/trans/{start}/{end}` : Returns a list of transactions between the *start* and *end* dates. **Format should be yyyy-mm-dd**.

    Example: `/trans/2020-01-01/2020-12-31/`

### Troubleshooting

Sometimes the Personal Capital API just like.. doesn't work? You'll notice some random exceptions being thrown about being unable to parse a dictionary. Usually it's about spData, a json object Personal Capital uses frequently in their responses. To get around this, I set up the service to refresh the session every 10 minutes or so.

This isn't perfect, so in my implementation I set up a Health Check in my Jenkins environment to refresh it when it sees a failure.

```python
def init_scheduler(pc):
    print("Refreshing the session")
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=pc.refresh_session, trigger="interval", seconds=600)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())
```

