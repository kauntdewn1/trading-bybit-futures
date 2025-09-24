#!/usr/bin/env python3
"""
Telegram Bot SNIPER NEØ + OpenAI Assistant
Bot híbrido com validação de IA para análise de gráficos
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from sniper_ai_enhanced import SniperAIEnhanced

class SniperAITelegramBot:
    """
    Bot Telegram SNIPER NEØ com integração OpenAI Assistant
    """
    
    def __init__(self, telegram_token: str, openai_api_key: str, openai_assistant_id: str):
        """
        Inicializa bot com validação de IA
        
        Args:
            telegram_token: Token do bot Telegram
            openai_api_key: Chave da API OpenAI
            openai_assistant_id: ID do assistant criado no playground
        """
        self.telegram_token = telegram_token
        self.sniper_ai = SniperAIEnhanced(openai_api_key, openai_assistant_id)
        self.bot = Bot(token=telegram_token)
        
        # Configurações
        self.ai_enabled = True
        self.threshold = 7.0
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start"""
        welcome_message = """
🤖 **SNIPER NEØ + AI VALIDATION** 🤖

Sistema híbrido com validação de IA para análise de gráficos.

**Comandos disponíveis:**
/analyze - Análise completa com IA
/analyze_ai BTCUSDT - Análise específica com IA
/ranking - TOP 6 ativos
/status - Status do sistema
/ai_stats - Estatísticas da IA
/toggle_ai - Liga/desliga IA
/threshold 7.0 - Define threshold
/help - Ajuda completa

**Novo:** Validação de IA para análise de gráficos!
        """
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def analyze_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /analyze - Análise completa com IA"""
        await update.message.reply_text("🔍 **Analisando com IA...**", parse_mode='Markdown')
        
        try:
            # Busca melhor trade com IA
            result = self.sniper_ai.find_best_trade_with_ai(self.threshold)
            
            if result.get('status') == 'no_target':
                message = """
❌ **NENHUM ALVO ENCONTRADO**

Threshold atual: {:.1f}/10
IA habilitada: {}

Tente reduzir o threshold ou aguarde melhores condições.
                """.format(self.threshold, "✅" if self.ai_enabled else "❌")
            else:
                # Gera alerta aprimorado com IA
                alert = self.sniper_ai.generate_ai_enhanced_alert(result)
                message = alert
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            error_message = f"❌ **Erro na análise:** {str(e)}"
            await update.message.reply_text(error_message, parse_mode='Markdown')
    
    async def analyze_ai_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /analyze_ai - Análise específica com IA"""
        if not context.args:
            await update.message.reply_text("❌ **Uso:** /analyze_ai BTCUSDT,ETHUSDT")
            return
        
        symbols = [s.upper() for s in context.args[0].split(',')]
        await update.message.reply_text(f"🔍 **Analisando {len(symbols)} ativos com IA...**", parse_mode='Markdown')
        
        try:
            results = []
            for symbol in symbols:
                # Busca dados do ativo
                trade_data = self.sniper_ai.calculate_score(symbol)
                if trade_data and trade_data.get('score', 0) >= self.threshold:
                    # Valida com IA
                    ai_analysis = self.sniper_ai._validate_with_ai(trade_data)
                    trade_data['ai_analysis'] = ai_analysis
                    results.append(trade_data)
            
            if not results:
                message = f"❌ **Nenhum ativo encontrado** com threshold {self.threshold}/10"
            else:
                # Ordena por score
                results.sort(key=lambda x: x.get('score', 0), reverse=True)
                
                message = f"🤖 **ANÁLISE IA - {len(results)} ATIVOS**\n\n"
                for i, result in enumerate(results[:6], 1):
                    ai_conf = result.get('ai_analysis', {}).get('confidence_level', 0)
                    ai_confirm = result.get('ai_analysis', {}).get('signal_confirmation', False)
                    
                    message += f"**{i}º {result['symbol']}**\n"
                    message += f"Score: {result.get('score', 0):.1f}/10\n"
                    message += f"IA: {ai_conf}/10 {'✅' if ai_confirm else '❌'}\n"
                    message += f"Direção: {result.get('direction', 'N/A')}\n\n"
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            error_message = f"❌ **Erro na análise:** {str(e)}"
            await update.message.reply_text(error_message, parse_mode='Markdown')
    
    async def ranking_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /ranking - TOP 6 ativos"""
        await update.message.reply_text("📊 **Gerando ranking...**", parse_mode='Markdown')
        
        try:
            # Busca ranking normal
            ranking = self.sniper_ai.get_full_ranking()
            
            if not ranking:
                message = "❌ **Nenhum ativo encontrado**"
            else:
                message = "🏆 **TOP 6 ATIVOS RANQUEADOS**\n\n"
                for i, asset in enumerate(ranking[:6], 1):
                    message += f"**{i}º {asset['symbol']}**\n"
                    message += f"Score: {asset.get('score', 0):.1f}/10\n"
                    message += f"Direção: {asset.get('direction', 'N/A')}\n"
                    message += f"RSI: {asset.get('rsi', 0):.1f}\n"
                    message += f"MACD: {asset.get('macd', 'N/A')}\n\n"
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            error_message = f"❌ **Erro no ranking:** {str(e)}"
            await update.message.reply_text(error_message, parse_mode='Markdown')
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /status - Status do sistema"""
        try:
            # Busca estatísticas
            ai_stats = self.sniper_ai.get_ai_performance_stats()
            
            message = f"""
🟢 **SISTEMA SNIPER NEØ + AI - ONLINE**

**Configurações:**
- Threshold: {self.threshold}/10
- IA habilitada: {'✅' if self.ai_enabled else '❌'}
- Ativos monitorados: {len(self.sniper_ai.assets)}

**Estatísticas IA:**
- Análises realizadas: {ai_stats.get('total_analyses', 0)}
- Sinais confirmados: {ai_stats.get('confirmed_signals', 0)}
- Taxa de confirmação: {ai_stats.get('confirmation_rate', 0):.1f}%
- Confiança média: {ai_stats.get('avg_confidence', 0):.1f}/10

**Última atualização:** {datetime.now().strftime('%H:%M:%S')}
            """
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            error_message = f"❌ **Erro no status:** {str(e)}"
            await update.message.reply_text(error_message, parse_mode='Markdown')
    
    async def ai_stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /ai_stats - Estatísticas da IA"""
        try:
            ai_stats = self.sniper_ai.get_ai_performance_stats()
            
            message = f"""
