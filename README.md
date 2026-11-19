# Trabalho II - Aprendizado Nao Supervisionado

## Integrantes

Preencher antes da entrega:

- Nome completo - matricula
- Nome completo - matricula
- Nome completo - matricula

## Metodos escolhidos

- Tarefa A (agrupamento): K-Means e DBSCAN.
- Tarefa B (reducao): PCA e t-SNE.

## Requisitos

O ambiente usado para validar a analise tem Python 3.6, NumPy 1.19.5,
pandas 1.1.5, scikit-learn 0.24.2 e Matplotlib 3.3.4. Em um ambiente
compativel, instale as dependencias com:

```powershell
python -m pip install numpy==1.19.5 pandas==1.1.5 scikit-learn==0.24.2 matplotlib==3.3.4
```

## Reproducao

1. Deixe os arquivos `Dados_REG.csv`, `Dados_REG_transformado.tsv` e
   `Dados_REG_atividades_transformadas.tsv` nesta pasta.
2. Se precisar refazer a limpeza e as transformacoes, execute:

   ```powershell
   python Limpeza.py
   python transformer.py
   ```

3. Execute a analise completa:

   ```powershell
   python analise_completa.py
   ```

4. O script usa semente aleatoria 42 e organiza os arquivos gerados:
   - `relatorios\`: relatorio final em Markdown e HTML;
   - `resultados\tabelas\`: tabelas TSV com metricas e resultados;
   - `resultados\figuras\`: graficos PNG.
   Consulte `resultados\README.md` para saber para que serve cada arquivo.
   Complete nomes e matriculas no inicio do relatorio antes de entregar.

Abra `relatorios\relatorio_final.html` no navegador para ver o relatorio com
as figuras. Use Imprimir > Salvar como PDF para gerar a versao final em PDF.
A apresentacao em sala pode usar o relatorio e as figuras, sem slides formais.

## Separacao entre codigo reutilizado e implementado

O projeto usa implementacoes das bibliotecas pandas, NumPy, scikit-learn e
Matplotlib. O codigo de `analise_completa.py`, a preparacao dos dados em
`Limpeza.py`/`transformer.py`, os calculos de metricas, as tabelas e os graficos
foram organizados para este trabalho. Declare quaisquer trechos de terceiros
adicionais que o grupo eventualmente tenha reaproveitado.

## Arquivos principais

- `analise_completa.py`: analises A e B, comparacoes, metricas, figuras e
  relatorio.
- `GUIA_APRESENTACAO.md`: requisitos do enunciado mapeados a decisoes,
  evidencias, perguntas provaveis e roteiro para apresentacao.
- `relatorios\relatorio_final.html`: relatorio pronto para leitura/impressao,
  com figuras incorporadas.
- `relatorios\relatorio_final.md`: versao editavel do relatorio.
- `resultados\README.md`: indice com a finalidade de cada tabela e grafico.
