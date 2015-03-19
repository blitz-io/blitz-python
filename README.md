### ![blitz.io](http://blitz.io/images/logo2.png)

### Make load and performance a fun sport.

* Run a sprint from around the world
* Rush your API and website to scale it out
* Condition your site around the clock

## Getting started

Login to [blitz.io](http://blitz.io) and open blitz keys tab:
https://blitz.io/to#/settings/blitz_keys/api_key

Then download and:

    python setup.py install

Or:

    easy_install blitz

And finally:

**Sprint**

```javascript
def callback(result):
    print("> Result:")
    print("\tregion: " + result.region)
    print("\tduration: " + str(result.duration))
    for step in result.steps:
        print("> Step:")
        print("\tstatus: " + str(step.response.status))
        print("\tduration: " + str(step.duration))
        print("\tconnect: " + str(step.connect))

options = {
    'steps':[
        {'url': "http://your.cool.app"},
        {'url': "http://your.cool.app/page1"}
    ]
}
s = Sprint("your@account.com", "aqbcdge-sjfkgurti-sjdhgft-skdiues")
s.execute(options, callback)
```

**Rush**

```javascript
def callback(result):
    for point in result.timeline:
        print("[")
        print("total:"+ str(point.total))
        print(", errors: " + str(point.errors))
        print(", hits: " + str(point.hits))
        print(", steps: " + str(len(point.steps)))
        for step in point.steps:
            print("\tstep duration: " + str(step.duration))
        print("]\n");

options = {
    'steps':[
        {'url': "http://your.cool.app"},
        {'url': "http://your.cool.app/page1"}
    ],
    'pattern': { 'intervals': [{'start':1, 'end':50, 'duration':30}]}}
r = Rush("your@account.com", "aqbcdge-sjfkgurti-sjdhgft-skdiues")
r.execute(options, callback)    
```

**Blitz-bar like syntax**

It will parse the test string and recognize the test as a rush or a sprint

```javascript
from blitz.curl import Test

test = Test("your@account.com", "aqbcdge-sjfkgurti-sjdhgft-skdiues")

def callback_sprint(result):
    print(result.region)
    print(result.duration)

test.parse("http://www.google.com", callback_sprint)

def callback_rush(result):
    for point in result.timeline:
        print("[")
        print("total:"+ str(point.total))
        print(", errors: " + str(point.errors))
        print(", hits: " + str(point.hits))
        print(", steps: " + str(len(point.steps)))
        for step in point.steps:
            print("\tstep duration: " + str(step.duration))
        print("]\n");

test.parse("-p 10-100:60 http://example.com", callback_rush)
```