🤖 **ESTATÍSTICAS DA IA**

**Performance:**
- Total de análises: {ai_stats.get('total_analyses', 0)}
- Sinais confirmados: {ai_stats.get('confirmed_signals', 0)}
- Taxa de confirmação: {ai_stats.get('confirmation_rate', 0):.1f}%
- Confiança média: {ai_stats.get('avg_confidence', 0):.1f}/10

**Status:**
- IA habilitada: {'✅' if self.ai_enabled else '❌'}
- Threshold IA: {self.sniper_ai.ai_confidence_threshold}/10

**Cache:**
- Análises em cache: {len(self.sniper_ai.ai_analysis_cache)}
            """
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            error_message = f"❌ **Erro nas estatísticas:** {str(e)}"
            await update.message.reply_text(error_message, parse_mode='Markdown')
    
    async def toggle_ai_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /toggle_ai - Liga/desliga IA"""
        self.ai_enabled = self.sniper_ai.toggle_ai()
        
        status = "✅ HABILITADA" if self.ai_enabled else "❌ DESABILITADA"
        message = f"🤖 **IA {status}**\n\nSistema agora {'usa' if self.ai_enabled else 'não usa'} validação de IA."
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def threshold_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /threshold - Define threshold"""
        if not context.args:
            await update.message.reply_text(f"❌ **Uso:** /threshold 7.0\n\nThreshold atual: {self.threshold}")
            return
        
        try:
            new_threshold = float(context.args[0])
            if 0 <= new_threshold <= 10:
                self.threshold = new_threshold
                message = f"✅ **Threshold definido para {new_threshold}/10**"
            else:
                message = "❌ **Threshold deve estar entre 0 e 10**"
        except ValueError:
            message = "❌ **Threshold deve ser um número**"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /help - Ajuda completa"""
        help_message = """
🤖 **SNIPER NEØ + AI - AJUDA COMPLETA**

**Comandos principais:**
/analyze - Análise completa com validação de IA
/analyze_ai BTCUSDT,ETHUSDT - Análise específica com IA
/ranking - TOP 6 ativos ranqueados
/status - Status do sistema e IA

**Comandos de configuração:**
/threshold 7.0 - Define threshold (0-10)
/toggle_ai - Liga/desliga validação de IA
/ai_stats - Estatísticas da IA

**Comandos de ajuda:**
/help - Esta ajuda
/start - Reinicia o bot

**Novo:** Validação de IA para análise de gráficos!
        """
        await update.message.reply_text(help_message, parse_mode='Markdown')
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler de erros"""
        print(f"Erro: {context.error}")
        if update and update.message:
            await update.message.reply_text("❌ **Erro interno do sistema**")
    
    def run_bot(self):
        """Executa o bot"""
        # Cria aplicação
        application = Application.builder().token(self.telegram_token).build()
        
        # Adiciona handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("analyze", self.analyze_command))
        application.add_handler(CommandHandler("analyze_ai", self.analyze_ai_command))
        application.add_handler(CommandHandler("ranking", self.ranking_command))
        application.add_handler(CommandHandler("status", self.status_command))
        application.add_handler(CommandHandler("ai_stats", self.ai_stats_command))
        application.add_handler(CommandHandler("toggle_ai", self.toggle_ai_command))
        application.add_handler(CommandHandler("threshold", self.threshold_command))
        application.add_handler(CommandHandler("help", self.help_command))
        
        # Handler de erros
        application.add_error_handler(self.error_handler)
        
        # Inicia o bot
        print("🤖 SNIPER NEØ + AI Bot iniciado!")
        print("Pressione Ctrl+C para parar")
        
        try:
            application.run_polling()
        except KeyboardInterrupt:
            print("\n🛑 Bot parado pelo usuário")

# Exemplo de uso
def main():
    """Função principal"""
    # Configuração (substitua pelos seus valores)
    TELEGRAM_TOKEN = "seu_telegram_token"
    OPENAI_API_KEY = "sua_api_key_openai"
    OPENAI_ASSISTANT_ID = "seu_assistant_id"
    
    # Cria e executa bot
    bot = SniperAITelegramBot(TELEGRAM_TOKEN, OPENAI_API_KEY, OPENAI_ASSISTANT_ID)
    bot.run_bot()

if __name__ == "__main__":
    main()
