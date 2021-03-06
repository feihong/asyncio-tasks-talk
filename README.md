# Using Tasks in Your Asyncio Web App

## Introduction

In this talk, I cover how to implement different types of tasks in an asyncio-based web application, including how to start them, stop them, and send incremental data to a web frontend using websockets. I will also spend a little time reviewing asyncio concepts.

## Slides

[View the slides on SpeakerDeck](https://speakerdeck.com/feihong/using-tasks-in-your-asyncio-web-app)

[View the slides as a single web page (includes notes)](https://github.com/feihong/asyncio-tasks-talk/blob/master/talk.md)

# Running example programs

Install all dependencies:

```
mkvirtualenv -p python3 asyncio-talk
pip install -r requirements.txt
# Make sure you have Node installed, then run:
npm install -g stylus rapydscript-ng
```

Now `cd` into any of the example directories and run:

```
muffin app run
```

The app will be served at `http://localhost:5000`.

## License

<a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>.
