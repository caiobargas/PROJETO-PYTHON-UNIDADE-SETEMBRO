# RentSmart — Sistema de Orçamento de Locação

Projeto acadêmico em Python para automatizar o cálculo de orçamentos de locação da R.M Imóveis, utilizando Programação Orientada a Objetos (POO).

## Requisitos
- Python 3.10 ou superior
- Nenhuma biblioteca externa é necessária

## Como executar
1. Baixe ou extraia os arquivos do projeto.
2. Abra um terminal na pasta do projeto.
3. Execute:

   ```bash
   python rentsmart.py
   ```

   Em alguns sistemas, o comando pode ser `python3 rentsmart.py`.

4. Responda às perguntas exibidas no terminal.
5. O programa exibirá o resumo do orçamento e criará o arquivo `projecao_rentsmart.csv` na pasta de execução.

## Regras implementadas
- Apartamento: R$ 700,00 com um quarto; adicional de R$ 200,00 para dois quartos.
- Casa: R$ 900,00 com um quarto; adicional de R$ 250,00 para dois quartos.
- Estúdio: R$ 1.200,00.
- Garagem de casa/apartamento: adicional de R$ 300,00 por mês.
- Estúdio: pacote opcional de duas vagas por R$ 250,00 e R$ 60,00 por vaga adicional.
- Apartamento sem crianças: desconto de 5% sobre o subtotal após os adicionais.
- Taxa contratual: R$ 2.000,00, parcelável de 1 a 5 vezes e apresentada separadamente do aluguel.
- Projeção: 12 meses em CSV, com aluguel, parcela da taxa e total previsto de cada mês.

## Organização e POO
- `Imovel`: classe-base com atributos e métodos de cálculo.
- `Apartamento`, `Casa` e `Estudio`: especializações que implementam regras específicas.
- `Locacao`: valida os dados e coordena os cálculos e a exportação CSV.
- `Orcamento`: estrutura os valores finais calculados.
- Funções auxiliares: validação de entradas e formatação monetária.

## Observações sobre as regras
O pacote de estacionamento do estúdio foi implementado como opcional; quando contratado, inclui duas vagas por R$ 250,00 e cada vaga adicional custa R$ 60,00. A taxa contratual não é somada ao aluguel mensal recorrente: suas parcelas aparecem separadamente no CSV e no total previsto de cada um dos primeiros meses, conforme o parcelamento escolhido.

## GitHub
Para publicar o projeto:
1. Entre em https://github.com/new e crie um repositório chamado `RentSmart`.
2. Envie `rentsmart.py`, `README.md`, `Relatorio_RentSmart.pdf` e, se desejar, `Relatorio_RentSmart.docx`.
3. Pelo terminal, dentro da pasta do projeto, use:

   ```bash
   git init
   git add .
   git commit -m "Entrega inicial do projeto RentSmart"
   git branch -M main
   git remote add origin https://github.com/SEU-USUARIO/RentSmart.git
   git push -u origin main
   ```

Substitua `SEU-USUARIO` pelo seu nome de usuário do GitHub. O endereço acima é um modelo, não um repositório já publicado.
