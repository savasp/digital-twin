# digital twin
Experiments with a digital twin.

The digital representation of a person.

## Set up instructions

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

Set up the custom models:

```bash
>  ollama create digital_twin_mistral -f models/modelfile_mistral.txt
>  ollama create digital_twin_mixtral -f models/modelfile_mixtral.txt
>  ollama create digital_twin_llama2-7b -f models/modelfile_llama2-7b.txt
>  ollama create digital_twin_llama2-13b -f models/modelfile_llama2-13b.txt
>  ollama create digital_twin_gemma-2b -f models/modelfile_gemma-2b.txt
>  ollama create digital_twin_gemma-7b -f models/modelfile_gemma-7b.txt
```

Run the experiments

```bash
> python3 -m src.experiments.main
```
