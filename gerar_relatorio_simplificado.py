import pandas as pd
import argparse
import os
import sys
import json
from gerador_relatorio_pdf_simplificado import RelatorioRiscoCardiaco

def verificar_arquivos_necessarios():
    """
    Verifica se todos os arquivos necessários estão disponíveis
    """
    arquivos = ['estatisticas.json', 'framingham_clean.csv']
    missing = [f for f in arquivos if not os.path.exists(f)]
    
    if missing:
        print(f"Erro: Arquivos ausentes: {', '.join(missing)}")
        print("Execute primeiro o script de análise exploratória.")
        return False
    return True

def gerar_relatorio_individual(nome_paciente, dados_paciente):
    """
    Gera um relatório para um paciente individual com os dados fornecidos
    """
    # Criar e gerar relatório
    relatorio = RelatorioRiscoCardiaco(nome_paciente, dados_paciente)
    nome_arquivo = relatorio.gerar_relatorio()
    
    print(f"\nRelatório para {nome_paciente} gerado com sucesso!")
    print(f"Arquivo: {nome_arquivo}")
    print(f"Índice de risco cardiovascular: {relatorio.probabilidade_risco:.0%} (Categoria: {relatorio.categoria_risco})")
    
    return nome_arquivo

def processar_arquivo_csv(arquivo_csv, coluna_nome=None):
    """
    Processa um arquivo CSV com dados de múltiplos pacientes
    """
    try:
        # Carregar o arquivo CSV
        df = pd.read_csv(arquivo_csv)
        
        # Verificar se a coluna de nome existe
        if coluna_nome and coluna_nome not in df.columns:
            print(f"Erro: Coluna '{coluna_nome}' não encontrada no arquivo.")
            return
            
        # Gerar relatórios para cada linha
        relatorios_gerados = []
        for i, row in df.iterrows():
            # Determinar o nome do paciente
            if coluna_nome:
                nome = row[coluna_nome]
            else:
                nome = f"Paciente_{i+1}"
                
            # Extrair dados relevantes (excluindo a coluna de nome se existir)
            dados = row.drop(coluna_nome) if coluna_nome else row
            
            # Gerar relatório
            try:
                arquivo = gerar_relatorio_individual(nome, dados)
                relatorios_gerados.append((nome, arquivo))
            except Exception as e:
                print(f"Erro ao gerar relatório para {nome}: {str(e)}")
        
        # Mostrar resumo
        if relatorios_gerados:
            print("\nResumo dos relatórios gerados:")
            for nome, arquivo in relatorios_gerados:
                print(f"- {nome}: {arquivo}")
                
    except Exception as e:
        print(f"Erro ao processar arquivo CSV: {str(e)}")

def coletar_dados_manual():
    """
    Coleta dados de um paciente manualmente via linha de comando
    """
    print("\n=== Coleta de Dados do Paciente ===")
    
    nome = input("Nome do paciente: ")
    
    # Coletar dados numéricos
    dados = {}
    variaveis_numericas = [
        ('age', 'Idade (anos): '),
        ('male', 'Sexo (0-Feminino, 1-Masculino): '),
        ('currentSmoker', 'Fumante (0-Não, 1-Sim): '),
        ('cigsPerDay', 'Cigarros por dia (0 se não fuma): '),
        ('BPMeds', 'Usa medicação para pressão (0-Não, 1-Sim): '),
        ('prevalentStroke', 'Histórico de AVC (0-Não, 1-Sim): '),
        ('prevalentHyp', 'Hipertensão (0-Não, 1-Sim): '),
        ('diabetes', 'Diabetes (0-Não, 1-Sim): '),
        ('totChol', 'Colesterol total (mg/dL): '),
        ('sysBP', 'Pressão sistólica (mmHg): '),
        ('diaBP', 'Pressão diastólica (mmHg): '),
        ('BMI', 'IMC (kg/m²): '),
        ('heartRate', 'Frequência cardíaca (bpm): '),
        ('glucose', 'Glicose (mg/dL): ')
    ]
    
    for var, prompt in variaveis_numericas:
        while True:
            try:
                valor = input(prompt)
                dados[var] = float(valor)
                break
            except ValueError:
                print("Erro: Insira um valor numérico válido.")
    
    # Gerar relatório
    try:
        gerar_relatorio_individual(nome, dados)
    except Exception as e:
        print(f"Erro ao gerar relatório: {str(e)}")

def main():
    # Verificar se os arquivos necessários existem
    if not verificar_arquivos_necessarios():
        return
    
    # Configurar argumentos da linha de comando
    parser = argparse.ArgumentParser(description='Gerador de Relatórios de Risco Cardiovascular')
    
    # Criar grupos mutuamente exclusivos
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-m', '--manual', action='store_true', 
                      help='Coletar dados de paciente manualmente')
    group.add_argument('-c', '--csv', type=str, 
                      help='Arquivo CSV com dados de múltiplos pacientes')
    
    # Opção adicional para o modo CSV
    parser.add_argument('-n', '--nome-coluna', type=str, 
                      help='Nome da coluna com os nomes dos pacientes (para modo CSV)')
    
    # Analisar argumentos
    args = parser.parse_args()
    
    # Executar modo apropriado
    if args.manual:
        coletar_dados_manual()
    elif args.csv:
        processar_arquivo_csv(args.csv, args.nome_coluna)

if __name__ == "__main__":
    main()