Utilizo esse scritp para simplificar a geração de diagramas UML para minhas atividades das disciplinas de POO.

## Configuração

1. Compile o core-uml.jar a partir do repositório https://github.com/Milvum/urm
2. Instale o plantuml

## Utilização

```
usage: diaguml.py [-h] [--puml] [--sort] [--image] urmcore target

positional arguments:
  urmcore      urm-core.jar path
  target       file with java classes

optional arguments:
  -h, --help   show this help message and exit
  --puml, -p   generate puml file
  --sort, -s   sort puml using access modifiers
  --image, -i  make png image from puml

```

## Gerando uma imagem a partir do arquivo Solver.java

```
diaguml.py path_para_urm-core.jar -si Solver.java
```