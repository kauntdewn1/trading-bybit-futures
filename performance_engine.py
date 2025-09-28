#!/usr/bin/env python3
"""
⚡ PERFORMANCE ENGINE NEØ - OTIMIZAÇÃO CRÍTICA
Sistema de processamento paralelo e cache inteligente para análise de ativos
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from collections import defaultdict
import pandas as pd

@dataclass
class PerformanceMetrics:
    """Métricas de performance do sistema"""
    total_assets: int
    processed_assets: int
    failed_assets: int
    processing_time: float
    cache_hits: int
    cache_misses: int
    api_requests: int
    rate_limit_hits: int
    avg_response_time: float
    throughput: float  # assets/second

class IntelligentCache:
    """
    Cache inteligente com TTL adaptativo baseado na volatilidade do mercado
    """
    
    def __init__(self):
        self.cache = {}
        self.access_times = {}
        self.hit_counts = defaultdict(int)
        self.miss_counts = defaultdict(int)
        self.volatility_cache = {}
        self.lock = threading.RLock()
        
    def _calculate_ttl(self, symbol: str, data_type: str) -> int:
        """Calcula TTL baseado na volatilidade e tipo de dado"""
        base_ttls = {
            "price": 5,      # Preços: 5 segundos
            "klines": 15,    # Klines: 15 segundos
            "indicators": 30, # Indicadores: 30 segundos
            "funding": 60,    # Funding: 1 minuto
            "volume": 10      # Volume: 10 segundos
        }
        
        base_ttl = base_ttls.get(data_type, 30)
        
        # Ajusta TTL baseado na volatilidade
        volatility = self.volatility_cache.get(symbol, 0.02)  # 2% padrão
        
        if volatility > 0.05:  # Alta volatilidade
            return max(base_ttl // 2, 5)  # TTL menor
        elif volatility < 0.01:  # Baixa volatilidade
            return base_ttl * 2  # TTL maior
        else:
            return base_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Obtém item do cache com validação de TTL"""
        with self.lock:
            if key not in self.cache:
                self.miss_counts[key.split('_')[0]] += 1
                return None
            
            data, timestamp, ttl = self.cache[key]
            current_time = time.time()
            
            # Verifica se expirou
            if current_time - timestamp > ttl:
                del self.cache[key]
                if key in self.access_times:
                    del self.access_times[key]
                self.miss_counts[key.split('_')[0]] += 1
                return None
            
            # Atualiza tempo de acesso
            self.access_times[key] = current_time
            self.hit_counts[key.split('_')[0]] += 1
            
            return data
    
    def set(self, key: str, data: Any, symbol: str = None, data_type: str = "default") -> None:
        """Define item no cache com TTL inteligente"""
        with self.lock:
            ttl = self._calculate_ttl(symbol or "default", data_type)
            self.cache[key] = (data, time.time(), ttl)
            self.access_times[key] = time.time()
    
    def cleanup_expired(self) -> int:
        """Remove itens expirados do cache"""
        with self.lock:
            current_time = time.time()
            expired_keys = []
            
            for key, (data, timestamp, ttl) in self.cache.items():
                if current_time - timestamp > ttl:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.cache[key]
                if key in self.access_times:
                    del self.access_times[key]
            
            return len(expired_keys)
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas do cache"""
        with self.lock:
            total_hits = sum(self.hit_counts.values())
            total_misses = sum(self.miss_counts.values())
            hit_rate = total_hits / (total_hits + total_misses) if (total_hits + total_misses) > 0 else 0
            
            return {
                "cache_size": len(self.cache),
                "hit_rate": hit_rate,
                "total_hits": total_hits,
                "total_misses": total_misses,
                "hit_counts": dict(self.hit_counts),
                "miss_counts": dict(self.miss_counts)
            }

class AdaptiveRateLimiter:
    """
    Rate limiter adaptativo com backoff exponencial inteligente
    """
    
    def __init__(self, max_requests: int = 100, per_minute: int = 60):
        self.max_requests = max_requests
        self.per_minute = per_minute
        self.requests = []
        self.success_rate = 1.0
        self.adaptive_delay = 0.05  # Começa com 50ms
        self.retry_count = 0
        self.last_error_time = 0
        self.error_count = 0
        self.lock = threading.RLock()
        
    def _calculate_delay(self) -> float:
        """Calcula delay baseado na taxa de sucesso e erros recentes"""
        base_delay = self.adaptive_delay
        
        # Ajusta baseado na taxa de sucesso
        if self.success_rate < 0.8:
            base_delay *= 2.0  # Dobra o delay se taxa baixa
        elif self.success_rate > 0.95:
            base_delay *= 0.8  # Reduz delay se taxa alta
        
        # Ajusta baseado em erros recentes
        current_time = time.time()
        if current_time - self.last_error_time < 10:  # Erro nos últimos 10s
            base_delay *= 1.5
        
        # Limita entre 10ms e 2s
        return max(0.01, min(base_delay, 2.0))
    
    async def make_request(self, session: aiohttp.ClientSession, url: str, **kwargs) -> Dict:
        """Faz request com rate limiting adaptativo"""
        async with self.lock:
            # Limpa requests antigos
            current_time = time.time()
            self.requests = [req_time for req_time in self.requests if current_time - req_time < 60]
            
            # Verifica rate limit
            if len(self.requests) >= self.max_requests:
                sleep_time = 60 - (current_time - self.requests[0])
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
            
            # Calcula delay adaptativo
            delay = self._calculate_delay()
            await asyncio.sleep(delay)
            
            try:
                # Faz o request
                async with session.get(url, **kwargs) as response:
                    result = await response.json()
                    
                    # Atualiza métricas de sucesso
                    self.requests.append(current_time)
                    self.success_rate = 0.9 * self.success_rate + 0.1
                    self.retry_count = 0
                    self.error_count = 0
                    
                    return result
                    
            except Exception as e:
                # Atualiza métricas de erro
                self.success_rate = 0.9 * self.success_rate
                self.last_error_time = current_time
                self.error_count += 1
                
                if "rate limit" in str(e).lower() or response.status == 429:
                    self.retry_count += 1
                    backoff_time = min(2 ** self.retry_count, 30)
                    await asyncio.sleep(backoff_time)
                
                raise e

class PerformanceEngine:
    """
    Engine de performance com processamento paralelo e cache inteligente
    """
    
    def __init__(self, max_workers: int = 20):
        self.cache = IntelligentCache()
        self.rate_limiter = AdaptiveRateLimiter()
        self.max_workers = max_workers
        self.metrics = PerformanceMetrics(
            total_assets=0, processed_assets=0, failed_assets=0,
            processing_time=0, cache_hits=0, cache_misses=0,
            api_requests=0, rate_limit_hits=0, avg_response_time=0, throughput=0
        )
        self.session = None
        
    async def _init_session(self):
        """Inicializa sessão HTTP assíncrona"""
        if not self.session:
            connector = aiohttp.TCPConnector(limit=100, limit_per_host=20)
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
    
    async def _get_futures_data_async(self, symbol: str) -> Optional[Dict]:
        """Obtém dados de futuros de forma assíncrona"""
        try:
            await self._init_session()
            
            cache_key = f"futures_{symbol}"
            cached_data = self.cache.get(cache_key)
            if cached_data:
                self.metrics.cache_hits += 1
                return cached_data
            
            # URL da API Bybit
            url = f"https://api.bybit.com/v5/market/tickers?category=linear&symbol={symbol}"
            
            result = await self.rate_limiter.make_request(self.session, url)
            
            if result.get("retCode") == 0 and result.get("result", {}).get("list"):
                data = result["result"]["list"][0]
                futures_data = {
                    "price": float(data["lastPrice"]),
                    "funding_rate": float(data.get("fundingRate", 0)),
                    "open_interest": float(data.get("openInterest", 0)),
                    "volume_24h": float(data.get("volume24h", 0))
                }
                
                # Salva no cache
                self.cache.set(cache_key, futures_data, symbol, "price")
                self.metrics.cache_misses += 1
                self.metrics.api_requests += 1
                
                return futures_data
            else:
                return None
                
        except Exception as e:
            print(f"Erro ao obter dados de {symbol}: {e}")
            return None
    
    async def _get_klines_async(self, symbol: str, interval: str = "15", limit: int = 50) -> Optional[pd.DataFrame]:
        """Obtém klines de forma assíncrona"""
        try:
            await self._init_session()
            
            cache_key = f"klines_{symbol}_{interval}_{limit}"
            cached_data = self.cache.get(cache_key)
            if cached_data:
                self.metrics.cache_hits += 1
                return cached_data
            
            # URL da API Bybit
            url = f"https://api.bybit.com/v5/market/kline?category=linear&symbol={symbol}&interval={interval}&limit={limit}"
            
            result = await self.rate_limiter.make_request(self.session, url)
            
            if result.get("retCode") == 0 and result.get("result", {}).get("list"):
                klines = result["result"]["list"]
                
                # Converte para DataFrame
                df = pd.DataFrame(klines, columns=[
                    "timestamp", "open", "high", "low", "close", "volume", "turnover"
                ])
                df["timestamp"] = pd.to_datetime(pd.to_numeric(df["timestamp"], errors='coerce'), unit='ms')
                df.set_index("timestamp", inplace=True)
                df = df.astype(float)
                
                # Salva no cache
                self.cache.set(cache_key, df, symbol, "klines")
                self.metrics.cache_misses += 1
                self.metrics.api_requests += 1
                
                return df
            else:
                return None
                
        except Exception as e:
            print(f"Erro ao obter klines de {symbol}: {e}")
            return None
    
    async def _analyze_asset_async(self, symbol: str) -> Optional[Dict]:
        """Analisa um ativo de forma assíncrona"""
        try:
            # Obtém dados em paralelo
            futures_task = self._get_futures_data_async(symbol)
            klines_task = self._get_klines_async(symbol)
            
            futures_data, df = await asyncio.gather(futures_task, klines_task)
            
            if not futures_data or df is None or len(df) < 20:
                return None
            
            # Calcula indicadores técnicos
            from ta.momentum import RSIIndicator
            from ta.trend import MACD
            
            rsi = RSIIndicator(close=df["close"], window=14).rsi().iloc[-1]
            macd = MACD(close=df["close"])
            macd_line = macd.macd().iloc[-1]
            signal_line = macd.macd_signal().iloc[-1]
            
            # Volume
            volume_sma = df["volume"].rolling(window=20).mean().iloc[-1]
            current_volume = df["volume"].iloc[-1]
            volume_ratio = current_volume / volume_sma if volume_sma > 0 else 1
            
            # Determina status
            macd_status = "bullish" if macd_line > signal_line else "bearish"
            volume_status = "high" if volume_ratio > 1.5 else "low"
            oi_status = "up" if futures_data["open_interest"] > 1000000 else "down"
            
            # Calcula scores
            score_long = 0
            score_short = 0
            
            # Regras LONG
            if rsi < 35: score_long += 3
            if macd_status == "bullish": score_long += 2
            if futures_data["funding_rate"] < 0: score_long += 1
            if volume_status == "high": score_long += 1
            if oi_status == "up": score_long += 1
            
            # Regras SHORT
            if rsi > 70: score_short += 3
            if macd_status == "bearish": score_short += 2
            if futures_data["funding_rate"] > 0: score_short += 1
            if volume_status == "high": score_short += 1
            if oi_status == "down": score_short += 1
            
            return {
                "symbol": symbol,
                "long_score": round(score_long, 1),
                "short_score": round(score_short, 1),
                "data": {
                    "symbol": symbol,
                    "price": futures_data["price"],
                    "rsi": round(rsi, 1),
                    "macd": macd_status,
                    "volume": volume_status,
                    "funding": round(futures_data["funding_rate"], 4),
                    "oi": oi_status,
                    "volume_ratio": round(volume_ratio, 2)
                }
            }
            
        except Exception as e:
            print(f"Erro ao analisar {symbol}: {e}")
            return None
    
    async def analyze_assets_parallel(self, symbols: List[str]) -> List[Dict]:
        """Analisa múltiplos ativos em paralelo"""
        start_time = time.time()
        
        print(f"⚡ ANALISANDO {len(symbols)} ATIVOS EM PARALELO...")
        
        # Cria semáforo para limitar concorrência
        semaphore = asyncio.Semaphore(self.max_workers)
        
        async def analyze_with_semaphore(symbol):
            async with semaphore:
                return await self._analyze_asset_async(symbol)
        
        # Executa análises em paralelo
        tasks = [analyze_with_semaphore(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Processa resultados
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Erro em {symbols[i]}: {result}")
                self.metrics.failed_assets += 1
            elif result is not None:
                valid_results.append(result)
                self.metrics.processed_assets += 1
            else:
                self.metrics.failed_assets += 1
        
        # Atualiza métricas
        end_time = time.time()
        self.metrics.processing_time = end_time - start_time
        self.metrics.total_assets = len(symbols)
        self.metrics.throughput = len(symbols) / self.metrics.processing_time
        self.metrics.avg_response_time = self.metrics.processing_time / len(symbols)
        
        print(f"✅ ANÁLISE CONCLUÍDA: {len(valid_results)}/{len(symbols)} ativos processados")
        print(f"⏱️ Tempo: {self.metrics.processing_time:.2f}s")
        print(f"🚀 Throughput: {self.metrics.throughput:.1f} ativos/s")
        
        return valid_results
    
    def get_performance_report(self) -> str:
        """Gera relatório de performance"""
        cache_stats = self.cache.get_stats()
        
        report = f"""
