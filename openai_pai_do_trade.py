#!/usr/bin/env python3
"""
OpenAI Pai do Trade Integration - SNIPER NEØ
Integração personalizada que ativa o Assistant no final da análise do Telegram
"""

import openai
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv

class PaiDoTradeOpenAI:
    """
    Integração personalizada com OpenAI Assistant
    Ativa apenas no final da análise do Telegram
    """
    
    def __init__(self):
        """Inicializa integração com OpenAI"""
        load_dotenv()
        
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_SECRET_KEY"))
        self.assistant_id = os.getenv("OPENAI_ASSISTANT_ID")
        self.thread_id = None
        
        # Configurações
        self.enabled = True
        self.analysis_cache = {}
        
    def create_thread(self) -> str:
        """Cria novo thread para conversação"""
        thread = self.client.beta.threads.create()
        self.thread_id = thread.id
        return self.thread_id
    
    def analyze_top_6_assets(self, top_6_data: List[Dict]) -> Dict:
        """
        Analisa TOP 6 ativos e retorna sugestões avançadas
        
        Args:
            top_6_data: Lista com dados dos TOP 6 ativos
            
        Returns:
            Dict com análise e sugestões do Assistant
        """
        if not self.enabled or not top_6_data:
            return {"error": "Assistant desabilitado ou dados vazios"}
        
        try:
            # Cria thread se não existir
            if not self.thread_id:
                self.create_thread()
            
            # Prepara dados para análise
            analysis_prompt = self._prepare_top_6_analysis(top_6_data)
            
            # Envia mensagem para o assistant
            message = self.client.beta.threads.messages.create(
                thread_id=self.thread_id,
                role="user",
                content=analysis_prompt
            )
            
            # Executa o assistant
            run = self.client.beta.threads.runs.create(
                thread_id=self.thread_id,
                assistant_id=self.assistant_id
            )
            
            # Aguarda resposta
            while run.status in ['queued', 'in_progress', 'cancelling']:
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=self.thread_id,
                    run_id=run.id
                )
            
            if run.status == 'completed':
                # Recupera resposta
                messages = self.client.beta.threads.messages.list(
                    thread_id=self.thread_id
                )
                
                response = messages.data[0].content[0].text.value
                return self._parse_assistant_response(response)
            else:
                return {"error": f"Assistant failed: {run.status}"}
                
        except Exception as e:
            return {"error": f"Erro OpenAI Assistant: {str(e)}"}
    
    def _prepare_top_6_analysis(self, top_6_data: List[Dict]) -> str:
        """Prepara prompt para análise dos TOP 6 ativos"""
        
        # Formata dados dos ativos
        assets_info = []
        for i, asset in enumerate(top_6_data, 1):
            asset_info = f"""
**{i}º {asset.get('symbol', 'N/A')}**
- Score: {asset.get('score', 0):.1f}/10
- Direção: {asset.get('direction', 'N/A')}
- RSI: {asset.get('rsi', 0):.1f}
- MACD: {asset.get('macd', 'N/A')}
- Volume: {asset.get('volume_status', 'N/A')}
- Funding: {asset.get('funding_rate', 0):.6f}
- OI: {asset.get('oi_trend', 'N/A')}
- Preço: ${asset.get('price', 0):,.2f}
"""
            assets_info.append(asset_info)
        
        # Cria prompt estruturado
        prompt = f"""
**ANÁLISE AVANÇADA - TOP 6 ATIVOS SNIPER NEØ**

Dados dos ativos ranqueados:

{chr(10).join(assets_info)}

**SOLICITAÇÃO:**
Analise estes 6 ativos e forneça:

1. **RANKING FINAL** - Reordene por melhor oportunidade
2. **ANÁLISE TÉCNICA** - Padrões identificados em cada ativo
3. **SUGESTÕES DE ENTRADA** - Long/Short com justificativa
4. **NÍVEIS DE PREÇO** - Stop-loss e take-profit para cada ativo
5. **GESTÃO DE RISCO** - Posicionamento e alocação de capital
6. **CONFLUÊNCIAS** - Ativos que se complementam
7. **ALERTAS** - Riscos específicos identificados

**FORMATO DE RESPOSTA:**
Responda em JSON estruturado:
{{
    "final_ranking": [
        {{
            "position": 1,
            "symbol": "BTCUSDT",
            "direction": "LONG",
            "confidence": 8.5,
            "entry_price": "112,000",
            "stop_loss": "108,500",
            "take_profit": "115,000",
            "reasoning": "Explicação técnica",
            "risk_level": "MEDIUM"
        }}
    ],
    "market_analysis": "Análise geral do mercado",
    "risk_warnings": ["Lista de riscos identificados"],
    "capital_allocation": {{
        "total_capital": 100,
        "allocations": [
            {{"symbol": "BTCUSDT", "percentage": 40}},
            {{"symbol": "ETHUSDT", "percentage": 30}}
        ]
    }},
    "confluences": ["Padrões que se complementam"],
    "timestamp": "2024-01-15T14:30:00Z"
}}

**REGRAS:**
- Seja objetivo e técnico
- Baseie decisões em dados concretos
- Identifique padrões de confluência
- Considere gestão de risco
- Seja conservador com confiança baixa
- Foque em oportunidades de alta probabilidade
        """
        
        return prompt
    
    def _parse_assistant_response(self, response: str) -> Dict:
        """Parseia resposta do assistant"""
        try:
            # Tenta extrair JSON da resposta
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            else:
                json_str = response
            
            return json.loads(json_str)
        except Exception as e:
            # Se não conseguir parsear JSON, retorna resposta estruturada
            return {
                "raw_response": response,
                "error": f"Erro ao parsear resposta: {str(e)}",
                "final_ranking": [],
                "market_analysis": "Análise não disponível",
                "risk_warnings": ["Erro na análise"],
                "capital_allocation": {"total_capital": 100, "allocations": []},
                "confluences": [],
                "timestamp": datetime.now().isoformat()
            }
    
    def generate_enhanced_telegram_message(self, top_6_data: List[Dict], 
                                         assistant_analysis: Dict) -> str:
        """Gera mensagem aprimorada para Telegram"""
        
        if assistant_analysis.get("error"):
            return self._generate_fallback_message(top_6_data)
        
        # Header
        message = "🤖 **SNIPER NEØ + PAI DO TRADE ANALYSIS** 🤖\n\n"
        
        # Análise de mercado
        market_analysis = assistant_analysis.get("market_analysis", "Análise não disponível")
        message += f"📊 **ANÁLISE DE MERCADO:**\n{market_analysis}\n\n"
        
        # Ranking final
        final_ranking = assistant_analysis.get("final_ranking", [])
        if final_ranking:
            message += "🏆 **RANKING FINAL PAI DO TRADE:**\n\n"
            
            for asset in final_ranking:
                position = asset.get("position", 0)
                symbol = asset.get("symbol", "N/A")
                direction = asset.get("direction", "N/A")
                confidence = asset.get("confidence", 0)
                entry_price = asset.get("entry_price", "N/A")
                stop_loss = asset.get("stop_loss", "N/A")
                take_profit = asset.get("take_profit", "N/A")
                reasoning = asset.get("reasoning", "Sem explicação")
                risk_level = asset.get("risk_level", "UNKNOWN")
                
                # Emoji baseado na direção
                direction_emoji = "🟢" if direction == "LONG" else "🔴" if direction == "SHORT" else "🟡"
                
                # Emoji de risco
                risk_emoji = "🟢" if risk_level == "LOW" else "🟡" if risk_level == "MEDIUM" else "🔴"
                
                message += f"**{position}º {symbol}** {direction_emoji}\n"
                message += f"Direção: {direction} | Confiança: {confidence}/10\n"
                message += f"Entrada: ${entry_price} | SL: ${stop_loss} | TP: ${take_profit}\n"
                message += f"Risco: {risk_level} {risk_emoji}\n"
                message += f"Razão: {reasoning}\n\n"
        
        # Alocação de capital
        capital_allocation = assistant_analysis.get("capital_allocation", {})
        if capital_allocation.get("allocations"):
            message += "💰 **ALOCAÇÃO DE CAPITAL:**\n"
            for allocation in capital_allocation["allocations"]:
                symbol = allocation.get("symbol", "N/A")
                percentage = allocation.get("percentage", 0)
                message += f"• {symbol}: {percentage}%\n"
            message += "\n"
        
        # Confluências
        confluences = assistant_analysis.get("confluences", [])
        if confluences:
            message += "🔗 **CONFLUÊNCIAS IDENTIFICADAS:**\n"
            for confluence in confluences:
                message += f"• {confluence}\n"
            message += "\n"
        
        # Alertas de risco
        risk_warnings = assistant_analysis.get("risk_warnings", [])
        if risk_warnings:
            message += "⚠️ **ALERTAS DE RISCO:**\n"
            for warning in risk_warnings:
                message += f"• {warning}\n"
            message += "\n"
        
        # Timestamp
        timestamp = assistant_analysis.get("timestamp", datetime.now().isoformat())
        message += f"⏰ **Análise realizada em:** {timestamp}\n"
        message += "🤖 **Powered by Pai do Trade OpenAI Assistant**"
        
        return message
    
    def _generate_fallback_message(self, top_6_data: List[Dict]) -> str:
        """Gera mensagem de fallback se Assistant falhar"""
        
        message = "🤖 **SNIPER NEØ - TOP 6 ATIVOS**\n\n"
        message += "⚠️ *Análise avançada temporariamente indisponível*\n\n"
        
        for i, asset in enumerate(top_6_data, 1):
            symbol = asset.get('symbol', 'N/A')
            direction = asset.get('direction', 'N/A')
            score = asset.get('score', 0)
            
            direction_emoji = "🟢" if direction == "LONG" else "🔴" if direction == "SHORT" else "🟡"
            
            message += f"**{i}º {symbol}** {direction_emoji}\n"
            message += f"Score: {score:.1f}/10 | Direção: {direction}\n\n"
        
        return message
    
    def toggle_assistant(self, enabled: bool = None) -> bool:
        """Liga/desliga o Assistant"""
        if enabled is None:
            self.enabled = not self.enabled
        else:
            self.enabled = enabled
        
        return self.enabled
    
    def get_status(self) -> Dict:
        """Retorna status do Assistant"""
        return {
            "enabled": self.enabled,
            "assistant_id": self.assistant_id,
            "thread_id": self.thread_id,
            "cache_size": len(self.analysis_cache)
        }

