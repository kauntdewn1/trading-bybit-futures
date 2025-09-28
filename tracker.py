#!/usr/bin/env python3
"""
🥷 TRACKER NEØ - SISTEMA DE AUTO-LEARNING
Registra acertos e flops para otimização automática
"""

import json
import pandas as pd
from datetime import datetime, timedelta
import os

class Tracker:
    def __init__(self, data_file="tracker_data.json"):
        self.data_file = data_file
        self.data = self.load_data()
    
    def load_data(self):
        """Carrega dados do tracker"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "alerts": [],
            "performance": {},
            "patterns": {},
            "assets": {}
        }
    
    def save_data(self):
        """Salva dados do tracker"""
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
    
    def record_alert(self, symbol, direction, score, data, combo_patterns=None):
        """Registra um alerta para tracking"""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "direction": direction,
            "score": score,
            "data": data,
            "combo_patterns": combo_patterns or [],
            "status": "PENDING",  # PENDING, HIT, MISS, STOPPED
            "result": None,  # Será preenchido depois
            "profit_loss": None,
            "max_favorable": None,
            "max_adverse": None
        }
        
        self.data["alerts"].append(alert)
        self.save_data()
        
        return len(self.data["alerts"]) - 1  # Retorna ID do alerta
    
    def update_alert_result(self, alert_id, status, profit_loss=None, max_favorable=None, max_adverse=None):
        """Atualiza resultado de um alerta"""
        if 0 <= alert_id < len(self.data["alerts"]):
            alert = self.data["alerts"][alert_id]
            alert["status"] = status
            alert["result"] = status
            alert["profit_loss"] = profit_loss
            alert["max_favorable"] = max_favorable
            alert["max_adverse"] = max_adverse
            
            # Atualiza estatísticas
            self.update_performance_stats(alert)
            self.save_data()
    
    def update_performance_stats(self, alert):
        """Atualiza estatísticas de performance"""
        symbol = alert["symbol"]
        direction = alert["direction"]
        score = alert["score"]
        status = alert["status"]
        combo_patterns = alert.get("combo_patterns", [])
        
        # Estatísticas por ativo
        if symbol not in self.data["assets"]:
            self.data["assets"][symbol] = {
                "total_alerts": 0,
                "hits": 0,
                "misses": 0,
                "stops": 0,
                "avg_score": 0,
                "hit_rate": 0,
                "total_pnl": 0
            }
        
        asset_stats = self.data["assets"][symbol]
        asset_stats["total_alerts"] += 1
        
        if status == "HIT":
            asset_stats["hits"] += 1
        elif status == "MISS":
            asset_stats["misses"] += 1
        elif status == "STOPPED":
            asset_stats["stops"] += 1
        
        # Atualiza hit rate
        total_completed = asset_stats["hits"] + asset_stats["misses"] + asset_stats["stops"]
        if total_completed > 0:
            asset_stats["hit_rate"] = asset_stats["hits"] / total_completed
        
        # Atualiza PnL
        if alert.get("profit_loss"):
            asset_stats["total_pnl"] += alert["profit_loss"]
        
        # Estatísticas por score
        score_range = self.get_score_range(score)
        if score_range not in self.data["performance"]:
            self.data["performance"][score_range] = {
                "total": 0,
                "hits": 0,
                "hit_rate": 0
            }
        
        perf_stats = self.data["performance"][score_range]
        perf_stats["total"] += 1
        if status == "HIT":
            perf_stats["hits"] += 1
        perf_stats["hit_rate"] = perf_stats["hits"] / perf_stats["total"] if perf_stats["total"] > 0 else 0
        
        # Estatísticas por combo patterns
        for pattern in combo_patterns:
            if pattern not in self.data["patterns"]:
                self.data["patterns"][pattern] = {
                    "total": 0,
                    "hits": 0,
                    "hit_rate": 0
                }
            
            pattern_stats = self.data["patterns"][pattern]
            pattern_stats["total"] += 1
            if status == "HIT":
                pattern_stats["hits"] += 1
            pattern_stats["hit_rate"] = pattern_stats["hits"] / pattern_stats["total"] if pattern_stats["total"] > 0 else 0
    
    def get_score_range(self, score):
        """Categoriza score em ranges"""
        if score >= 8:
            return "8-10"
        elif score >= 6:
            return "6-7.9"
        elif score >= 4:
            return "4-5.9"
        else:
            return "0-3.9"
    
    def get_asset_preference(self, symbol):
        """Retorna preferência de um ativo baseada no histórico"""
        if symbol not in self.data["assets"]:
            return 1.0  # Neutro se não tem histórico
        
        asset_stats = self.data["assets"][symbol]
        
        # Fator baseado no hit rate
        hit_rate = asset_stats["hit_rate"]
        if hit_rate > 0.7:
            return 1.3  # Prefere ativos com hit rate alto
        elif hit_rate > 0.5:
            return 1.1
        elif hit_rate < 0.3:
            return 0.7  # Evita ativos com hit rate baixo
        else:
            return 1.0
    
    def get_pattern_preference(self, combo_patterns):
        """Retorna preferência de combo patterns baseada no histórico"""
        if not combo_patterns:
            return 1.0
        
        total_preference = 0
        valid_patterns = 0
        
        for pattern in combo_patterns:
            if pattern in self.data["patterns"]:
                pattern_stats = self.data["patterns"][pattern]
                hit_rate = pattern_stats["hit_rate"]
                
                if hit_rate > 0.7:
                    total_preference += 1.3
                elif hit_rate > 0.5:
                    total_preference += 1.1
                elif hit_rate < 0.3:
                    total_preference += 0.7
                else:
                    total_preference += 1.0
                
                valid_patterns += 1
        
        return total_preference / valid_patterns if valid_patterns > 0 else 1.0
    
    def get_performance_summary(self):
        """Retorna resumo de performance"""
        total_alerts = len(self.data["alerts"])
        completed_alerts = [a for a in self.data["alerts"] if a["status"] != "PENDING"]
        
        if not completed_alerts:
            return {
                "total_alerts": total_alerts,
                "completed": 0,
                "hit_rate": 0,
                "best_asset": None,
                "worst_asset": None,
                "best_pattern": None,
                "worst_pattern": None
            }
        
        # Hit rate geral
        hits = len([a for a in completed_alerts if a["status"] == "HIT"])
        hit_rate = hits / len(completed_alerts)
        
        # Melhor/pior ativo
        asset_performance = []
        for symbol, stats in self.data["assets"].items():
            if stats["total_alerts"] >= 3:  # Mínimo 3 alertas
                asset_performance.append({
                    "symbol": symbol,
                    "hit_rate": stats["hit_rate"],
                    "total_pnl": stats["total_pnl"]
                })
        
        best_asset = max(asset_performance, key=lambda x: x["hit_rate"]) if asset_performance else None
        worst_asset = min(asset_performance, key=lambda x: x["hit_rate"]) if asset_performance else None
        
        # Melhor/pior pattern
        pattern_performance = []
        for pattern, stats in self.data["patterns"].items():
            if stats["total"] >= 3:  # Mínimo 3 ocorrências
                pattern_performance.append({
                    "pattern": pattern,
                    "hit_rate": stats["hit_rate"]
                })
        
        best_pattern = max(pattern_performance, key=lambda x: x["hit_rate"]) if pattern_performance else None
        worst_pattern = min(pattern_performance, key=lambda x: x["hit_rate"]) if pattern_performance else None
        
        return {
            "total_alerts": total_alerts,
            "completed": len(completed_alerts),
            "hit_rate": hit_rate,
            "best_asset": best_asset,
            "worst_asset": worst_asset,
            "best_pattern": best_pattern,
            "worst_pattern": worst_pattern
        }
    
    def get_recent_alerts(self, days=7):
        """Retorna alertas recentes"""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent = []
        
        for alert in self.data["alerts"]:
            alert_date = datetime.fromisoformat(alert["timestamp"])
            if alert_date >= cutoff_date:
                recent.append(alert)
        
        return recent
    
    def cleanup_old_data(self, days=30):
        """Remove dados antigos para manter performance"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Remove alertas antigos
        self.data["alerts"] = [
            alert for alert in self.data["alerts"]
            if datetime.fromisoformat(alert["timestamp"]) >= cutoff_date
        ]
        
        self.save_data()

