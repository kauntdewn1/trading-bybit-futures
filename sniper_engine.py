#!/usr/bin/env python3
"""
🥷 SNIPER ENGINE NEØ - CORE AUTOMATIZADO
Sistema 24/7 que coleta, analisa e dispara alertas
"""

import time
import json
import schedule
from datetime import datetime
from sniper_system import SniperSystem
from sniper_telegram import send_sniper_alert
import logging

# Configuração de logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sniper_engine.log'),
        logging.StreamHandler()
    ]
)

class SniperEngine:
    def __init__(self, chat_id="6582122066", threshold=7.0):
        self.sniper = SniperSystem()
        self.sniper.threshold = threshold
        self.chat_id = chat_id
        self.last_alert_time = None
        self.alert_cooldown = 300  # 5 minutos entre alertas
        self.logger = logging.getLogger(__name__)
        
    def run_sniper_cycle(self):
        """Executa um ciclo completo de análise e alerta"""
        try:
            self.logger.info("🔄 Iniciando ciclo sniper...")
            
            # Executa análise
            best_trade, direction, score = self.sniper.find_best_trade()
            alert = self.sniper.generate_sniper_alert(best_trade, direction, score)
            
            # Verifica cooldown
            current_time = time.time()
            if (self.last_alert_time and 
                current_time - self.last_alert_time < self.alert_cooldown and
                alert["status"] == "TARGET"):
                self.logger.info("⏳ Cooldown ativo - pulando alerta")
                return
            
            # Envia alerta se necessário
            if alert["status"] == "TARGET":
                self.logger.info(f"🎯 ALVO IDENTIFICADO: {alert['data']['symbol']} {direction}")
                success = send_sniper_alert(self.chat_id, alert["alert"])
                
                if success:
                    self.last_alert_time = current_time
                    self.logger.info("✅ Alerta enviado com sucesso")
                else:
                    self.logger.error("❌ Falha ao enviar alerta")
            else:
                self.logger.info("⏳ Nenhum alvo encontrado - aguardando próximo ciclo")
                
        except Exception as e:
            self.logger.error(f"❌ Erro no ciclo sniper: {e}")
    
    def start_engine(self, interval_minutes=15):
        """Inicia o motor sniper com intervalo definido"""
        self.logger.info(f"🚀 SNIPER ENGINE INICIADO - Intervalo: {interval_minutes}min")
        
        # Agenda execução
        schedule.every(interval_minutes).minutes.do(self.run_sniper_cycle)
        
        # Executa imediatamente
        self.run_sniper_cycle()
        
        # Loop principal
        while True:
            schedule.run_pending()
            time.sleep(60)  # Verifica a cada minuto
    
    def run_once(self):
        """Executa uma única análise (para testes)"""
        self.logger.info("🧪 Executando análise única...")
        self.run_sniper_cycle()

def main():
    """Função principal"""
    import sys
    
    # Configurações
    chat_id = sys.argv[1] if len(sys.argv) > 1 else "6582122066"
    threshold = float(sys.argv[2]) if len(sys.argv) > 2 else 7.0
    interval = int(sys.argv[3]) if len(sys.argv) > 3 else 15
    
    # Inicia engine
    engine = SniperEngine(chat_id=chat_id, threshold=threshold)
    
    if len(sys.argv) > 4 and sys.argv[4] == "--once":
        # Modo teste - executa uma vez
        engine.run_once()
    else:
        # Modo contínuo
        engine.start_engine(interval)

if __name__ == "__main__":
    main()
