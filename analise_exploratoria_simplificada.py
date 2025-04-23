import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Configurações para visualização
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 12
sns.set_palette('viridis')

# Carregando o dataset
df = pd.read_csv('framingham.csv')

# Exibindo informações básicas
print("Informações do Dataset:")
print(f"Dimensões: {df.shape}")
print("\nPrimeiras linhas:")
print(df.head())
print("\nInformações sobre as colunas:")
print(df.info())
print("\nEstatísticas descritivas:")
print(df.describe())

# Verificando valores nulos
print("\nValores nulos por coluna:")
print(df.isnull().sum())

# Limpeza dos dados - preenchendo valores nulos com a mediana
df_clean = df.copy()
for col in df.columns:
    if df[col].isnull().sum() > 0:
        if df[col].dtype != 'object':  # Se for numérica
            median_val = df[col].median()
            df_clean[col] = df[col].fillna(median_val)
            print(f"Preenchidos {df[col].isnull().sum()} valores em '{col}' com a mediana: {median_val}")

# Análise de distribuição das variáveis principais
plt.figure(figsize=(14, 10))

# Variáveis numéricas para analisar
numeric_vars = ['age', 'cigsPerDay', 'totChol', 'sysBP', 'diaBP', 'BMI', 'heartRate', 'glucose']

for i, var in enumerate(numeric_vars):
    plt.subplot(3, 3, i+1)
    sns.histplot(df_clean[var], kde=True)
    plt.title(f'Distribuição de {var}')
    plt.tight_layout()

plt.savefig('distribuicoes.png')

# Análise da correlação entre as variáveis
plt.figure(figsize=(14, 12))
corr_matrix = df_clean.corr()
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
sns.heatmap(corr_matrix, mask=mask, annot=True, fmt=".2f", 
            cmap='coolwarm', linewidths=0.5, vmin=-1, vmax=1)
plt.title('Matriz de Correlação', fontsize=16)
plt.tight_layout()
plt.savefig('correlacao.png')

# Análise por gênero
plt.figure(figsize=(12, 8))
sns.countplot(x='TenYearCHD', hue='male', data=df_clean)
plt.title('Risco de Doença Cardíaca por Gênero')
plt.xlabel('Risco de Doença Cardíaca')
plt.ylabel('Quantidade')
plt.xticks([0, 1], ['Não', 'Sim'])
plt.legend(['Feminino', 'Masculino'])
plt.tight_layout()
plt.savefig('risco_por_genero.png')

# Relação entre idade e risco
plt.figure(figsize=(10, 6))
sns.boxplot(x='TenYearCHD', y='age', data=df_clean)
plt.title('Relação entre Idade e Risco de Doença Cardíaca')
plt.xlabel('Risco de Doença Cardíaca')
plt.ylabel('Idade')
plt.xticks([0, 1], ['Não', 'Sim'])
plt.tight_layout()
plt.savefig('risco_por_idade.png')

# Relação entre pressão sistólica e risco
plt.figure(figsize=(10, 6))
sns.boxplot(x='TenYearCHD', y='sysBP', data=df_clean)
plt.title('Relação entre Pressão Sistólica e Risco de Doença Cardíaca')
plt.xlabel('Risco de Doença Cardíaca')
plt.ylabel('Pressão Sistólica')
plt.xticks([0, 1], ['Não', 'Sim'])
plt.tight_layout()
plt.savefig('risco_por_pressao.png')

# Cálculo de valores de referência para categorização de risco
referencias = {
    'age': {'baixo': df_clean['age'].quantile(0.25), 
            'moderado': df_clean['age'].quantile(0.5),
            'alto': df_clean['age'].quantile(0.75)},
    
    'sysBP': {'baixo': 120, 'moderado': 130, 'alto': 140},
    'diaBP': {'baixo': 80, 'moderado': 85, 'alto': 90},
    'BMI': {'baixo': 18.5, 'moderado': 25, 'alto': 30},
    'glucose': {'baixo': 100, 'moderado': 125, 'alto': 140},
    'totChol': {'baixo': 200, 'moderado': 240, 'alto': 280},
    'cigsPerDay': {'baixo': 0, 'moderado': 5, 'alto': 10},
    'heartRate': {'baixo': 60, 'moderado': 80, 'alto': 100}
}

# Salvando estatísticas importantes e valores de referência
estatisticas = {
    'medias': df_clean.mean().to_dict(),
    'medianas': df_clean.median().to_dict(),
    'percentil_25': df_clean.quantile(0.25).to_dict(),
    'percentil_75': df_clean.quantile(0.75).to_dict(),
    'referencias': referencias
}

import json
with open('estatisticas.json', 'w') as f:
    json.dump(estatisticas, f, indent=4)

print("\nAnálise exploratória concluída. As visualizações e estatísticas foram salvas.")

# Salvando o dataset limpo
df_clean.to_csv('framingham_clean.csv', index=False)
print("Dataset limpo salvo como 'framingham_clean.csv'")