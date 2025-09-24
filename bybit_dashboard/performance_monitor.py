#!/usr/bin/env python3
"""
📊 PERFORMANCE MONITOR NEØ - MONITORAMENTO EM TEMPO REAL
Sistema de métricas e monitoramento de performance do SNIPER NEØ
"""

import time
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import deque, defaultdict
import psutil
import os

@dataclass
class SystemMetrics:
    """Métricas do sistema"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_usage_percent: float
    network_io_bytes: int
    active_threads: int
    python_memory_mb: float

@dataclass
class TradingMetrics:
    """Métricas de trading"""
    timestamp: str
    total_assets: int
    processed_assets: int
    failed_assets: int
    processing_time: float
    throughput: float
    cache_hit_rate: float
    api_requests: int
    rate_limit_hits: int
    avg_response_time: float
    success_rate: float

@dataclass
class PerformanceAlert:
    """Alerta de performance"""
    timestamp: str
    alert_type: str
    severity: str
    message: str
    threshold: float
    current_value: float
    recommendation: str

class PerformanceMonitor:
    """
    Monitor de performance em tempo real
    """
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.system_metrics = deque(maxlen=max_history)
        self.trading_metrics = deque(maxlen=max_history)
        self.alerts = deque(maxlen=100)
        self.performance_history = defaultdict(list)
        
        # Thresholds de alerta
        self.thresholds = {
            "cpu_percent": 80.0,
            "memory_percent": 85.0,
            "processing_time": 30.0,  # segundos
            "throughput": 5.0,  # ativos/s
            "cache_hit_rate": 0.5,  # 50%
            "success_rate": 0.8,  # 80%
            "avg_response_time": 2.0  # segundos
        }
        
        # Contadores
        self.counters = defaultdict(int)
        self.start_time = time.time()
        self.last_cleanup = time.time()
        
        # Thread de monitoramento
        self.monitoring = False
        self.monitor_thread = None
        
    def start_monitoring(self, interval: float = 5.0):
        """Inicia monitoramento em background"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        print(f"📊 Monitor de performance iniciado (intervalo: {interval}s)")
    
    def stop_monitoring(self):
        """Para monitoramento"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        print("📊 Monitor de performance parado")
    
    def _monitoring_loop(self, interval: float):
        """Loop de monitoramento"""
        while self.monitoring:
            try:
                self.collect_system_metrics()
                self.check_alerts()
                self.cleanup_old_data()
                time.sleep(interval)
            except Exception as e:
                print(f"Erro no monitoramento: {e}")
                time.sleep(interval)
    
    def collect_system_metrics(self):
        """Coleta métricas do sistema"""
        try:
            # Métricas do sistema
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            # Métricas do processo Python
            process = psutil.Process(os.getpid())
            python_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            metrics = SystemMetrics(
                timestamp=datetime.now().isoformat(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=memory.used / 1024 / 1024,
                disk_usage_percent=disk.percent,
                network_io_bytes=network.bytes_sent + network.bytes_recv,
                active_threads=threading.active_count(),
                python_memory_mb=python_memory
            )
            
            self.system_metrics.append(metrics)
            self.counters["system_metrics_collected"] += 1
            
        except Exception as e:
            print(f"Erro ao coletar métricas do sistema: {e}")
    
    def record_trading_metrics(self, metrics: TradingMetrics):
        """Registra métricas de trading"""
        self.trading_metrics.append(metrics)
        self.counters["trading_metrics_recorded"] += 1
        
        # Atualiza histórico de performance
        self.performance_history["throughput"].append(metrics.throughput)
        self.performance_history["processing_time"].append(metrics.processing_time)
        self.performance_history["success_rate"].append(metrics.success_rate)
        self.performance_history["cache_hit_rate"].append(metrics.cache_hit_rate)
    
    def check_alerts(self):
        """Verifica alertas de performance"""
        if not self.system_metrics:
            return
        
        latest_system = self.system_metrics[-1]
        latest_trading = self.trading_metrics[-1] if self.trading_metrics else None
        
        # Verifica alertas do sistema
        self._check_system_alerts(latest_system)
        
        # Verifica alertas de trading
        if latest_trading:
            self._check_trading_alerts(latest_trading)
    
    def _check_system_alerts(self, metrics: SystemMetrics):
        """Verifica alertas do sistema"""
        # CPU alto
        if metrics.cpu_percent > self.thresholds["cpu_percent"]:
            self._create_alert(
                "cpu_high",
                "warning",
                f"CPU alto: {metrics.cpu_percent:.1f}%",
                self.thresholds["cpu_percent"],
                metrics.cpu_percent,
                "Considere reduzir carga de processamento"
            )
        
        # Memória alta
        if metrics.memory_percent > self.thresholds["memory_percent"]:
            self._create_alert(
                "memory_high",
                "critical",
                f"Memória alta: {metrics.memory_percent:.1f}%",
                self.thresholds["memory_percent"],
                metrics.memory_percent,
                "Considere reiniciar o sistema ou otimizar uso de memória"
            )
        
        # Threads excessivas
        if metrics.active_threads > 50:
            self._create_alert(
                "threads_high",
                "warning",
                f"Muitas threads ativas: {metrics.active_threads}",
                50,
                metrics.active_threads,
                "Verifique se há vazamentos de threads"
            )
    
    def _check_trading_alerts(self, metrics: TradingMetrics):
        """Verifica alertas de trading"""
        # Tempo de processamento alto
        if metrics.processing_time > self.thresholds["processing_time"]:
            self._create_alert(
                "processing_slow",
                "warning",
                f"Processamento lento: {metrics.processing_time:.1f}s",
                self.thresholds["processing_time"],
                metrics.processing_time,
                "Considere otimizar análise ou reduzir número de ativos"
            )
        
        # Throughput baixo
        if metrics.throughput < self.thresholds["throughput"]:
            self._create_alert(
                "throughput_low",
                "warning",
                f"Throughput baixo: {metrics.throughput:.1f} ativos/s",
                self.thresholds["throughput"],
                metrics.throughput,
                "Considere otimizar processamento paralelo"
            )
        
        # Taxa de sucesso baixa
        if metrics.success_rate < self.thresholds["success_rate"]:
            self._create_alert(
                "success_rate_low",
                "critical",
                f"Taxa de sucesso baixa: {metrics.success_rate:.1%}",
                self.thresholds["success_rate"],
                metrics.success_rate,
                "Verifique conectividade e validação de dados"
            )
        
        # Cache hit rate baixo
        if metrics.cache_hit_rate < self.thresholds["cache_hit_rate"]:
            self._create_alert(
                "cache_hit_rate_low",
                "info",
                f"Cache hit rate baixo: {metrics.cache_hit_rate:.1%}",
                self.thresholds["cache_hit_rate"],
                metrics.cache_hit_rate,
                "Considere ajustar TTL do cache"
            )
    
    def _create_alert(self, alert_type: str, severity: str, message: str, 
                     threshold: float, current_value: float, recommendation: str):
        """Cria alerta de performance"""
        alert = PerformanceAlert(
            timestamp=datetime.now().isoformat(),
            alert_type=alert_type,
            severity=severity,
            message=message,
            threshold=threshold,
            current_value=current_value,
            recommendation=recommendation
        )
        
        self.alerts.append(alert)
        self.counters[f"alerts_{severity}"] += 1
        
        # Log do alerta
        emoji = {"info": "ℹ️", "warning": "⚠️", "critical": "🚨"}.get(severity, "📊")
        print(f"{emoji} ALERTA DE PERFORMANCE: {message}")
    
    def cleanup_old_data(self):
        """Limpa dados antigos"""
        current_time = time.time()
        if current_time - self.last_cleanup < 300:  # 5 minutos
            return
        
        # Remove dados antigos do histórico
        cutoff_time = current_time - 3600  # 1 hora
        
        # Limpa histórico de performance
        for key in list(self.performance_history.keys()):
            if len(self.performance_history[key]) > self.max_history:
                self.performance_history[key] = self.performance_history[key][-self.max_history:]
        
        self.last_cleanup = current_time
    
    def get_performance_summary(self) -> Dict:
        """Retorna resumo de performance"""
        uptime = time.time() - self.start_time
        
        # Métricas atuais
        current_system = self.system_metrics[-1] if self.system_metrics else None
        current_trading = self.trading_metrics[-1] if self.trading_metrics else None
        
        # Métricas médias
        avg_throughput = self._calculate_average("throughput")
        avg_processing_time = self._calculate_average("processing_time")
        avg_success_rate = self._calculate_average("success_rate")
        avg_cache_hit_rate = self._calculate_average("cache_hit_rate")
        
        # Alertas recentes
        recent_alerts = [alert for alert in self.alerts 
                        if datetime.fromisoformat(alert.timestamp) > datetime.now() - timedelta(hours=1)]
        
        return {
            "uptime_seconds": uptime,
            "uptime_formatted": self._format_uptime(uptime),
            "current_system": asdict(current_system) if current_system else None,
            "current_trading": asdict(current_trading) if current_trading else None,
            "averages": {
                "throughput": avg_throughput,
                "processing_time": avg_processing_time,
                "success_rate": avg_success_rate,
                "cache_hit_rate": avg_cache_hit_rate
            },
            "counters": dict(self.counters),
            "recent_alerts": len(recent_alerts),
            "total_alerts": len(self.alerts),
            "monitoring_active": self.monitoring
        }
    
    def _calculate_average(self, metric_name: str) -> float:
        """Calcula média de uma métrica"""
        if metric_name not in self.performance_history:
            return 0.0
        
        values = self.performance_history[metric_name]
        if not values:
            return 0.0
        
        return sum(values) / len(values)
    
    def _format_uptime(self, seconds: float) -> str:
        """Formata tempo de uptime"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def get_performance_report(self) -> str:
        """Gera relatório de performance"""
        summary = self.get_performance_summary()
        
        report = f"""
📊 RELATÓRIO DE PERFORMANCE - SNIPER NEØ
=========================================

⏱️ TEMPO DE ATIVIDADE:
- Uptime: {summary['uptime_formatted']}
- Monitoramento: {'✅ Ativo' if summary['monitoring_active'] else '❌ Inativo'}

💻 MÉTRICAS DO SISTEMA:
"""
        
        if summary['current_system']:
            sys_metrics = summary['current_system']
            report += f"- CPU: {sys_metrics['cpu_percent']:.1f}%\n"
            report += f"- Memória: {sys_metrics['memory_percent']:.1f}% ({sys_metrics['memory_used_mb']:.1f} MB)\n"
            report += f"- Disco: {sys_metrics['disk_usage_percent']:.1f}%\n"
            report += f"- Threads: {sys_metrics['active_threads']}\n"
            report += f"- Memória Python: {sys_metrics['python_memory_mb']:.1f} MB\n"
        
        report += f"""
📈 MÉTRICAS DE TRADING:
- Throughput médio: {summary['averages']['throughput']:.1f} ativos/s
- Tempo médio: {summary['averages']['processing_time']:.2f}s
- Taxa de sucesso: {summary['averages']['success_rate']:.1%}
- Cache hit rate: {summary['averages']['cache_hit_rate']:.1%}

🚨 ALERTAS:
- Total de alertas: {summary['total_alerts']}
- Alertas recentes (1h): {summary['recent_alerts']}

📊 CONTADORES:
- Métricas do sistema: {summary['counters'].get('system_metrics_collected', 0)}
- Métricas de trading: {summary['counters'].get('trading_metrics_recorded', 0)}
- Alertas críticos: {summary['counters'].get('alerts_critical', 0)}
- Alertas de aviso: {summary['counters'].get('alerts_warning', 0)}

🎯 STATUS GERAL:
- Sistema: {'🟢 Saudável' if summary['recent_alerts'] == 0 else '🟡 Atenção' if summary['counters'].get('alerts_critical', 0) == 0 else '🔴 Crítico'}
- Performance: {'🟢 Excelente' if summary['averages']['throughput'] > 20 else '🟡 Boa' if summary['averages']['throughput'] > 10 else '🔴 Baixa'}
"""
        
        return report
    
    def export_metrics(self, filename: str = None) -> str:
        """Exporta métricas para arquivo JSON"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_metrics_{timestamp}.json"
        
        data = {
            "export_timestamp": datetime.now().isoformat(),
            "summary": self.get_performance_summary(),
            "system_metrics": [asdict(m) for m in self.system_metrics],
            "trading_metrics": [asdict(m) for m in self.trading_metrics],
            "alerts": [asdict(a) for a in self.alerts],
            "performance_history": dict(self.performance_history),
            "counters": dict(self.counters)
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        print(f"📊 Métricas exportadas para: {filename}")
        return filename

def main():
    """Teste do monitor de performance"""
    print("📊 TESTE DO MONITOR DE PERFORMANCE NEØ")
    print("=" * 50)
    
    monitor = PerformanceMonitor()
    
    # Inicia monitoramento
    monitor.start_monitoring(interval=2.0)
    
    try:
        # Simula algumas métricas de trading
        for i in range(5):
            trading_metrics = TradingMetrics(
                timestamp=datetime.now().isoformat(),
                total_assets=100,
                processed_assets=95 + i,
                failed_assets=5 - i,
                processing_time=2.0 + i * 0.5,
                throughput=20.0 - i * 2,
                cache_hit_rate=0.8 + i * 0.02,
                api_requests=50 + i * 10,
                rate_limit_hits=i,
                avg_response_time=0.1 + i * 0.05,
                success_rate=0.9 + i * 0.01
            )
            
            monitor.record_trading_metrics(trading_metrics)
            time.sleep(3)
        
        # Gera relatório
        report = monitor.get_performance_report()
        print(report)
        
        # Exporta métricas
        filename = monitor.export_metrics()
        print(f"✅ Métricas exportadas: {filename}")
        
    finally:
        monitor.stop_monitoring()

if __name__ == "__main__":
    main()
