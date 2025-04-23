import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
import json
import os
from datetime import datetime
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import io

# Configurações de estilo para os gráficos
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette('viridis')

# Carregar o dataset para estatísticas da população e as referências
df_pop = pd.read_csv('framingham_clean.csv')

# Carregar estatísticas e referências
with open('estatisticas.json', 'r') as f:
    estatisticas = json.load(f)

# Função para calcular o escore de risco sem modelo preditivo
def calcular_risco_simplificado(dados):
    """
    Calcula um escore de risco simples baseado em valores de referência
    """
    referencias = estatisticas['referencias']
    pontos = 0
    
    # Atribuir pontos para cada fator de risco
    for fator, ref in referencias.items():
        if fator in dados:
            valor = dados[fator]
            if valor >= ref['alto']:
                pontos += 2
            elif valor >= ref['moderado']:
                pontos += 1
                
    # Fatores binários
    fatores_binarios = ['currentSmoker', 'prevalentHyp', 'prevalentStroke', 'diabetes']
    for fator in fatores_binarios:
        if fator in dados and dados[fator] == 1:
            pontos += 2
            
    # Calcular probabilidade normalizada (0 a 1)
    # Considerando pontuação máxima possível = 16 (8 fatores contínuos + 4 binários)
    max_pontos = 16
    probabilidade = pontos / max_pontos
    
    return probabilidade

# Função para categorizar o risco
def categorizar_risco(probabilidade):
    """
    Categoriza o risco cardíaco com base na probabilidade
    """
    if probabilidade < 0.25:
        return "Baixo", "green"
    elif probabilidade < 0.50:
        return "Moderado", "orange"
    else:
        return "Alto", "red"

# Função para gerar o nome do arquivo
def gerar_nome_arquivo(nome_paciente):
    """
    Gera um nome de arquivo baseado no nome do paciente e data atual
    """
    data_atual = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_sem_espacos = nome_paciente.replace(" ", "_")
    return f"Relatorio_Risco_Cardiaco_{nome_sem_espacos}_{data_atual}.pdf"

# Função para criar gráfico comparativo
def criar_grafico_comparativo(valor_paciente, coluna, titulo, nome_temp):
    """
    Cria um gráfico comparando o valor do paciente com a distribuição populacional
    """
    plt.figure(figsize=(10, 6))
    # Plotar histograma da população
    sns.histplot(df_pop[coluna], kde=True, color='skyblue')
    
    # Adicionar linha vertical para o valor do paciente
    plt.axvline(x=valor_paciente, color='red', linestyle='--', linewidth=2)
    
    # Adicionar texto para o valor do paciente
    plt.text(valor_paciente, plt.ylim()[1]*0.9, f'Paciente: {valor_paciente}', 
             ha='center', va='center', bbox=dict(facecolor='white', alpha=0.7))
    
    plt.title(titulo)
    plt.tight_layout()
    
    # Salvar temporariamente
    plt.savefig(nome_temp)
    plt.close()

# Função para criar gráfico de radar
def criar_grafico_radar(dados_paciente, nome_temp):
    """
    Cria um gráfico de radar com os principais fatores de risco
    """
    # Fatores para o gráfico de radar
    fatores = ['age', 'sysBP', 'BMI', 'glucose', 'totChol']
    
    # Obter médias da população
    medias_pop = df_pop[fatores].mean()
    
    # Normalizar os dados para comparação
    max_vals = df_pop[fatores].max()
    min_vals = df_pop[fatores].min()
    
    # Normalização dos dados do paciente
    paciente_norm = [(dados_paciente[f] - min_vals[f]) / (max_vals[f] - min_vals[f]) for f in fatores]
    
    # Normalização das médias da população
    pop_norm = [(medias_pop[f] - min_vals[f]) / (max_vals[f] - min_vals[f]) for f in fatores]
    
    # Criar figura para o gráfico de radar
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, polar=True)
    
    # Ângulos para cada eixo
    angles = np.linspace(0, 2*np.pi, len(fatores), endpoint=False).tolist()
    
    # Completar o círculo repetindo o primeiro valor
    paciente_norm.append(paciente_norm[0])
    pop_norm.append(pop_norm[0])
    angles.append(angles[0])
    
    # Adicionar rótulos legíveis
    rotulos = ['Idade', 'Pressão Sistólica', 'IMC', 'Glicose', 'Colesterol Total']
    rotulos.append(rotulos[0])
    
    # Plotar dados do paciente
    ax.plot(angles, paciente_norm, 'r-', linewidth=2, label='Paciente')
    ax.fill(angles, paciente_norm, 'r', alpha=0.1)
    
    # Plotar médias da população
    ax.plot(angles, pop_norm, 'b-', linewidth=2, label='Média Pop.')
    ax.fill(angles, pop_norm, 'b', alpha=0.1)
    
    # Adicionar rótulos aos eixos
    plt.xticks(angles[:-1], rotulos[:-1])
    
    # Adicionar título e legenda
    plt.title('Comparação dos Fatores de Risco', size=15)
    plt.legend(loc='upper right')
    
    # Salvar temporariamente
    plt.savefig(nome_temp)
    plt.close()

