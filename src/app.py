"""
Aplicação CLI principal.
Cobre: funções, estruturas de dados, arquivos (JSON+TXT) e Oracle.
"""
import uuid, datetime
from typing import List, Dict

from calculos import calcular_perda_ton
from validacao import input_float, input_opcao, input_str
from io_arquivos import carregar_json, salvar_json, log
import db_oracle
from colorama import Fore, Style, init

# "Tabela de memória" (lista de dicionários)
colheitas: List[Dict] = []


def title(txt: str):
    bar = "─" * (len(txt) + 2)
    print(Fore.CYAN + f"\n┌{bar}┐")
    print("│ " + Fore.GREEN + txt + Fore.CYAN + " │")
    print(f"└{bar}┘" + Style.RESET_ALL)

def section(txt: str):
    print(Fore.BLUE + f"\n» {txt}" + Style.RESET_ALL)

def ok(msg: str):    print(Fore.GREEN + "✅ " + msg + Style.RESET_ALL)
def warn(msg: str):  print(Fore.YELLOW + "⚠️  " + msg + Style.RESET_ALL)
def err(msg: str):   print(Fore.RED + "❌ " + msg + Style.RESET_ALL)

def moeda(v: float) -> str:
    s = f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {s}"

def card_header(txt):
    bar = "═" * (len(txt) + 4)
    print(Fore.CYAN + f"\n╔{bar}╗")
    print(f"║  {Fore.YELLOW}{txt}{Style.RESET_ALL}{Fore.CYAN}  ║")
    print(f"╚{bar}╝" + Style.RESET_ALL)




def cadastrar_colheita():
    print("\n🆕 Cadastro de Colheita")
    talhao = input_str("Talhão: ")
    area = input_float("Área (ha): ", minimo=0.01)
    prod = input_float("Produtividade (t/ha): ", minimo=0.01)
    metodo = input_opcao("Método [manual/mecanica]: ", ("manual", "mecanica"))
    preco = input_float("Preço (R$/t): ", minimo=0.0)

    perda_pct, perda_ton, total_ton = calcular_perda_ton(prod, area, metodo)

    reg = {
        "id": str(uuid.uuid4()),
        "data": datetime.date.today().isoformat(),
        "talhao": talhao,
        "area_ha": round(area, 2),
        "produtividade_t_ha": round(prod, 2),
        "metodo": metodo,
        "preco_ton": round(preco, 2),
        "perda_pct": perda_pct,
        "perda_ton": perda_ton,
        "perda_reais": round(perda_ton * preco, 2),
        "total_ton": total_ton
    }
    colheitas.append(reg)
    log(f"Cadastrada colheita {reg['id']} ({talhao})")
    print("✅ Registro adicionado.")

def listar_colheitas():
    if not colheitas:
        warn("Sem registros.")
        return

    section("Colheitas")

    for i, r in enumerate(colheitas, 1):
        # Cabeçalho do “cartão”
        card_header(f"Registro #{i} – {r['talhao']}")
        # Campos, um por linha (vertical)
        print(f"{Fore.GREEN}Data:{Style.RESET_ALL} {r['data']}")
        print(f"{Fore.CYAN}Método:{Style.RESET_ALL} {r['metodo']}")
        print(f"{Fore.WHITE}Área:{Style.RESET_ALL} {r['area_ha']} ha")
        print(f"{Fore.WHITE}Produtividade:{Style.RESET_ALL} {r['produtividade_t_ha']} t/ha")
        print(f"{Fore.RED}Perda:{Style.RESET_ALL} {r['perda_ton']} t")
        print(f"{Fore.RED}Custo da perda:{Style.RESET_ALL} {moeda(r['perda_reais'])}")




def resumo_perdas():
    total_ton = sum(r["total_ton"] for r in colheitas)
    total_perda_ton = sum(r["perda_ton"] for r in colheitas)
    total_perda_reais = sum(r["perda_reais"] for r in colheitas)
    title("Resumo de Perdas")
    print(f"Total produzido (t): {Fore.GREEN}{round(total_ton,2)}{Style.RESET_ALL}")
    print(f"Total perdido   (t): {Fore.RED}{round(total_perda_ton,2)}{Style.RESET_ALL}")
    print(f"Custo da perda  (R$): {Fore.RED}{moeda(total_perda_reais)}{Style.RESET_ALL}")


def salvar_carregar():
    section("Persistência")
    print("1) Salvar JSON\n2) Carregar JSON")
    op = input(Fore.CYAN + "Escolha: " + Style.RESET_ALL).strip()
    if op == "1":
        salvar_json(colheitas); log("Salvou JSON"); ok("Salvo em data/colheitas.json")
    elif op == "2":
        colheitas.clear(); colheitas.extend(carregar_json()); log("Carregou JSON")
        ok(f"Carregados {len(colheitas)} registro(s).")
    else:
        warn("Opção inválida.")


def oracle_ops():
    section("Oracle")
    print("1) Criar tabela\n2) Exportar dados\n3) Consultar")
    op = input(Fore.CYAN + "Escolha: " + Style.RESET_ALL).strip()
    try:
        conn = db_oracle.conectar()
    except Exception as e:
        err(f"Conexão Oracle indisponível: {e}")
        return

    if op == "1":
        msg = db_oracle.criar_tabela(conn); print(Fore.YELLOW + f"ℹ️  {msg}" + Style.RESET_ALL)
    elif op == "2":
        msg = db_oracle.exportar(colheitas, conn); ok(msg)
    elif op == "3":
        # (por enquanto, mantém a saída original / depois a gente troca pela tabela bonita do db_oracle)
        rows = db_oracle.consultar(conn)
        section("Registros no Oracle")
        for r in rows: print(r)
    else:
        warn("Opção inválida.")
    try: conn.close()
    except: pass


def menu():
    title("AgroGestão • Perdas na Colheita de Cana")
    while True:
        print(
            Fore.MAGENTA +
            "\n[1] Cadastrar colheita\n"
            "[2] Listar colheitas\n"
            "[3] Resumo de perdas\n"
            "[4] Salvar/Carregar JSON\n"
            "[5] Oracle (criar/exportar/consultar)\n"
            "[6] Sair" +
            Style.RESET_ALL
        )
        op = input(Fore.CYAN + "Escolha: " + Style.RESET_ALL).strip()
        if op == "1": cadastrar_colheita()
        elif op == "2": listar_colheitas()
        elif op == "3": resumo_perdas()
        elif op == "4": salvar_carregar()
        elif op == "5": oracle_ops()
        elif op == "6":
            print(Fore.CYAN + "Até mais! 👋" + Style.RESET_ALL)
            break
        else:
            warn("Opção inválida.")


if __name__ == "__main__":
    # carrega automaticamente dados prévios (se quiser, comente esta linha)
    colheitas.extend(carregar_json())
    menu()