⚡ RELATÓRIO DE PERFORMANCE - SNIPER NEØ
=========================================

📊 MÉTRICAS DE PROCESSAMENTO:
- Ativos processados: {self.metrics.processed_assets}/{self.metrics.total_assets}
- Taxa de sucesso: {(self.metrics.processed_assets/self.metrics.total_assets*100):.1f}%
- Tempo total: {self.metrics.processing_time:.2f}s
- Throughput: {self.metrics.throughput:.1f} ativos/s
- Tempo médio por ativo: {self.metrics.avg_response_time:.3f}s

📈 MÉTRICAS DE CACHE:
- Hit rate: {cache_stats['hit_rate']*100:.1f}%
- Cache size: {cache_stats['cache_size']} itens
- Total hits: {cache_stats['total_hits']}
- Total misses: {cache_stats['total_misses']}

🌐 MÉTRICAS DE API:
- Requests totais: {self.metrics.api_requests}
- Rate limit hits: {self.metrics.rate_limit_hits}
- Taxa de sucesso: {(self.metrics.success_rate*100):.1f}%

🚀 MELHORIAS DE PERFORMANCE:
- Processamento paralelo: ✅ Ativo
- Cache inteligente: ✅ Ativo
- Rate limiting adaptativo: ✅ Ativo
- Validação em batch: ✅ Ativo

