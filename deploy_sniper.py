#!/usr/bin/env python3
"""
🚀 DEPLOY SNIPER NEØ - SCRIPT DE IMPLANTAÇÃO
Configura e inicia o sistema sniper completo
"""

import os
import sys
import subprocess
import time
import signal
from datetime import datetime

class SniperDeploy:
    def __init__(self):
        self.processes = {}
        
    def check_dependencies(self):
        """Verifica dependências"""
        print("🔍 Verificando dependências...")
        
        required_packages = [
            'streamlit', 'pandas', 'plotly', 'pybit', 
            'python-telegram-bot', 'schedule', 'ta'
        ]
        
        missing = []
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing.append(package)
        
        if missing:
            print(f"❌ Dependências faltando: {missing}")
            print("📦 Instalando dependências...")
            subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing)
        else:
            print("✅ Todas as dependências OK")
    
    def start_dashboard(self):
        """Inicia dashboard"""
        print("🎯 Iniciando Sniper Dashboard...")
        
        try:
            process = subprocess.Popen([
                sys.executable, '-m', 'streamlit', 'run', 'sniper_dashboard.py',
                '--server.port', '8502',
                '--server.headless', 'true'
            ])
            self.processes['dashboard'] = process
            print("✅ Dashboard iniciado na porta 8502")
            return True
        except Exception as e:
            print(f"❌ Erro ao iniciar dashboard: {e}")
            return False
    
    def start_engine(self, chat_id="6582122066", threshold=7.0, interval=15):
        """Inicia engine sniper"""
        print("🥷 Iniciando Sniper Engine...")
        
        try:
            process = subprocess.Popen([
                sys.executable, 'sniper_engine.py', 
                chat_id, str(threshold), str(interval)
            ])
            self.processes['engine'] = process
            print(f"✅ Engine iniciado - Chat: {chat_id}, Threshold: {threshold}, Interval: {interval}min")
            return True
        except Exception as e:
            print(f"❌ Erro ao iniciar engine: {e}")
            return False
    
    def start_telegram_bot(self):
        """Inicia bot do Telegram"""
        print("📱 Iniciando Telegram Bot...")
        
        try:
            process = subprocess.Popen([
                sys.executable, 'telegram_bot.py'
            ])
            self.processes['telegram'] = process
            print("✅ Telegram Bot iniciado")
            return True
        except Exception as e:
            print(f"❌ Erro ao iniciar bot: {e}")
            return False
    
    def show_status(self):
        """Mostra status dos processos"""
        print("\n📊 STATUS DO SISTEMA SNIPER NEØ")
        print("=" * 50)
        
        for name, process in self.processes.items():
            if process.poll() is None:
                print(f"🟢 {name.upper()}: Ativo (PID: {process.pid})")
            else:
                print(f"🔴 {name.upper()}: Inativo")
        
        print(f"\n🌐 Dashboard: http://localhost:8502")
        print(f"📱 Telegram: @nettomello")
        print(f"⏰ Iniciado em: {datetime.now().strftime('%H:%M:%S')}")
    
    def stop_all(self):
        """Para todos os processos"""
        print("\n🛑 Parando sistema...")
        
        for name, process in self.processes.items():
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ {name} parado")
            except:
                process.kill()
                print(f"🔴 {name} forçado a parar")
    
    def run_interactive(self):
        """Modo interativo"""
        print("🥷 SNIPER NEØ - DEPLOY INTERATIVO")
        print("=" * 50)
        
        # Verifica dependências
        self.check_dependencies()
        
        # Configurações
        print("\n⚙️ CONFIGURAÇÕES:")
        chat_id = input(f"Chat ID Telegram [{6582122066}]: ").strip() or "6582122066"
        threshold = float(input(f"Threshold de Score [7.0]: ").strip() or "7.0")
        interval = int(input(f"Intervalo de Análise (min) [15]: ").strip() or "15")
        
        # Inicia serviços
        print("\n🚀 INICIANDO SERVIÇOS...")
        
        services = [
            ("Dashboard", lambda: self.start_dashboard()),
            ("Engine", lambda: self.start_engine(chat_id, threshold, interval)),
            ("Telegram Bot", lambda: self.start_telegram_bot())
        ]
        
        for name, start_func in services:
            if start_func():
                time.sleep(2)  # Aguarda inicialização
            else:
                print(f"❌ Falha ao iniciar {name}")
                return
        
        # Mostra status
        self.show_status()
        
        print("\n🎯 SISTEMA SNIPER NEØ ATIVO!")
        print("Pressione Ctrl+C para parar")
        
        try:
            while True:
                time.sleep(10)
                # Verifica se processos ainda estão rodando
                for name, process in list(self.processes.items()):
                    if process.poll() is not None:
                        print(f"⚠️ {name} parou inesperadamente")
                        del self.processes[name]
        except KeyboardInterrupt:
            print("\n🛑 Parando sistema...")
            self.stop_all()
            print("✅ Sistema parado com sucesso")

def main():
    """Função principal"""
    deploy = SniperDeploy()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        # Modo automático
        deploy.check_dependencies()
        deploy.start_dashboard()
        deploy.start_engine()
        deploy.start_telegram_bot()
        deploy.show_status()
        
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            deploy.stop_all()
    else:
        # Modo interativo
        deploy.run_interactive()

if __name__ == "__main__":
    main()
