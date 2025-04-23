# Sistema de Avaliação de Risco Cardiovascular

Este projeto implementa um sistema automatizado para geração de relatórios PDF que avaliam fatores de risco cardiovascular baseado no conjunto de dados do Estudo de Framingham.

## Descrição

O sistema analisa dados cardiovasculares de pacientes e gera relatórios detalhados que incluem:
- Cálculo de índice de risco cardiovascular
- Visualizações comparativas com a população de referência
- Recomendações personalizadas baseadas nos fatores de risco identificados
- Representações visuais como gráficos de radar e histogramas comparativos

## Requisitos

- Python 3.8 ou superior
- Bibliotecas Python (listadas em `requirements.txt`):
  - pandas
  - numpy
  - matplotlib
  - seaborn
  - fpdf

## Instalação

1. Clone o repositório ou baixe os arquivos do projeto
2. Crie e ative um ambiente virtual Python:

```bash
# Crie o ambiente virtual
python -m venv venv

# Ative o ambiente (Windows)
venv\Scripts\activate

# Ative o ambiente (Linux/Mac)
source venv/bin/activate
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Baixe o conjunto de dados do Framingham:
   - Acesse: https://www.kaggle.com/datasets/aasheesh200/framingham-heart-study-dataset
   - Baixe o arquivo CSV
   - Salve-o como `framingham.csv` na pasta raiz do projeto

## Execução

O sistema possui dois scripts principais:

### 1. Preparação dos dados

Primeiro, execute o script de análise exploratória para processar o dataset e gerar os arquivos necessários:

```bash
python analise_exploratoria_simplificada.py
```

Este script irá:
- Analisar e limpar os dados do Framingham dataset
- Calcular estatísticas descritivas
- Gerar visualizações exploratórias
- Criar os arquivos `framingham_clean.csv` e `estatisticas.json`

### 2. Geração de relatórios

Existem duas formas de gerar relatórios:

#### Modo manual (para um único paciente)

```bash
python gerar_relatorio_simplificado.py -m
```

Esta opção inicia uma interface interativa de linha de comando que solicita os dados do paciente passo a passo:
- Nome do paciente
- Idade
- Sexo
- Fatores de risco como pressão arterial, colesterol, etc.

#### Modo CSV (para múltiplos pacientes)

```bash
python gerar_relatorio_simplificado.py -c arquivo_pacientes.csv -n nome_coluna
```

Onde:
- `arquivo_pacientes.csv` é o caminho para um arquivo CSV contendo dados de múltiplos pacientes
- `nome_coluna` (opcional) é o nome da coluna que contém os nomes dos pacientes

### Formato do arquivo CSV

Para processar múltiplos pacientes, o arquivo CSV deve conter as seguintes colunas:

```
nome_paciente,age,male,currentSmoker,cigsPerDay,BPMeds,prevalentStroke,prevalentHyp,diabetes,totChol,sysBP,diaBP,BMI,heartRate,glucose
```

Exemplo:
```
João Silva,55,1,1,10,0,0,1,0,220,140,90,28.5,75,105
Maria Souza,48,0,0,0,0,0,0,0,190,120,80,24.3,72,95
```

## Arquivos do Projeto

- `analise_exploratoria_simplificada.py`: Script para análise e preparação dos dados
- `gerador_relatorio_pdf_simplificado.py`: Classes e funções para geração de PDFs
- `gerar_relatorio_simplificado.py`: Script principal para execução do sistema
- `requirements.txt`: Lista de dependências do projeto
- `framingham.csv`: Dataset original (precisa ser baixado)
- `framingham_clean.csv`: Dataset limpo (gerado pelo script de análise)
- `estatisticas.json`: Estatísticas e valores de referência (gerado pelo script de análise)

## Relatório PDF Gerado

O relatório PDF gerado inclui as seguintes seções:

1. **Página de Resumo**:
   - Identificação do paciente
   - Data do relatório
   - Índice de risco cardiovascular
   - Categoria de risco (Baixo, Moderado, Alto) 
   - Interpretação do resultado

2. **Página de Detalhes**:
   - Tabela de fatores de risco numéricos
   - Tabela de fatores de risco categóricos
   - Indicação visual de valores fora dos limites recomendados

3. **Páginas de Visualizações**:
   - Gráfico de radar comparando múltiplos fatores de risco
   - Histogramas comparativos para idade, pressão sistólica e IMC

4. **Página de Recomendações**:
   - Recomendações gerais de saúde cardiovascular
   - Recomendações específicas baseadas nos fatores de risco identificados
   - Aviso legal

## Resolução de Problemas

- **Erro com caracteres especiais**: Se ocorrer erro relacionado a caracteres Unicode (como o marcador de lista •), edite o arquivo `gerador_relatorio_pdf_simplificado.py` e substitua o caractere • por - ou * nas seções de recomendações.

- **Erro com cores de texto**: Se ocorrer erro relacionado ao método `set_text_color()`, verifique se todas as chamadas deste método estão usando parâmetros RGB individuais e não tuplas desempacotadas.

## Exemplos

Exemplo de um relatório gerado:

```
Relatório para João Silva gerado com sucesso!
Arquivo: Relatorio_Risco_Cardiaco_João_Silva_20250423_144502.pdf
Índice de risco cardiovascular: 50% (Categoria: Moderado)
```

## Customização

Você pode customizar o sistema editando os seguintes componentes:

- Valores de referência: edite o dicionário `referencias` no método `gerar_pagina_detalhes()`
- Categorias de risco: modifique a função `categorizar_risco()`
- Recomendações: altere as listas `recomendacoes_gerais` e a lógica para gerar `recomendacoes_especificas`