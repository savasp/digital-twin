# Digital Twin

Experiments with a digital twin, a digital representation of a person.

I wanted to learn/play with some technologies such as langchain, python, and open source LLMs. The "digital twin" is just the playground for my learning process. It's not meant to be a finished/polished experience. Suggestions/corrections are more than welcomed.

More context and results at https://savas.me/

## Set up instructions

You need to install [Python](https://www.python.org/) (I used v3.11) and [Ollama](https://ollama.com/). The `requirements.txt` files in some of the folder will ensure that the correct Python packages are installed (`pip3 install -r requirements.txt`).

Start `ollama`:

```bash
> ollama serve
```

Pull the models (using a different terminal):

```bash
> ollama pull mistral
> ollama pull llama2:7b
> ollama pull llama2:13b
> ollama pull gemma:2b
> ollama pull gemma:7b
```

Run the experiments from the root folder of the project.

```bash
> python3 -m src.experiments.main
```
