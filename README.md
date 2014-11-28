badge-service
=============
 
# Endpoints

## /dependencies/update

### HTTP method

```
POST 
```

### BODY

I will receive

```
{
    "appId": "uptodator_repo-connector",
	"numberOfUpdates : "10"
}
```

I will reply with HTTP 201 status code

## /<appId>

### HTTP method

```
GET
```

I will reply with 302 redirect to http://shields.io
