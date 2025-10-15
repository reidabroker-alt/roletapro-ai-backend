# backend/app/routers/simulator.py

from fastapi import APIRouter, Depends
from .. import schemas, models
from ..security import get_current_active_user
import random

router = APIRouter(prefix="/simulator", tags=["simulator"])

def simular_roleta(config: schemas.SimulatorConfig):
    """Simula rodadas de roleta com base na configuração fornecida."""
    saldo = config.saldo_inicial
    aposta = config.aposta_inicial
    historico = []
    rodada = 0
    
    # Definir cores da roleta (0 é verde, 1-10 e 19-28 são vermelhos, 11-18 e 29-36 são pretos)
    cores = {0: "verde"}
    for i in range(1, 37):
        if i in [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]:
            cores[i] = "vermelho"
        else:
            cores[i] = "preto"
    
    gatilho_ativo = False
    contagem_gatilho = 0
    
    while rodada < config.max_rodadas and saldo > 0:
        rodada += 1
        numero = random.randint(0, 36)
        cor = cores[numero]
        
        # Lógica de gatilho (se aplicável)
        if config.gatilho_cor and config.gatilho_contagem:
            if cor == config.gatilho_cor:
                contagem_gatilho += 1
                if contagem_gatilho >= config.gatilho_contagem:
                    gatilho_ativo = True
            else:
                contagem_gatilho = 0
                gatilho_ativo = False
        else:
            gatilho_ativo = True  # Sem gatilho, sempre ativo
        
        # Fazer aposta se o gatilho estiver ativo
        if gatilho_ativo and saldo >= aposta:
            saldo -= aposta
            
            # Verificar se ganhou
            ganhou = False
            if config.cor_alvo and cor == config.cor_alvo:
                ganhou = True
                saldo += aposta * 2  # Paga 1:1
            
            historico.append({
                "rodada": rodada,
                "numero": numero,
                "cor": cor,
                "aposta": aposta,
                "ganhou": ganhou,
                "saldo": saldo
            })
            
            # Aplicar estratégia
            if config.estrategia == "martingale":
                if ganhou:
                    aposta = config.aposta_inicial
                else:
                    aposta *= 2
            elif config.estrategia == "fibonacci":
                # Implementação simplificada de Fibonacci
                if ganhou:
                    aposta = config.aposta_inicial
                else:
                    aposta = aposta * 1.5  # Simplificação
            elif config.estrategia == "dalembert":
                if ganhou:
                    aposta = max(config.aposta_inicial, aposta - config.aposta_inicial)
                else:
                    aposta += config.aposta_inicial
        else:
            historico.append({
                "rodada": rodada,
                "numero": numero,
                "cor": cor,
                "aposta": 0,
                "ganhou": False,
                "saldo": saldo
            })
    
    return {
        "saldo_final": saldo,
        "lucro": saldo - config.saldo_inicial,
        "total_rodadas": rodada,
        "historico": historico
    }

@router.post("/run")
def run_simulator(
    config: schemas.SimulatorConfig,
    current_user: models.User = Depends(get_current_active_user)
):
    """Executa a simulação de roleta."""
    resultado = simular_roleta(config)
    return resultado