def main():
    """Teste do tracker"""
    tracker = Tracker()
    
    # Simula alguns alertas
    alert_id1 = tracker.record_alert("BTCUSDT", "LONG", 8.5, {"rsi": 25}, ["GOLDEN_CROSS_LONG"])
    alert_id2 = tracker.record_alert("ETHUSDT", "SHORT", 7.2, {"rsi": 75}, ["GOLDEN_CROSS_SHORT"])
    
    # Simula resultados
    tracker.update_alert_result(alert_id1, "HIT", profit_loss=150.0)
    tracker.update_alert_result(alert_id2, "MISS", profit_loss=-50.0)
    
    # Mostra resumo
    summary = tracker.get_performance_summary()
    print("📊 TRACKER NEØ - RESUMO DE PERFORMANCE")
    print("=" * 50)
    print(f"Total Alertas: {summary['total_alerts']}")
    print(f"Completados: {summary['completed']}")
    print(f"Hit Rate: {summary['hit_rate']:.1%}")
    
    if summary['best_asset']:
        print(f"Melhor Ativo: {summary['best_asset']['symbol']} ({summary['best_asset']['hit_rate']:.1%})")
    
    if summary['best_pattern']:
        print(f"Melhor Pattern: {summary['best_pattern']['pattern']} ({summary['best_pattern']['hit_rate']:.1%})")

if __name__ == "__main__":
    main()
