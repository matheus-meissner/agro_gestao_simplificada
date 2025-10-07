"""
Validação e leitura segura de entradas.
"""
from typing import Tuple

def input_float(msg: str, minimo: float = 0.0) -> float:
    while True:
        try:
            valor = float(input(msg).replace(",", ".").strip())
            if valor < minimo:
                print(f"⚠️  Valor deve ser >= {minimo}.")
                continue
            return valor
        except ValueError:
            print("⚠️  Digite um número válido.")

def input_opcao(msg: str, opcoes: Tuple[str, ...]) -> str:
    opcoes_lower = tuple(o.lower() for o in opcoes)
    while True:
        v = input(msg).strip().lower()
        if v in opcoes_lower:
            return v
        print(f"⚠️  Opção inválida. Use: {', '.join(opcoes)}")

def input_str(msg: str, minimo_len: int = 1) -> str:
    while True:
        v = input(msg).strip()
        if len(v) >= minimo_len:
            return v
        print(f"⚠️  Informe ao menos {minimo_len} caractere(s).")