# Exemplo de uso
def test_pai_do_trade():
    """Testa integração Pai do Trade"""
    
    # Dados de exemplo
    top_6_data = [
        {
            "symbol": "BTCUSDT",
            "score": 8.5,
            "direction": "LONG",
            "rsi": 28.5,
            "macd": "bullish",
            "volume_status": "high",
            "funding_rate": -0.0001,
            "oi_trend": "up",
            "price": 112000
        },
        {
            "symbol": "ETHUSDT",
            "score": 7.8,
            "direction": "SHORT",
            "rsi": 72.3,
            "macd": "bearish",
            "volume_status": "high",
            "funding_rate": 0.0002,
            "oi_trend": "down",
            "price": 3500
        }
    ]
    
    # Testa integração
    pai_do_trade = PaiDoTradeOpenAI()
    
    print("🧪 Testando Pai do Trade OpenAI...")
    analysis = pai_do_trade.analyze_top_6_assets(top_6_data)
    
    if analysis.get("error"):
        print(f"❌ Erro: {analysis['error']}")
    else:
        print("✅ Análise concluída!")
        print(f"Ranking final: {len(analysis.get('final_ranking', []))} ativos")
        
        # Gera mensagem para Telegram
        message = pai_do_trade.generate_enhanced_telegram_message(top_6_data, analysis)
        print("\n📱 MENSAGEM TELEGRAM:")
        print("=" * 50)
        print(message)

if __name__ == "__main__":
    test_pai_do_trade()
