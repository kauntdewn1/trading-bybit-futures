#!/usr/bin/env python3
"""
OpenAI Assistant Integration - SNIPER NEØ
Node de análise avançada para interpretação de gráficos e validação de sinais
"""

import openai
import json
import base64
import io
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import requests
from PIL import Image

class OpenAIAssistantNode:
    def __init__(self, api_key: str, assistant_id: str):
        """
        Inicializa o node de análise OpenAI Assistant
        
        Args:
            api_key: Chave da API OpenAI
            assistant_id: ID do assistant criado no playground
        """
        self.client = openai.OpenAI(api_key=api_key)
        self.assistant_id = assistant_id
        self.thread_id = None
        
    def create_thread(self) -> str:
        """Cria um novo thread para conversação"""
        thread = self.client.beta.threads.create()
        self.thread_id = thread.id
        return self.thread_id
    
    def analyze_chart_data(self, symbol: str, df: pd.DataFrame, 
                          indicators: Dict, score: float) -> Dict:
        """
        Analisa dados do gráfico usando OpenAI Assistant
        
        Args:
            symbol: Símbolo do ativo (ex: BTCUSDT)
            df: DataFrame com dados OHLCV
            indicators: Dicionário com indicadores calculados
            score: Score atual do sistema
            
        Returns:
            Dict com análise do assistant
        """
        try:
            # Cria thread se não existir
            if not self.thread_id:
                self.create_thread()
            
            # Prepara dados para análise
            analysis_data = self._prepare_analysis_data(symbol, df, indicators, score)
            
            # Envia mensagem para o assistant
            message = self.client.beta.threads.messages.create(
                thread_id=self.thread_id,
                role="user",
                content=analysis_data
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
                return self._parse_response(response)
            else:
                return {"error": f"Assistant failed: {run.status}"}
                
        except Exception as e:
            return {"error": f"OpenAI Assistant error: {str(e)}"}
    
    def _prepare_analysis_data(self, symbol: str, df: pd.DataFrame, 
                              indicators: Dict, score: float) -> str:
        """Prepara dados para análise do assistant"""
        
        # Dados básicos
        current_price = df['close'].iloc[-1]
        price_change_24h = ((current_price - df['close'].iloc[-24]) / df['close'].iloc[-24]) * 100 if len(df) >= 24 else 0
        
        # Indicadores técnicos
        rsi = indicators.get('rsi', 0)
        macd_signal = indicators.get('macd_signal', 'neutral')
        volume_ratio = indicators.get('volume_ratio', 1.0)
        funding_rate = indicators.get('funding_rate', 0)
        oi_trend = indicators.get('oi_trend', 'neutral')
        
        # Dados de volatilidade
        volatility = df['close'].pct_change().std() * 100
        
        # Cria prompt estruturado
        prompt = f"""
        ANÁLISE TÉCNICA AVANÇADA - {symbol}
        
        DADOS ATUAIS:
        - Preço: ${current_price:,.2f}
        - Variação 24h: {price_change_24h:+.2f}%
        - Volatilidade: {volatility:.2f}%
        
        INDICADORES TÉCNICOS:
        - RSI: {rsi:.2f}
        - MACD: {macd_signal}
        - Volume Ratio: {volume_ratio:.2f}x
        - Funding Rate: {funding_rate:.6f}
        - OI Trend: {oi_trend}
        
        SCORE SISTEMA: {score:.2f}/10
        
        DADOS HISTÓRICOS (Últimas 20 velas):
        {df.tail(20)[['open', 'high', 'low', 'close', 'volume']].to_string()}
        
        SOLICITAÇÃO:
        Analise estes dados e forneça:
        1. Análise técnica detalhada
        2. Confirmação ou refutação do sinal
        3. Nível de confiança (1-10)
        4. Recomendações de entrada/saída
        5. Stop-loss e take-profit sugeridos
        6. Riscos identificados
        
        Formato de resposta em JSON:
        {{
            "analysis": "Análise técnica detalhada",
            "signal_confirmation": true/false,
            "confidence_level": 1-10,
            "entry_recommendation": "LONG/SHORT/HOLD",
            "stop_loss": "Preço sugerido",
            "take_profit": "Preço sugerido",
            "risks": ["Lista de riscos"],
            "reasoning": "Explicação da decisão"
        }}
        """
        
        return prompt
    
    def _parse_response(self, response: str) -> Dict:
        """Parseia resposta do assistant"""
        try:
            # Tenta extrair JSON da resposta
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            else:
                json_str = response
            
            return json.loads(json_str)
        except:
            # Se não conseguir parsear JSON, retorna resposta raw
            return {
                "raw_response": response,
                "analysis": "Resposta não estruturada",
                "signal_confirmation": False,
                "confidence_level": 5
            }
    
    def generate_enhanced_alert(self, symbol: str, original_alert: Dict, 
                               ai_analysis: Dict) -> str:
        """Gera alerta aprimorado com análise do assistant"""
        
        # Emoji baseado na confiança
        confidence_emoji = "🔥" if ai_analysis.get('confidence_level', 5) >= 8 else "⚠️"
        
        # Status do sinal
        signal_status = "✅ CONFIRMADO" if ai_analysis.get('signal_confirmation', False) else "❌ REFUTADO"
        
        # Recomendação
        recommendation = ai_analysis.get('entry_recommendation', 'HOLD')
        rec_emoji = "🟢" if recommendation == "LONG" else "🔴" if recommendation == "SHORT" else "🟡"
        
        # Constrói alerta aprimorado
        enhanced_alert = f"""
{confidence_emoji} **SNIPER NEØ + AI VALIDATION** {confidence_emoji}

🎯 **ATIVO:** {symbol}
{rec_emoji} **RECOMENDAÇÃO:** {recommendation}
📊 **STATUS:** {signal_status}
🎯 **CONFIANÇA IA:** {ai_analysis.get('confidence_level', 5)}/10

📈 **ANÁLISE TÉCNICA:**
{ai_analysis.get('analysis', 'Análise não disponível')}

🎯 **NÍVEIS SUGERIDOS:**
- **Stop Loss:** {ai_analysis.get('stop_loss', 'N/A')}
- **Take Profit:** {ai_analysis.get('take_profit', 'N/A')}

⚠️ **RISCOS IDENTIFICADOS:**
{chr(10).join(f"• {risk}" for risk in ai_analysis.get('risks', ['Nenhum risco identificado']))}

🧠 **RAZÃO DA DECISÃO:**
{ai_analysis.get('reasoning', 'Análise não disponível')}

📊 **SCORE ORIGINAL:** {original_alert.get('score', 'N/A')}/10
🤖 **VALIDAÇÃO IA:** {ai_analysis.get('confidence_level', 5)}/10

⏰ **TIMESTAMP:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        return enhanced_alert.strip()

# Exemplo de uso
def test_openai_integration():
    """Testa integração com OpenAI Assistant"""
    
    # Configuração (substitua pelos seus valores)
    API_KEY = "sua_api_key_openai"
    ASSISTANT_ID = "seu_assistant_id"
    
    # Cria instância
    ai_node = OpenAIAssistantNode(API_KEY, ASSISTANT_ID)
    
    # Dados de teste
    test_df = pd.DataFrame({
        'open': [100, 101, 102, 103, 104],
        'high': [105, 106, 107, 108, 109],
        'low': [99, 100, 101, 102, 103],
        'close': [101, 102, 103, 104, 105],
        'volume': [1000, 1100, 1200, 1300, 1400]
    })
    
    test_indicators = {
        'rsi': 35.5,
        'macd_signal': 'bullish',
        'volume_ratio': 1.8,
        'funding_rate': -0.0001,
        'oi_trend': 'up'
    }
    
    # Testa análise
    result = ai_node.analyze_chart_data("BTCUSDT", test_df, test_indicators, 7.5)
    print("Análise IA:", json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test_openai_integration()
