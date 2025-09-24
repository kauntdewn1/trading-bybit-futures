#!/usr/bin/env python3
"""
🥷 ASSISTANT OPENAI + TELEGRAM BOT NEØ - SISTEMA INTEGRADO
Bot que conecta OpenAI Assistant com Telegram para sinais automáticos
"""

import openai
import requests
import time
import os
from dotenv import load_dotenv
from sniper_system import SniperSystem
from datetime import datetime

load_dotenv()

class AssistantTelegramBot:
    def __init__(self):
        # Configurações
        self.openai_api_key = os.getenv('OPENAI_SECRET_KEY')
        self.assistant_id = os.getenv('OPENAI_ASSISTANT_ID', 'asst_1234567890')  # Configure seu Assistant ID
        self.telegram_token = os.getenv('TELEGRAM_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID', '6582122066')
        self.intervalo_minutos = 15  # Intervalo entre sinais
        
        # Inicializa sistemas
        self.sniper = SniperSystem()
        self.client = openai.OpenAI(api_key=self.openai_api_key)
        
        print(f"🥷 ASSISTANT TELEGRAM BOT NEØ INICIADO")
        print(f"📊 Intervalo: {self.intervalo_minutos} minutos")
        print(f"🎯 Chat ID: {self.telegram_chat_id}")
    
    def get_sinal_assistant(self, pergunta):
        """Obtém sinal do Assistant OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Você é um especialista em trading de futuros cripto. Analise dados de mercado e forneça sinais precisos de entrada/saída."},
                    {"role": "user", "content": pergunta}
                ],
                temperature=0.3,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ Erro ao consultar Assistant: {e}")
            return None
    
    def get_sinal_sniper(self):
        """Obtém sinal do sistema Sniper local"""
        try:
            # Executa scan completo
            self.sniper.assets = self.sniper.get_all_futures_symbols()
            ranking = self.sniper.get_full_ranking()
            
            if not ranking:
                return "⏳ Nenhum sinal encontrado no momento"
            
            # Pega o melhor sinal
            best = ranking[0]
            if best['score'] >= self.sniper.threshold:
                return self.format_sniper_signal(best)
            else:
                return f"⏳ Nenhum sinal acima do threshold {self.sniper.threshold}/10"
                
        except Exception as e:
            print(f"❌ Erro no sistema Sniper: {e}")
            return f"❌ Erro no sistema: {str(e)}"
    
    def format_sniper_signal(self, signal):
        """Formata sinal do Sniper para Telegram"""
        emoji = "🟢" if signal['direcao'] == "LONG" else "🔴"
        
        message = f"""
🔥 <b>SINAL SNIPER NEØ</b>

{emoji} <b>{signal['ativo']}</b> {signal['direcao']}
📊 Score: <b>{signal['score']}/10</b>

📈 <b>Indicadores:</b>
• RSI: {signal['dados']['rsi']:.1f}
• MACD: {signal['dados']['macd']}
• Volume: {signal['dados']['volume']}
• Funding: {signal['dados']['funding']:.4f}%

⏱️ {datetime.now().strftime('%H:%M:%S')} | Node NΞØ
        """
        return message.strip()
    
    def send_telegram(self, mensagem):
        """Envia mensagem para Telegram"""
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        data = {
            "chat_id": self.telegram_chat_id,
            "text": mensagem,
            "parse_mode": "HTML"
        }
        
        try:
            response = requests.post(url, data=data, timeout=10)
            if response.status_code == 200:
                print("✅ Sinal enviado para Telegram")
                return True
            else:
                print(f"❌ Falha ao enviar: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Erro ao enviar Telegram: {e}")
            return False
    
    def run_cycle(self):
        """Executa um ciclo completo de análise"""
        print(f"\n🔍 CICLO DE ANÁLISE - {datetime.now().strftime('%H:%M:%S')}")
        
        # Opção 1: Usar sistema Sniper local
        print("📊 Executando scan Sniper local...")
        sinal = self.get_sinal_sniper()
        
        # Opção 2: Usar Assistant OpenAI (descomente para usar)
        # print("🤖 Consultando Assistant OpenAI...")
        # pergunta = "Qual o melhor ativo futuro para trade curto agora? Me entregue o sinal mais forte (long ou short), pronto pra operar."
        # sinal = self.get_sinal_assistant(pergunta)
        
        if sinal:
            print("📱 Enviando sinal para Telegram...")
            self.send_telegram(sinal)
            print("✅ Ciclo concluído")
        else:
            print("⏳ Nenhum sinal para enviar")
    
    def run_continuous(self):
        """Executa loop contínuo"""
        print(f"🚀 INICIANDO LOOP CONTÍNUO - {self.intervalo_minutos}min")
        print("Pressione Ctrl+C para parar")
        
        try:
            while True:
                self.run_cycle()
                print(f"⏳ Aguardando {self.intervalo_minutos} minutos...")
                time.sleep(self.intervalo_minutos * 60)
        except KeyboardInterrupt:
            print("\n🛑 Bot interrompido pelo usuário")
        except Exception as e:
            print(f"❌ Erro no loop: {e}")
    
    def run_once(self):
        """Executa análise única"""
        print("🎯 EXECUÇÃO ÚNICA")
        self.run_cycle()

def main():
    """Função principal"""
    import sys
    
    bot = AssistantTelegramBot()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        # Execução única
        bot.run_once()
    else:
        # Loop contínuo
        bot.run_continuous()

if __name__ == "__main__":
    main()
