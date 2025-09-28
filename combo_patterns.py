#!/usr/bin/env python3
"""
🥷 COMBO PATTERNS NEØ - LÓGICAS DE CONFLUÊNCIA
Sistema de correlação entre indicadores para setups mais confiáveis
"""

class ComboPatterns:
    def __init__(self):
        self.patterns = {
            "GOLDEN_CROSS_LONG": {
                "description": "MACD bullish + RSI < 30 + Volume high",
                "multiplier": 2.0,
                "conditions": ["macd_bullish", "rsi_oversold", "volume_high"]
            },
            "GOLDEN_CROSS_SHORT": {
                "description": "MACD bearish + RSI > 70 + Volume high", 
                "multiplier": 2.0,
                "conditions": ["macd_bearish", "rsi_overbought", "volume_high"]
            },
            "FUNDING_SQUEEZE_LONG": {
                "description": "Funding negativo + RSI < 35 + OI up",
                "multiplier": 1.8,
                "conditions": ["funding_negative", "rsi_oversold", "oi_up"]
            },
            "FUNDING_SQUEEZE_SHORT": {
                "description": "Funding positivo + RSI > 65 + OI down",
                "multiplier": 1.8,
                "conditions": ["funding_positive", "rsi_overbought", "oi_down"]
            },
            "VOLUME_SURGE_LONG": {
                "description": "Volume 2x+ + RSI < 40 + MACD bullish",
                "multiplier": 1.6,
                "conditions": ["volume_surge", "rsi_oversold", "macd_bullish"]
            },
            "VOLUME_SURGE_SHORT": {
                "description": "Volume 2x+ + RSI > 60 + MACD bearish",
                "multiplier": 1.6,
                "conditions": ["volume_surge", "rsi_overbought", "macd_bearish"]
            },
            "EXTREME_REVERSAL_LONG": {
                "description": "RSI < 25 + MACD bullish + Funding < -0.001",
                "multiplier": 2.5,
                "conditions": ["rsi_extreme_oversold", "macd_bullish", "funding_very_negative"]
            },
            "EXTREME_REVERSAL_SHORT": {
                "description": "RSI > 75 + MACD bearish + Funding > 0.001",
                "multiplier": 2.5,
                "conditions": ["rsi_extreme_overbought", "macd_bearish", "funding_very_positive"]
            },
            "MOMENTUM_BREAKOUT_LONG": {
                "description": "Volume high + OI up + RSI < 45 + MACD bullish",
                "multiplier": 1.4,
                "conditions": ["volume_high", "oi_up", "rsi_oversold", "macd_bullish"]
            },
            "MOMENTUM_BREAKOUT_SHORT": {
                "description": "Volume high + OI down + RSI > 55 + MACD bearish",
                "multiplier": 1.4,
                "conditions": ["volume_high", "oi_down", "rsi_overbought", "macd_bearish"]
            }
        }
    
    def check_conditions(self, data):
        """Verifica condições dos indicadores"""
        conditions = {}
        
        # RSI conditions
        rsi = data.get("rsi", 50)
        conditions["rsi_oversold"] = rsi < 35
        conditions["rsi_overbought"] = rsi > 70
        conditions["rsi_extreme_oversold"] = rsi < 25
        conditions["rsi_extreme_overbought"] = rsi > 75
        
        # MACD conditions
        macd = data.get("macd", "neutral")
        conditions["macd_bullish"] = macd == "bullish"
        conditions["macd_bearish"] = macd == "bearish"
        
        # Volume conditions
        volume_ratio = data.get("volume_ratio", 1)
        conditions["volume_high"] = volume_ratio > 1.5
        conditions["volume_surge"] = volume_ratio > 2.0
        
        # Funding conditions
        funding = data.get("funding", 0)
        conditions["funding_negative"] = funding < 0
        conditions["funding_positive"] = funding > 0
        conditions["funding_very_negative"] = funding < -0.001
        conditions["funding_very_positive"] = funding > 0.001
        
        # Open Interest conditions
        oi = data.get("oi", "neutral")
        conditions["oi_up"] = oi == "up"
        conditions["oi_down"] = oi == "down"
        
        return conditions
    
    def find_combo_patterns(self, data, direction="LONG"):
        """Encontra padrões de confluência"""
        conditions = self.check_conditions(data)
        matched_patterns = []
        
        for pattern_name, pattern_data in self.patterns.items():
            # Filtra por direção
            if direction == "LONG" and "SHORT" in pattern_name:
                continue
            if direction == "SHORT" and "LONG" in pattern_name:
                continue
            
            # Verifica se todas as condições do padrão são atendidas
            pattern_conditions = pattern_data["conditions"]
            if all(conditions.get(cond, False) for cond in pattern_conditions):
                matched_patterns.append({
                    "name": pattern_name,
                    "description": pattern_data["description"],
                    "multiplier": pattern_data["multiplier"],
                    "conditions_met": pattern_conditions
                })
        
        return matched_patterns
    
    def calculate_combo_bonus(self, data, direction="LONG"):
        """Calcula bônus de combo patterns"""
        patterns = self.find_combo_patterns(data, direction)
        
        if not patterns:
            return 0, []
        
        # Pega o padrão com maior multiplicador
        best_pattern = max(patterns, key=lambda x: x["multiplier"])
        
        # Calcula bônus baseado no multiplicador
        bonus = best_pattern["multiplier"] - 1.0  # Ex: 2.0 vira 1.0 de bônus
        
        return bonus, patterns
    
    def get_combo_description(self, patterns):
        """Gera descrição dos combos encontrados"""
        if not patterns:
            return ""
        
        descriptions = []
        for pattern in patterns:
            descriptions.append(f"🔥 {pattern['name']}: {pattern['description']}")
        
        return "\n".join(descriptions)

def main():
    """Teste dos combo patterns"""
    combo = ComboPatterns()
    
    # Dados de exemplo
    test_data = {
        "rsi": 28,
        "macd": "bullish", 
        "volume_ratio": 2.1,
        "funding": -0.0005,
        "oi": "up"
    }
    
    # Testa LONG
    patterns_long = combo.find_combo_patterns(test_data, "LONG")
    bonus_long, _ = combo.calculate_combo_bonus(test_data, "LONG")
    
    print("🔍 COMBO PATTERNS - TESTE")
    print("=" * 50)
    print(f"📊 Dados: RSI {test_data['rsi']}, MACD {test_data['macd']}, Volume {test_data['volume_ratio']}x")
    print(f"🎯 LONG Patterns: {len(patterns_long)}")
    print(f"💰 Bônus: +{bonus_long:.1f}")
    
    if patterns_long:
        print("\n🔥 COMBOS ENCONTRADOS:")
        for pattern in patterns_long:
            print(f"   {pattern['name']}: {pattern['description']}")

if __name__ == "__main__":
    main()