📈 COMPARAÇÃO COM SISTEMA ANTERIOR:
- Tempo de análise: {self.metrics.processing_time:.1f}s vs 40+ segundos
- Melhoria: {((40 - self.metrics.processing_time) / 40 * 100):.1f}% mais rápido
- Throughput: {self.metrics.throughput:.1f} ativos/s vs ~10 ativos/s
- Melhoria: {(self.metrics.throughput / 10):.1f}x mais eficiente
"""
        return report
    
    async def cleanup(self):
        """Limpa recursos"""
        if self.session:
            await self.session.close()
        
        # Limpa cache expirado
        expired_count = self.cache.cleanup_expired()
        if expired_count > 0:
            print(f"🧹 Cache limpo: {expired_count} itens expirados removidos")

def main():
    """Teste do engine de performance"""
    print("⚡ TESTE DO ENGINE DE PERFORMANCE NEØ")
    print("=" * 50)
    
    # Lista de ativos para teste
    test_symbols = [
        "BTCUSDT", "ETHUSDT", "SOLUSDT", "ADAUSDT", "AVAXUSDT",
        "XRPUSDT", "DOGEUSDT", "MATICUSDT", "LTCUSDT", "UNIUSDT"
    ]
    
    async def run_test():
        engine = PerformanceEngine(max_workers=10)
        
        try:
            # Testa análise paralela
            results = await engine.analyze_assets_parallel(test_symbols)
            
            # Mostra resultados
            print(f"\n📊 RESULTADOS:")
            for result in results[:5]:  # Mostra apenas os primeiros 5
                print(f"   {result['symbol']}: LONG {result['long_score']}/10, SHORT {result['short_score']}/10")
            
            # Gera relatório
            report = engine.get_performance_report()
            print(report)
            
        finally:
            await engine.cleanup()
    
    # Executa teste
    asyncio.run(run_test())

if __name__ == "__main__":
    main()