# Classe para criar o relatório PDF
class RelatorioRiscoCardiaco(FPDF):
    def __init__(self, nome_paciente, dados_paciente):
        super().__init__()
        self.nome_paciente = nome_paciente
        self.dados_paciente = dados_paciente
        self.set_auto_page_break(auto=True, margin=15)
        self.probabilidade_risco = calcular_risco_simplificado(dados_paciente)
        self.categoria_risco, self.cor_risco = categorizar_risco(self.probabilidade_risco)
        
    def header(self):
        # Logo (pode ser substituído por uma imagem real)
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Relatório de Avaliação de Risco Cardiovascular', 0, 1, 'C')
        self.ln(5)
        
    def footer(self):
        # Rodapé com número da página
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')
        
    def gerar_pagina_resumo(self):
        self.add_page()
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, f'Resumo - {self.nome_paciente}', 0, 1, 'L')
        self.ln(5)
        
        # Data do relatório
        self.set_font('Arial', '', 10)
        self.cell(0, 10, f'Data: {datetime.now().strftime("%d/%m/%Y")}', 0, 1, 'L')
        
        # Probabilidade e categoria de risco
        self.ln(10)
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'Avaliação de Fatores de Risco Cardiovascular:', 0, 1, 'L')
        
        self.set_font('Arial', '', 12)
        self.cell(60, 10, 'Índice de Risco:', 0, 0, 'L')
        self.cell(0, 10, f'{self.probabilidade_risco:.0%}', 0, 1, 'L')
        
        self.cell(60, 10, 'Categoria de Risco:', 0, 0, 'L')
        
        # Definir cor para a categoria de risco
        if self.cor_risco == 'green':
            self.set_text_color(0, 128, 0)  # Verde
        elif self.cor_risco == 'orange':
            self.set_text_color(255, 128, 0)  # Laranja
        else:
            self.set_text_color(255, 0, 0)  # Vermelho
            
        self.cell(0, 10, self.categoria_risco, 0, 1, 'L')
        self.set_text_color(0, 0, 0)  # Voltar para preto
        
        # Adicionar interpretação
        self.ln(5)
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Interpretação:', 0, 1, 'L')
        
        self.set_font('Arial', '', 10)
        if self.categoria_risco == "Baixo":
            texto = ("O paciente apresenta baixo risco cardiovascular, com indicadores dentro ou próximos dos valores "
                    "recomendados. Recomenda-se manter hábitos saudáveis e realizar check-ups periódicos.")
        elif self.categoria_risco == "Moderado":
            texto = ("O paciente apresenta risco cardiovascular moderado, com alguns indicadores fora dos valores "
                    "recomendados. Recomenda-se atenção aos fatores de risco e possível intervenção médica.")
        else:
            texto = ("O paciente apresenta alto risco cardiovascular, com vários indicadores significativamente "
                    "fora dos valores recomendados. Recomenda-se intervenção médica e modificação dos fatores de risco.")
            
        self.multi_cell(0, 5, texto)
        
    def gerar_pagina_detalhes(self):
        self.add_page()
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Detalhes dos Fatores de Risco', 0, 1, 'L')
        self.ln(5)
        
        # Tabela de fatores
        self.set_font('Arial', 'B', 10)
        self.cell(80, 7, 'Fator', 1, 0, 'C')
        self.cell(30, 7, 'Valor', 1, 0, 'C')
        self.cell(40, 7, 'Média População', 1, 0, 'C')
        self.cell(40, 7, 'Referência', 1, 1, 'C')
        
        # Configurações para comparação com valores de referência
        referencias = {
            'age': {'ref': '< 55 anos', 'alto': 55},
            'sysBP': {'ref': '< 120 mmHg', 'alto': 120},
            'diaBP': {'ref': '< 80 mmHg', 'alto': 80},
            'BMI': {'ref': '18.5 - 24.9', 'alto': 25, 'baixo': 18.5},
            'glucose': {'ref': '< 100 mg/dL', 'alto': 100},
            'totChol': {'ref': '< 200 mg/dL', 'alto': 200},
            'cigsPerDay': {'ref': '0', 'alto': 1},
            'heartRate': {'ref': '60 - 100 bpm', 'alto': 100, 'baixo': 60}
        }
        
        # Mapeamento para nomes mais legíveis
        nomes_legiveis = {
            'age': 'Idade',
            'sysBP': 'Pressão Sistólica',
            'diaBP': 'Pressão Diastólica',
            'BMI': 'Índice de Massa Corporal',
            'glucose': 'Glicose',
            'totChol': 'Colesterol Total',
            'cigsPerDay': 'Cigarros por Dia',
            'heartRate': 'Frequência Cardíaca',
            'male': 'Sexo',
            'currentSmoker': 'Fumante Atual',
            'BPMeds': 'Usa Medicação para PA',
            'prevalentStroke': 'Histórico de AVC',
            'prevalentHyp': 'Hipertensão',
            'diabetes': 'Diabetes'
        }
        
        self.set_font('Arial', '', 10)
        
        # Fatores numéricos
        for fator in ['age', 'sysBP', 'diaBP', 'BMI', 'glucose', 'totChol', 'heartRate']:
            if fator in self.dados_paciente:
                valor = self.dados_paciente[fator]
                media_pop = df_pop[fator].mean()
                
                # Colorir célula se valor estiver fora da referência
                self.cell(80, 7, nomes_legiveis.get(fator, fator), 1, 0, 'L')
                
                # Verificar se valor está fora da referência
                cor_original = self.text_color
                
                if 'alto' in referencias[fator] and valor > referencias[fator]['alto']:
                    self.set_text_color(255, 0, 0)  # Vermelho para valor alto
                elif 'baixo' in referencias[fator] and valor < referencias[fator]['baixo']:
                    self.set_text_color(255, 0, 0)  # Vermelho para valor baixo
                
                self.cell(30, 7, f'{valor:.1f}', 1, 0, 'C')
                self.set_text_color(0, 0, 0)
                
                self.cell(40, 7, f'{media_pop:.1f}', 1, 0, 'C')
                self.cell(40, 7, referencias[fator]['ref'], 1, 1, 'C')
        
        # Fatores categóricos
        categoricos = {
            'male': {0: 'Feminino', 1: 'Masculino'},
            'currentSmoker': {0: 'Não', 1: 'Sim'},
            'BPMeds': {0: 'Não', 1: 'Sim'},
            'prevalentStroke': {0: 'Não', 1: 'Sim'},
            'prevalentHyp': {0: 'Não', 1: 'Sim'},
            'diabetes': {0: 'Não', 1: 'Sim'}
        }
        
        self.ln(5)
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Fatores Categóricos:', 0, 1, 'L')
        
        self.set_font('Arial', 'B', 10)
        self.cell(80, 7, 'Fator', 1, 0, 'C')
        self.cell(30, 7, 'Status', 1, 0, 'C')
        self.cell(80, 7, 'Relevância', 1, 1, 'C')
        
        self.set_font('Arial', '', 10)
        
        for fator, opcoes in categoricos.items():
            if fator in self.dados_paciente:
                valor = int(self.dados_paciente[fator])
                status = opcoes[valor]
                
                relevancia = "Baixa"
                cor = (0, 128, 0)  # Verde
                
                # Definir relevância e cor com base no valor
                if fator != 'male' and valor == 1:
                    relevancia = "Alta"
                    cor = (255, 0, 0)  # Vermelho
                
                self.cell(80, 7, nomes_legiveis.get(fator, fator), 1, 0, 'L')
                self.cell(30, 7, status, 1, 0, 'C')
                
                cor_original = self.text_color
                if isinstance(cor, tuple) and len(cor) == 3:
                    self.set_text_color(cor[0], cor[1], cor[2])
                else:
                    self.set_text_color(0, 0, 0)  # Preto como fallback
                self.cell(80, 7, relevancia, 1, 1, 'C')
                # Redefinir para a cor original
                self.set_text_color(0, 0, 0)  # Redefinir para preto
    
    def gerar_pagina_visualizacoes(self):
        self.add_page()
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Visualizações Comparativas', 0, 1, 'L')
        self.ln(5)
        
        # Criar gráfico de radar
        temp_radar = 'temp_radar.png'
        criar_grafico_radar(self.dados_paciente, temp_radar)
        
        # Adicionar gráfico de radar ao PDF
        self.image(temp_radar, x=25, y=30, w=160)
        os.remove(temp_radar)  # Remover arquivo temporário
        
        # Adicionar segunda página de visualizações com comparativos individuais
        self.add_page()
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Comparações com a População', 0, 1, 'L')
        self.ln(5)
        
        # Criar gráficos comparativos para principais fatores
        fatores_comparar = [
            ('age', 'Comparação de Idade'),
            ('sysBP', 'Comparação de Pressão Sistólica'),
            ('BMI', 'Comparação de IMC')
        ]
        
        y_pos = 30
        for i, (fator, titulo) in enumerate(fatores_comparar):
            temp_grafico = f'temp_comparativo_{i}.png'
            criar_grafico_comparativo(self.dados_paciente[fator], fator, titulo, temp_grafico)
            
            # Adicionar gráfico ao PDF
            self.image(temp_grafico, x=25, y=y_pos, w=160)
            y_pos += 85  # Espaçamento entre gráficos
            
            # Remover arquivo temporário
            os.remove(temp_grafico)
        
    def gerar_pagina_recomendacoes(self):
        self.add_page()
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Recomendações', 0, 1, 'L')
        self.ln(5)
        
        # Recomendações gerais
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Recomendações Gerais:', 0, 1, 'L')
        
        self.set_font('Arial', '', 10)
        recomendacoes_gerais = [
            "Mantenha uma alimentação balanceada, rica em frutas, vegetais e grãos integrais.",
            "Pratique atividade física regularmente, visando ao menos 150 minutos de atividade moderada por semana.",
            "Realize check-ups médicos anuais para monitoramento dos indicadores de saúde.",
            "Evite o consumo excessivo de álcool e sódio."
        ]
        
        for rec in recomendacoes_gerais:
            self.cell(10, 7, "-", 0, 0)  # Trocando • por -
            self.multi_cell(0, 7, rec)
        
        # Recomendações específicas com base nos fatores de risco
        self.ln(5)
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Recomendações Específicas:', 0, 1, 'L')
        
        self.set_font('Arial', '', 10)
        recomendacoes_especificas = []
        
        # Verificar cada fator de risco e adicionar recomendações específicas
        if self.dados_paciente['totChol'] > 200:
            recomendacoes_especificas.append(
                "Colesterol elevado: Considere reduzir o consumo de gorduras saturadas e trans, " +
                "aumentar a ingestão de fibras solúveis e consultar um médico para avaliação " +
                "da necessidade de tratamento medicamentoso."
            )
            
        if self.dados_paciente['sysBP'] > 120 or self.dados_paciente['diaBP'] > 80:
            recomendacoes_especificas.append(
                "Pressão arterial elevada: Reduza o consumo de sal, mantenha-se fisicamente ativo, " +
                "controle o estresse e, se necessário, consulte um médico para avaliação de " +
                "tratamento medicamentoso."
            )
            
        if self.dados_paciente['BMI'] > 25:
            recomendacoes_especificas.append(
                "IMC elevado: Busque manter um peso saudável através de dieta balanceada " +
                "e atividade física regular. Considere consultar um nutricionista para " +
                "orientações personalizadas."
            )
            
        if self.dados_paciente['glucose'] > 100:
            recomendacoes_especificas.append(
                "Glicose elevada: Reduza o consumo de açúcares e carboidratos refinados, " +
                "mantenha um peso saudável e considere consultar um médico para avaliação " +
                "mais detalhada."
            )
            
        if self.dados_paciente.get('currentSmoker', 0) == 1 or self.dados_paciente.get('cigsPerDay', 0) > 0:
            recomendacoes_especificas.append(
                "Tabagismo: Considere programas de cessação do tabagismo. O abandono do " +
                "hábito de fumar reduz significativamente o risco cardiovascular."
            )
            
        # Se não houver recomendações específicas
        if not recomendacoes_especificas:
            recomendacoes_especificas.append(
                "Seus indicadores estão em níveis saudáveis. Continue mantendo hábitos saudáveis para preservar sua saúde cardiovascular."
            )
            
        for rec in recomendacoes_especificas:
            self.cell(10, 7, "-", 0, 0)
            self.multi_cell(0, 7, rec)
            self.ln(3)
            
        # Disclaimer
        self.ln(10)
        self.set_font('Arial', 'I', 8)
        self.multi_cell(0, 5, 
            "AVISO: Este relatório é baseado em análise estatística e deve ser usado apenas " +
            "como uma ferramenta auxiliar. Consulte sempre um profissional de saúde para " +
            "avaliação completa e recomendações personalizadas."
        )
        
    def gerar_relatorio(self):
        """
        Gera o relatório PDF completo
        """
        self.gerar_pagina_resumo()
        self.gerar_pagina_detalhes()
        self.gerar_pagina_visualizacoes()
        self.gerar_pagina_recomendacoes()
        
        # Salvar o PDF
        nome_arquivo = gerar_nome_arquivo(self.nome_paciente)
        self.output(nome_arquivo)
        print(f"Relatório gerado com sucesso: {nome_arquivo}")
        return nome_arquivo