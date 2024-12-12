# Savas' twin

This is an implementation of a very simple version of my digital twin.
I used it as a playground for learning the [langchain](https://www.langchain.com/)
set of tools and APIs.

More info on my blog post: [Digital twin follow up](https://savas.me/2024/12/11/digital-twin-follow-up/↗).

## Instructions

I use Python 3.13.

### Install `ollama` and pull Llama

```bash
> brew install ollama
> ollama serve
```

In a separate terminal:

```bash
> ollama pull llama:70b
```

Please note that, at the time of writing this, I use a MacBook Pro M1 Max with 64GB RAM so I can host the 70b Llama model.

### Install requirements

```bash
> python3.13 -m .venv
> source .venv/bin/activate
> pip3.13 install -r digital_twin/requirements.txt
```

### Run

Now you can run the digital twin without retrieval. For more information, refer to the blog post: [Digital twin follow up](https://savas.me/2024/12/11/digital-twin-follow-up/↗).

```bash
> cd digital_twin
> python3.13 main_without_retrieval.py
```
