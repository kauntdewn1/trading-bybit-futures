#!/usr/bin/env python3
"""
Telegram Bot SNIPER NEØ + Pai do Trade OpenAI
Bot híbrido que ativa Assistant no final da análise
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from sniper_system import SniperSystem
from openai_pai_do_trade import PaiDoTradeOpenAI

class SniperEnhancedTelegramBot:
    """
    Bot Telegram SNIPER NEØ com integração Pai do Trade OpenAI
    Ativa Assistant apenas no final da análise
    """
    
    def __init__(self, telegram_token: str):
        """
        Inicializa bot com integração OpenAI
        
        Args:
            telegram_token: Token do bot Telegram
        """
        self.telegram_token = telegram_token
        self.sniper = SniperSystem()
        self.pai_do_trade = PaiDoTradeOpenAI()
        
        # Configurações
        self.threshold = 7.0
        self.ai_enabled = True
    
    def _sanitize_text(self, text: str) -> str:
        """Sanitiza texto para evitar problemas de parse no Telegram"""
        if not text:
            return "N/A"
        
        # Remove caracteres problemáticos
        text = str(text)
        text = text.replace('_', '\\_')  # Escapa underscores
        text = text.replace('*', '\\*')  # Escapa asteriscos
        text = text.replace('[', '\\[')  # Escapa colchetes
        text = text.replace(']', '\\]')  # Escapa colchetes
        text = text.replace('`', '\\`')  # Escapa backticks
        
        return text
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start"""
        welcome_message = """
🤖 **SNIPER NEØ + PAI DO TRADE** 🤖

Sistema híbrido com análise avançada de IA.

**Comandos disponíveis:**
/analyze - Análise completa com IA
/analyze_ai BTCUSDT,ETHUSDT - Análise específica com IA
/ranking - TOP 6 ativos
/status - Status do sistema
/toggle_ai - Liga/desliga IA
/threshold 7.0 - Define threshold
/help - Ajuda completa

**Novo:** Pai do Trade OpenAI para análise avançada!
        """
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def analyze_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /analyze - Análise completa com IA"""
        await update.message.reply_text("🔍 **Analisando com SNIPER NEØ...**", parse_mode='Markdown')
        
        try:
            # Busca melhor trade
            best_trade = self.sniper.find_best_trade()
            
            if not best_trade or best_trade.get('symbol') is None:
                message = """
❌ **NENHUM ALVO ENCONTRADO**

Threshold atual: {:.1f}/10
IA habilitada: {}

Tente reduzir o threshold ou aguarde melhores condições.
                """.format(self.threshold, "✅" if self.ai_enabled else "❌")
                
                await update.message.reply_text(message, parse_mode='Markdown')
                return
            
            # Gera alerta normal
            normal_alert = self.sniper.generate_sniper_alert(
                best_trade["data"], 
                best_trade["direction"], 
                best_trade["score"], 
                best_trade.get("frenzy_count", 0)
            )
            await update.message.reply_text(normal_alert["alert"], parse_mode='Markdown')
            
            # Se IA habilitada, ativa análise avançada
            if self.ai_enabled:
                await update.message.reply_text("🤖 **Ativando Pai do Trade OpenAI...**", parse_mode='Markdown')
                
                # Busca TOP 6 ativos para análise avançada
                top_6_data = self._get_top_6_assets()
                
                if top_6_data:
                    # Analisa com Pai do Trade
                    ai_analysis = self.pai_do_trade.analyze_top_6_assets(top_6_data)
                    
                    if ai_analysis.get("error"):
                        error_msg = f"⚠️ **Erro na análise IA:** {ai_analysis['error']}"
                        await update.message.reply_text(error_msg, parse_mode='Markdown')
                    else:
                        # Gera mensagem aprimorada
                        enhanced_message = self.pai_do_trade.generate_enhanced_telegram_message(
                            top_6_data, ai_analysis
                        )
                        await update.message.reply_text(enhanced_message, parse_mode='Markdown')
                else:
                    await update.message.reply_text("⚠️ **Nenhum ativo encontrado para análise avançada**", parse_mode='Markdown')
            
        except Exception as e:
            error_message = f"❌ **Erro na análise:** {str(e)}"
            await update.message.reply_text(error_message, parse_mode='Markdown')
    
    async def analyze_ai_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /analyze_ai - Análise específica com IA"""
        if not context.args:
            await update.message.reply_text("❌ **Uso:** /analyze_ai BTCUSDT,ETHUSDT")
            return
        
        symbols = [s.upper() for s in context.args[0].split(',')]
        await update.message.reply_text(f"🔍 **Analisando {len(symbols)} ativos com Pai do Trade...**", parse_mode='Markdown')
        
        try:
            # Busca dados dos ativos específicos
            specific_data = []
            for symbol in symbols:
                result = self.sniper.calculate_score(symbol)
                if result and result.get("data") is not None:
                    # Determina melhor direção e score
                    long_score = result["long"]
                    short_score = result["short"]
                    
                    if long_score > short_score:
                        melhor_direcao = "LONG"
                        melhor_score = long_score
                    else:
                        melhor_direcao = "SHORT"
                        melhor_score = short_score
                    
                    if melhor_score >= self.threshold:
                        specific_data.append({
                            "symbol": symbol,
                            "direction": melhor_direcao,
                            "score": melhor_score,
                            "rsi": result["data"]["rsi"],
                            "macd": result["data"]["macd"],
                            "volume": result["data"]["volume"],
                            "funding_rate": result["data"]["funding"],
                            "oi_trend": result["data"]["oi"],
                            "price": result["data"]["price"]
                        })
            
            if not specific_data:
                message = f"❌ **Nenhum ativo encontrado** com threshold {self.threshold}/10"
                await update.message.reply_text(message, parse_mode='Markdown')
                return
            
            # Analisa com Pai do Trade
            ai_analysis = self.pai_do_trade.analyze_top_6_assets(specific_data)
            
            if ai_analysis.get("error"):
                error_msg = f"⚠️ **Erro na análise IA:** {ai_analysis['error']}"
                await update.message.reply_text(error_msg, parse_mode='Markdown')
            else:
                # Gera mensagem aprimorada
                enhanced_message = self.pai_do_trade.generate_enhanced_telegram_message(
                    specific_data, ai_analysis
                )
                await update.message.reply_text(enhanced_message, parse_mode='Markdown')
            
        except Exception as e:
            error_message = f"❌ **Erro na análise:** {str(e)}"
            await update.message.reply_text(error_message, parse_mode='Markdown')
    
    async def ranking_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /ranking - TOP 6 ativos"""
        await update.message.reply_text("📊 **Gerando ranking...**", parse_mode='Markdown')
        
        try:
            # Busca ranking normal
            ranking = self.sniper.get_full_ranking()
            
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
            # Status do SNIPER
            sniper_status = "🟢 ATIVO" if hasattr(self.sniper, 'assets') else "❌ INATIVO"
            
            # Status do Pai do Trade
            pai_status = self.pai_do_trade.get_status()
            
            # Sanitiza dados para evitar problemas de parse
            assistant_id_safe = self._sanitize_text(pai_status['assistant_id'])[:10] if pai_status['assistant_id'] else 'N/A'
            thread_id_safe = self._sanitize_text(pai_status['thread_id'])[:10] if pai_status['thread_id'] else 'N/A'
            
            message = f"""🟢 **SISTEMA SNIPER NEØ + PAI DO TRADE - ONLINE**

