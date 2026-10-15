"""
RentSmart — Sistema de Orçamento de Locação
R.M Imóveis | Projeto acadêmico de Python e Programação Orientada a Objetos

Execução:
    python rentsmart.py

O programa gera um CSV com a projeção dos 12 meses no diretório de execução.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
import csv
from pathlib import Path


CENTAVO = Decimal("0.01")
TAXA_CONTRATUAL = Decimal("2000.00")


def dinheiro(valor: Decimal) -> Decimal:
    """Arredonda um valor monetário para duas casas decimais."""
    return Decimal(valor).quantize(CENTAVO, rounding=ROUND_HALF_UP)


def formatar_brl(valor: Decimal) -> str:
    """Formata um Decimal no padrão monetário brasileiro."""
    valor = dinheiro(valor)
    texto = f"{valor:,.2f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def ler_inteiro(mensagem: str, minimo: int, maximo: int) -> int:
    """Lê e valida um número inteiro dentro de um intervalo inclusivo."""
    while True:
        entrada = input(mensagem).strip()
        try:
            valor = int(entrada)
            if minimo <= valor <= maximo:
                return valor
            print(f"Informe um número entre {minimo} e {maximo}.")
        except ValueError:
            print("Entrada inválida. Digite um número inteiro.")


def ler_sim_nao(mensagem: str) -> bool:
    """Lê uma resposta afirmativa/negativa."""
    while True:
        resposta = input(mensagem).strip().lower()
        if resposta in ("s", "sim"):
            return True
        if resposta in ("n", "nao", "não"):
            return False
        print("Resposta inválida. Digite S para sim ou N para não.")


@dataclass
class Orcamento:
    """Representa os valores calculados para uma proposta de locação."""
    aluguel_base: Decimal
    adicional_quartos: Decimal
    adicional_estacionamento: Decimal
    desconto: Decimal
    aluguel_mensal: Decimal
    taxa_contratual: Decimal
    parcelas_taxa: int
    valores_parcelas: list[Decimal]

    @property
    def valor_parcela_taxa(self) -> Decimal:
        return self.valores_parcelas[0] if self.valores_parcelas else Decimal("0.00")


class Imovel:
    """Classe-base para os tipos de imóvel disponíveis na imobiliária."""

    def __init__(self, categoria: str, aluguel_base: Decimal):
        self.categoria = categoria
        self.aluguel_base = aluguel_base

    def calcular_adicional_quartos(self, quartos: int) -> Decimal:
        """Calcula adicional de quartos conforme a categoria."""
        return Decimal("0.00")

    def calcular_estacionamento(self, deseja_estacionamento: bool,
                                vagas_adicionais: int = 0) -> Decimal:
        """Calcula custo mensal de estacionamento."""
        return Decimal("0.00")

    def permite_desconto_sem_criancas(self) -> bool:
        return False


class Apartamento(Imovel):
    """Apartamento: base de R$ 700 e adicional de R$ 200 para dois quartos."""

    def __init__(self):
        super().__init__("Apartamento", Decimal("700.00"))

    def calcular_adicional_quartos(self, quartos: int) -> Decimal:
        return Decimal("200.00") if quartos == 2 else Decimal("0.00")

    def calcular_estacionamento(self, deseja_estacionamento: bool,
                                vagas_adicionais: int = 0) -> Decimal:
        return Decimal("300.00") if deseja_estacionamento else Decimal("0.00")

    def permite_desconto_sem_criancas(self) -> bool:
        return True


class Casa(Imovel):
    """Casa: base de R$ 900 e adicional de R$ 250 para dois quartos."""

    def __init__(self):
        super().__init__("Casa", Decimal("900.00"))

    def calcular_adicional_quartos(self, quartos: int) -> Decimal:
        return Decimal("250.00") if quartos == 2 else Decimal("0.00")

    def calcular_estacionamento(self, deseja_estacionamento: bool,
                                vagas_adicionais: int = 0) -> Decimal:
        return Decimal("300.00") if deseja_estacionamento else Decimal("0.00")


class Estudio(Imovel):
    """Estúdio: base de R$ 1.200; pacote opcional de duas vagas por R$ 250
    e R$ 60 por cada vaga adicional.
    """

    def __init__(self):
        super().__init__("Estúdio", Decimal("1200.00"))

    def calcular_estacionamento(self, deseja_estacionamento: bool,
                                vagas_adicionais: int = 0) -> Decimal:
        if not deseja_estacionamento:
            return Decimal("0.00")
        return Decimal("250.00") + Decimal("60.00") * vagas_adicionais


class Locacao:
    """Coordena regras comerciais e produz o orçamento da locação."""

    def __init__(self, imovel: Imovel, quartos: int = 1,
                 deseja_estacionamento: bool = False,
                 vagas_adicionais: int = 0,
                 sem_criancas: bool = False,
                 parcelas_taxa: int = 1):
        if imovel.categoria in ("Apartamento", "Casa") and quartos not in (1, 2):
            raise ValueError("Casas e apartamentos aceitam 1 ou 2 quartos.")
        if imovel.categoria == "Estúdio" and quartos != 1:
            raise ValueError("Para estúdio, utilize o valor padrão de quartos.")
        if vagas_adicionais < 0:
            raise ValueError("O número de vagas adicionais não pode ser negativo.")
        if imovel.categoria != "Estúdio" and vagas_adicionais != 0:
            raise ValueError("Vagas adicionais só se aplicam a estúdios.")
        if imovel.categoria != "Estúdio" and deseja_estacionamento and vagas_adicionais:
            raise ValueError("Casas e apartamentos possuem adicional fixo de garagem.")
        if not 1 <= parcelas_taxa <= 5:
            raise ValueError("A taxa contratual pode ser parcelada de 1 a 5 vezes.")

        self.imovel = imovel
        self.quartos = quartos
        self.deseja_estacionamento = deseja_estacionamento
        self.vagas_adicionais = vagas_adicionais
        self.sem_criancas = sem_criancas
        self.parcelas_taxa = parcelas_taxa

    def calcular_orcamento(self) -> Orcamento:
        """Calcula aluguel, adicionais, desconto e parcelas contratuais."""
        base = dinheiro(self.imovel.aluguel_base)
        adicional_quartos = dinheiro(
            self.imovel.calcular_adicional_quartos(self.quartos)
        )
        adicional_estacionamento = dinheiro(
            self.imovel.calcular_estacionamento(
                self.deseja_estacionamento, self.vagas_adicionais
            )
        )

        subtotal = base + adicional_quartos + adicional_estacionamento
        desconto = Decimal("0.00")
        if self.imovel.permite_desconto_sem_criancas() and self.sem_criancas:
            desconto = dinheiro(subtotal * Decimal("0.05"))

        aluguel_mensal = dinheiro(subtotal - desconto)
        valores_parcelas = self._calcular_parcelas(TAXA_CONTRATUAL, self.parcelas_taxa)

        return Orcamento(
            aluguel_base=base,
            adicional_quartos=adicional_quartos,
            adicional_estacionamento=adicional_estacionamento,
            desconto=desconto,
            aluguel_mensal=aluguel_mensal,
            taxa_contratual=TAXA_CONTRATUAL,
            parcelas_taxa=self.parcelas_taxa,
            valores_parcelas=valores_parcelas,
        )

    @staticmethod
    def _calcular_parcelas(total: Decimal, quantidade: int) -> list[Decimal]:
        """Divide a taxa e ajusta a última parcela para fechar o total exato."""
        parcela_padrao = dinheiro(total / Decimal(quantidade))
        parcelas = [parcela_padrao for _ in range(quantidade)]
        parcelas[-1] = dinheiro(total - sum(parcelas[:-1], Decimal("0.00")))
        return parcelas

    def gerar_projecao_csv(self, orcamento: Orcamento,
                           caminho: str | Path = "projecao_rentsmart.csv") -> Path:
        """Cria CSV com aluguel, taxa contratual e total previsto em 12 meses."""
        destino = Path(caminho)
        destino.parent.mkdir(parents=True, exist_ok=True)
        date.today()
        with destino.open("w", newline="", encoding="utf-8-sig") as arquivo:
            escritor = csv.writer(arquivo, delimiter=";")
            escritor.writerow([
                "Mes", "Aluguel mensal (R$)",
                "Parcela taxa contratual (R$)", "Total previsto no mes (R$)"
            ])
            for mes in range(1, 13):
                parcela = (
                    orcamento.valores_parcelas[mes - 1]
                    if mes <= orcamento.parcelas_taxa
                    else Decimal("0.00")
                )
                total_mes = dinheiro(orcamento.aluguel_mensal + parcela)
                escritor.writerow([
                    f"Mês {mes}",
                    f"{orcamento.aluguel_mensal:.2f}".replace(".", ","),
                    f"{parcela:.2f}".replace(".", ","),
                    f"{total_mes:.2f}".replace(".", ","),
                ])
        return destino


def selecionar_imovel() -> tuple[Imovel, int]:
    """Apresenta as categorias e coleta o número de quartos quando aplicável."""
    print("\\n=== RENTSMART | R.M IMÓVEIS ===")
    print("1 - Apartamento (1 quarto: R$ 700,00)")
    print("2 - Casa (1 quarto: R$ 900,00)")
    print("3 - Estúdio (R$ 1.200,00)")
    opcao = ler_inteiro("Escolha o tipo de imóvel (1-3): ", 1, 3)

    if opcao == 1:
        imovel = Apartamento()
        quartos = ler_inteiro("Quantidade de quartos (1 ou 2): ", 1, 2)
    elif opcao == 2:
        imovel = Casa()
        quartos = ler_inteiro("Quantidade de quartos (1 ou 2): ", 1, 2)
    else:
        imovel = Estudio()
        quartos = 1
    return imovel, quartos


def main() -> None:
    """Executa o fluxo de interação, cálculo, exibição e exportação."""
    imovel, quartos = selecionar_imovel()

    if imovel.categoria == "Estúdio":
        estacionamento = ler_sim_nao(
            "Deseja o pacote de estacionamento (duas vagas por R$ 250,00)? (S/N): "
        )
        vagas_extras = (
            ler_inteiro("Quantas vagas adicionais deseja? (0-20): ", 0, 20)
            if estacionamento else 0
        )
    else:
        estacionamento = ler_sim_nao(
            "Deseja vaga de garagem por R$ 300,00 mensais? (S/N): "
        )
        vagas_extras = 0

    sem_criancas = False
    if imovel.categoria == "Apartamento":
        sem_criancas = ler_sim_nao(
            "O cliente informa não possuir crianças e deseja aplicar o desconto de 5%? (S/N): "
        )

    parcelas = ler_inteiro(
        "Em quantas parcelas deseja pagar a taxa contratual de R$ 2.000,00 (1-5)? ",
        1, 5
    )

    locacao = Locacao(
        imovel=imovel,
        quartos=quartos,
        deseja_estacionamento=estacionamento,
        vagas_adicionais=vagas_extras,
        sem_criancas=sem_criancas,
        parcelas_taxa=parcelas,
    )
    orcamento = locacao.calcular_orcamento()

    print("\\n" + "=" * 48)
    print("RESUMO DO ORÇAMENTO — RENTSMART")
    print("=" * 48)
    print(f"Imóvel: {imovel.categoria}")
    if imovel.categoria != "Estúdio":
        print(f"Quartos: {quartos}")
    else:
        print(f"Estacionamento: {'pacote de duas vagas' if estacionamento else 'não contratado'}")
        if estacionamento:
            print(f"Vagas adicionais: {vagas_extras}")
    print(f"Aluguel-base:                    {formatar_brl(orcamento.aluguel_base)}")
    print(f"Adicional por quartos:           {formatar_brl(orcamento.adicional_quartos)}")
    print(f"Adicional de estacionamento:     {formatar_brl(orcamento.adicional_estacionamento)}")
    print(f"Desconto aplicado:              -{formatar_brl(orcamento.desconto)}")
    print("-" * 48)
    print(f"ALUGUEL MENSAL:                  {formatar_brl(orcamento.aluguel_mensal)}")
    print(f"Taxa contratual (separada):      {formatar_brl(orcamento.taxa_contratual)}")
    print(f"Parcelamento da taxa:            {parcelas}x")
    print("Parcelas: " + ", ".join(formatar_brl(p) for p in orcamento.valores_parcelas))
    print(f"Total previsto no 1º mês:        {formatar_brl(orcamento.aluguel_mensal + orcamento.valores_parcelas[0])}")
    print("=" * 48)

    arquivo_csv = locacao.gerar_projecao_csv(orcamento)
    print(f"Projeção de 12 meses gerada em: {arquivo_csv.resolve()}")
    print("Observação: o CSV separa aluguel e parcela contratual; após a última parcela,")
    print("o total mensal previsto corresponde apenas ao aluguel mensal.")


if __name__ == "__main__":
    main()