**Configurações:**
- Threshold: {self.threshold}/10
- IA habilitada: {'✅' if self.ai_enabled else '❌'}
- Ativos monitorados: {len(self.sniper.assets) if hasattr(self.sniper, 'assets') else 0}

**Status Pai do Trade:**
- Assistant: {'✅' if pai_status['enabled'] else '❌'}
- Assistant ID: {assistant_id_safe}...
- Thread ID: {thread_id_safe}...
- Cache: {pai_status['cache_size']} análises

**Última atualização:** {datetime.now().strftime('%H:%M:%S')}"""
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            error_message = f"❌ **Erro no status:** {str(e)}"
            await update.message.reply_text(error_message, parse_mode='Markdown')
    
    async def toggle_ai_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /toggle_ai - Liga/desliga IA"""
        self.ai_enabled = self.pai_do_trade.toggle_assistant()
        
        status = "✅ HABILITADA" if self.ai_enabled else "❌ DESABILITADA"
        message = f"🤖 **PAI DO TRADE {status}**\n\nSistema agora {'usa' if self.ai_enabled else 'não usa'} análise avançada de IA."
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def threshold_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /threshold - Define threshold"""
        if not context.args:
            await update.message.reply_text(f"❌ Uso: /threshold 7.0\n\nThreshold atual: {self.threshold}")
            return
        
        try:
            new_threshold = float(context.args[0])
            if 0 <= new_threshold <= 10:
                self.threshold = new_threshold
                self.sniper.threshold = new_threshold  # Sincroniza com sistema principal
                message = f"✅ Threshold definido para {new_threshold}/10\n\nSistema atualizado!"
            else:
                message = "❌ Threshold deve estar entre 0 e 10"
        except ValueError:
            message = "❌ Threshold deve ser um número"
        
        await update.message.reply_text(message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /help - Ajuda completa"""
        help_message = """
🤖 **SNIPER NEØ + PAI DO TRADE - AJUDA COMPLETA**

**Comandos principais:**
/analyze - Análise completa com Pai do Trade OpenAI
/analyze_ai BTCUSDT,ETHUSDT - Análise específica com IA
/ranking - TOP 6 ativos ranqueados
/status - Status do sistema e IA

**Comandos de configuração:**
/threshold 7.0 - Define threshold (0-10)
/toggle_ai - Liga/desliga Pai do Trade
/help - Esta ajuda
/start - Reinicia o bot

**Novo:** Pai do Trade OpenAI para análise avançada!
        """
        await update.message.reply_text(help_message, parse_mode='Markdown')
    
    def _get_top_6_assets(self) -> List[Dict]:
        """Busca TOP 6 ativos para análise"""
        try:
            ranking = self.sniper.get_full_ranking()
            if ranking:
                return ranking[:6]
            return []
        except Exception:
            return []
    
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
        application.add_handler(CommandHandler("toggle_ai", self.toggle_ai_command))
        application.add_handler(CommandHandler("threshold", self.threshold_command))
        application.add_handler(CommandHandler("help", self.help_command))
        
        # Handler de erros
        application.add_error_handler(self.error_handler)
        
        # Inicia o bot
        print("🤖 SNIPER NEØ + PAI DO TRADE Bot iniciado!")
        print("Pressione Ctrl+C para parar")
        
        try:
            application.run_polling()
        except KeyboardInterrupt:
            print("\n🛑 Bot parado pelo usuário")

# Exemplo de uso
def main():
    """Função principal"""
    # Configuração
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    
    if not TELEGRAM_TOKEN:
        print("❌ TELEGRAM_TOKEN não encontrada no .env")
        return
    
    # Cria e executa bot
    bot = SniperEnhancedTelegramBot(TELEGRAM_TOKEN)
    bot.run_bot()

if __name__ == "__main__":
    main()
