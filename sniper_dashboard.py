#!/usr/bin/env python3
"""
🎯 SNIPER DASHBOARD NEØ - VISUALIZAÇÃO EM TEMPO REAL
Dashboard profissional para monitoramento de sinais
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
import os
from sniper_system import SniperSystem
from bybit_api import connect_bybit, get_futures_balance

# Configuração da página
st.set_page_config(
    page_title="🥷 SNIPER DASHBOARD NEØ",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado para botões profissionais
st.markdown("""
<style>
/* Botões principais */
.stButton > button {
    background-color: #1a1a1a;
    color: white;
    border: 2px solid #333;
    border-radius: 10px;
    padding: 12px 20px;
    font-size: 16px;
    font-weight: bold;
    transition: all 0.3s ease;
    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
}

.stButton > button:hover {
    background-color: #333;
    border-color: #555;
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(0,0,0,0.4);
}

/* Botão primário */
.stButton > button[kind="primary"] {
    background: linear-gradient(45deg, #ff6b6b, #ee5a24);
    border-color: #ff6b6b;
}

.stButton > button[kind="primary"]:hover {
    background: linear-gradient(45deg, #ee5a24, #ff6b6b);
    transform: translateY(-3px);
}

/* Botão secundário (MODO FÚRIA) */
.stButton > button[kind="secondary"] {
    background: linear-gradient(45deg, #b30000, #ff0000);
    border-color: #b30000;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(255, 0, 0, 0.7); }
    70% { box-shadow: 0 0 0 10px rgba(255, 0, 0, 0); }
    100% { box-shadow: 0 0 0 0 rgba(255, 0, 0, 0); }
}

.stButton > button[kind="secondary"]:hover {
    background: linear-gradient(45deg, #ff0000, #b30000);
    animation: none;
}

/* Métricas com estilo */
.metric-container {
    background: linear-gradient(135deg, #1e3c72, #2a5298);
    padding: 20px;
    border-radius: 15px;
    color: white;
    text-align: center;
    box-shadow: 0 8px 16px rgba(0,0,0,0.3);
}

/* Alertas com estilo */
.alert-success {
    background: linear-gradient(135deg, #00b894, #00a085);
    color: white;
    padding: 15px;
    border-radius: 10px;
    border-left: 5px solid #00a085;
}

.alert-warning {
    background: linear-gradient(135deg, #fdcb6e, #e17055);
    color: white;
    padding: 15px;
    border-radius: 10px;
    border-left: 5px solid #e17055;
}

.alert-error {
    background: linear-gradient(135deg, #e84393, #d63031);
    color: white;
    padding: 15px;
    border-radius: 10px;
    border-left: 5px solid #d63031;
}

/* Tabelas com estilo */
.dataframe {
    background: #1a1a1a;
    color: white;
    border-radius: 10px;
    overflow: hidden;
}

/* Sidebar com estilo */
.css-1d391kg {
    background: linear-gradient(180deg, #1a1a1a, #2d2d2d);
}

/* Títulos com estilo */
h1, h2, h3 {
    color: #ff6b6b;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
}

/* Divider com estilo */
hr {
    border: none;
    height: 3px;
    background: linear-gradient(90deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4);
    border-radius: 2px;
    margin: 20px 0;
}
</style>
""", unsafe_allow_html=True)

class SniperDashboard:
    def __init__(self):
        self.sniper = SniperSystem()
        self.session = connect_bybit()
        
    def load_alert_history(self):
        """Carrega histórico de alertas"""
        try:
            if os.path.exists('sniper_alerts.json'):
                with open('sniper_alerts.json', 'r') as f:
                    return json.load(f)
        except:
            pass
        return []
    
    def save_alert(self, alert_data):
        """Salva alerta no histórico"""
        history = self.load_alert_history()
        history.append(alert_data)
        
        # Mantém apenas últimos 100 alertas
        if len(history) > 100:
            history = history[-100:]
            
        with open('sniper_alerts.json', 'w') as f:
            json.dump(history, f, indent=2)
    
    def get_live_ranking(self):
        """Obtém ranking em tempo real - TOP 6 sempre"""
        ranking = self.sniper.get_full_ranking()
        
        # Converte para DataFrame
        df_data = []
        for i, ativo in enumerate(ranking[:6], 1):  # TOP 6 sempre
            df_data.append({
                "Posição": i,
                "Ativo": ativo["ativo"],
                "Direção": ativo["direcao"],
                "Score": ativo["score"],
                "RSI": ativo["dados"]["rsi"],
                "MACD": ativo["dados"]["macd"],
                "Volume": ativo["dados"]["volume"],
                "Funding": f"{ativo['dados']['funding']:.4f}",
                "OI": ativo["dados"]["oi"],
                "Preço": ativo["dados"]["price"]
            })
        
        return pd.DataFrame(df_data)
    
    def render_header(self):
        """Renderiza cabeçalho com botões principais"""
        st.title("🥷 SNIPER DASHBOARD NEØ")
        st.markdown("**Sistema de Trading Automatizado - Node NΞØ**")
        
        # Status do sistema
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Status", "🟢 ATIVO", delta="Online")
        
        with col2:
            balance = get_futures_balance(self.session)
            st.metric("Saldo USDT", f"{balance['available']:.2f}")
        
        with col3:
            st.metric("Threshold", f"{self.sniper.threshold}/10")
        
        with col4:
            st.metric("Ativos", f"{len(self.sniper.assets)}")
        
        st.divider()
        
        # BOTÕES PRINCIPAIS NO HEADER
        st.markdown("### 🎯 AÇÕES RÁPIDAS")
        
        # Grid de botões principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔎 ANALISAR TUDO", type="primary", use_container_width=True):
                with st.spinner("🔍 Varrendo TODOS os ativos..."):
                    best_trade, direction, score, frenzy_count = self.sniper.find_best_trade()
                    alert = self.sniper.generate_sniper_alert(best_trade, direction, score, frenzy_count)
                    
                    if alert["status"] == "TARGET":
                        st.success("🎯 ALVO IDENTIFICADO!")
                        if frenzy_count >= 3:
                            st.error("🚨 MODO RAIVA TOTAL ATIVADO!")
                        st.code(alert["alert"])
                        
                        # Salva no histórico
                        self.save_alert(alert["data"])
                    else:
                        st.info("⏳ Nenhum alvo encontrado")
        
        with col2:
            if st.button("📊 TOP 6 ATIVOS", use_container_width=True):
                with st.spinner("📊 Gerando ranking..."):
                    ranking_df = self.get_live_ranking()
                    if not ranking_df.empty:
                        st.success("🏆 TOP 6 ATIVOS RANQUEADOS")
                        st.dataframe(ranking_df, use_container_width=True)
                    else:
                        st.warning("Nenhum dado disponível")
        
        with col3:
            if st.button("♻️ REINICIAR ENGINE", use_container_width=True):
                with st.spinner("🔄 Reiniciando sistema..."):
                    # Reinicia o sistema sniper
                    self.sniper = SniperSystem()
                    st.success("✅ Engine reiniciado com sucesso!")
                    st.rerun()
        
        with col4:
            if st.button("💀 MODO FÚRIA", type="secondary", use_container_width=True):
                # Ativa modo fúria (threshold baixo)
                self.sniper.threshold = 3.0
                st.error("🔥 MODO FÚRIA ATIVADO!")
                st.warning("⚠️ Threshold reduzido para 3.0 - CUIDADO!")
                st.rerun()
        
        st.divider()
    
    def render_ranking(self):
        """Renderiza ranking de ativos - TOP 6 sempre"""
        st.subheader("🏆 TOP 6 ATIVOS RANQUEADOS")
        
        # Botões de controle rápido
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔄 Atualizar Ranking", type="primary", use_container_width=True):
                st.rerun()
        
        with col2:
            if st.button("🎯 Análise Completa", use_container_width=True):
                with st.spinner("🔍 Executando análise completa..."):
                    best_trade, direction, score, frenzy_count = self.sniper.find_best_trade()
                    if best_trade:
                        st.success(f"🎯 Melhor ativo: {best_trade['symbol']} {direction} - Score: {score}/10")
                        if frenzy_count >= 3:
                            st.error("🚨 MODO RAIVA TOTAL ATIVADO!")
                    else:
                        st.info("⏳ Nenhum alvo encontrado")
        
        with col3:
            if st.button("⚙️ Configurações", use_container_width=True):
                st.info("💡 Use a aba 'Controles' para configurações avançadas")
        
        with col4:
            if st.button("📊 Estatísticas", use_container_width=True):
                try:
                    summary = self.sniper.tracker.get_performance_summary()
                    st.success(f"📈 Hit Rate: {summary['hit_rate']:.1%} | Alertas: {summary['total_alerts']}")
                except:
                    st.info("📊 Estatísticas não disponíveis ainda")
        
        # Obtém ranking TOP 6
        ranking_df = self.get_live_ranking()
        
        if not ranking_df.empty:
            # Filtros
            col1, col2 = st.columns(2)
            
            with col1:
                min_score = st.slider("Score Mínimo", 0.0, 10.0, 0.0)
            
            with col2:
                direction_filter = st.selectbox("Direção", ["Todas", "LONG", "SHORT"])
            
            # Aplica filtros
            filtered_df = ranking_df[ranking_df["Score"] >= min_score]
            if direction_filter != "Todas":
                filtered_df = filtered_df[filtered_df["Direção"] == direction_filter]
            
            # Exibe tabela TOP 6
            st.dataframe(
                filtered_df,
                use_container_width=True,
                hide_index=True
            )
            
            # Gráfico de scores TOP 6
            if not filtered_df.empty:
                fig = px.bar(
                    filtered_df,
                    x="Ativo",
                    y="Score",
                    color="Direção",
                    title="🏆 TOP 6 Ativos por Score",
                    color_discrete_map={"LONG": "#00ff00", "SHORT": "#ff0000"}
                )
                fig.update_layout(showlegend=True)
                st.plotly_chart(fig, use_container_width=True)
            
            # Estatísticas
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Ativos", len(ranking_df))
            
            with col2:
                long_count = len(ranking_df[ranking_df["Direção"] == "LONG"])
                st.metric("LONG", long_count)
            
            with col3:
                short_count = len(ranking_df[ranking_df["Direção"] == "SHORT"])
                st.metric("SHORT", short_count)
        else:
            st.warning("Nenhum dado disponível")
    
    def render_alerts_history(self):
        """Renderiza histórico de alertas"""
        st.subheader("📋 HISTÓRICO DE ALERTAS")
        
        history = self.load_alert_history()
        
        if history:
            # Converte para DataFrame
            df = pd.DataFrame(history)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Filtros de data
            col1, col2 = st.columns(2)
            
            with col1:
                start_date = st.date_input("Data Inicial", value=datetime.now().date() - timedelta(days=7))
            
            with col2:
                end_date = st.date_input("Data Final", value=datetime.now().date())
            
            # Filtra por data
            df_filtered = df[
                (df['timestamp'].dt.date >= start_date) & 
                (df['timestamp'].dt.date <= end_date)
            ]
            
            # Exibe histórico
            st.dataframe(
                df_filtered[['timestamp', 'symbol', 'direction', 'score']],
                use_container_width=True,
                hide_index=True
            )
            
            # Estatísticas
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Alertas", len(df_filtered))
            
            with col2:
                long_count = len(df_filtered[df_filtered['direction'] == 'LONG'])
                st.metric("LONG", long_count)
            
            with col3:
                short_count = len(df_filtered[df_filtered['direction'] == 'SHORT'])
                st.metric("SHORT", short_count)
        else:
            st.info("Nenhum alerta registrado ainda")
    
    def render_controls(self):
        """Renderiza controles do sistema com botões avançados"""
        st.subheader("⚙️ CONTROLES DO SISTEMA")
        
        # BOTÕES DE AÇÃO PRINCIPAIS
        st.markdown("### 🎯 AÇÕES RÁPIDAS")
        
        # Grid de botões principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔎 ANALISAR TUDO", type="primary", use_container_width=True):
                with st.spinner("🔍 Varrendo TODOS os ativos..."):
                    best_trade, direction, score, frenzy_count = self.sniper.find_best_trade()
                    alert = self.sniper.generate_sniper_alert(best_trade, direction, score, frenzy_count)
                    
                    if alert["status"] == "TARGET":
                        st.success("🎯 ALVO IDENTIFICADO!")
                        if frenzy_count >= 3:
                            st.error("🚨 MODO RAIVA TOTAL ATIVADO!")
                        st.code(alert["alert"])
                        
                        # Salva no histórico
                        self.save_alert(alert["data"])
                    else:
                        st.info("⏳ Nenhum alvo encontrado")
        
        with col2:
            if st.button("📊 TOP 6 ATIVOS", use_container_width=True):
                with st.spinner("📊 Gerando ranking..."):
                    ranking_df = self.get_live_ranking()
                    if not ranking_df.empty:
                        st.success("🏆 TOP 6 ATIVOS RANQUEADOS")
                        st.dataframe(ranking_df, use_container_width=True)
                    else:
                        st.warning("Nenhum dado disponível")
        
        with col3:
            if st.button("♻️ REINICIAR ENGINE", use_container_width=True):
                with st.spinner("🔄 Reiniciando sistema..."):
                    # Reinicia o sistema sniper
                    self.sniper = SniperSystem()
                    st.success("✅ Engine reiniciado com sucesso!")
                    st.rerun()
        
        with col4:
            if st.button("💀 MODO FÚRIA", type="secondary", use_container_width=True):
                # Ativa modo fúria (threshold baixo)
                self.sniper.threshold = 3.0
                st.error("🔥 MODO FÚRIA ATIVADO!")
                st.warning("⚠️ Threshold reduzido para 3.0 - CUIDADO!")
                st.rerun()
        
        st.divider()
        
        # CONTROLES AVANÇADOS
        st.markdown("### ⚙️ CONTROLES AVANÇADOS")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🎯 Configurações de Score")
            new_threshold = st.slider("Threshold de Score", 0.0, 10.0, self.sniper.threshold, 0.5)
            
            # Botões de threshold rápido
            col_th1, col_th2, col_th3 = st.columns(3)
            with col_th1:
                if st.button("Conservador (7.0)", use_container_width=True):
                    self.sniper.threshold = 7.0
                    st.success("Threshold: 7.0 (Conservador)")
                    st.rerun()
            
            with col_th2:
                if st.button("Moderado (5.0)", use_container_width=True):
                    self.sniper.threshold = 5.0
                    st.success("Threshold: 5.0 (Moderado)")
                    st.rerun()
            
            with col_th3:
                if st.button("Agressivo (3.0)", use_container_width=True):
                    self.sniper.threshold = 3.0
                    st.success("Threshold: 3.0 (Agressivo)")
                    st.rerun()
            
            if st.button("Atualizar Threshold Manual", type="primary"):
                self.sniper.threshold = new_threshold
                st.success(f"Threshold atualizado para {new_threshold}")
                st.rerun()
        
        with col2:
            st.markdown("#### 🔧 Análise Específica")
            
            # Input para análise específica
            symbols_input = st.text_input(
                "Ativos Específicos (separados por vírgula)",
                placeholder="Ex: BTCUSDT,ETHUSDT,SOLUSDT",
                help="Digite os símbolos dos ativos que deseja analisar"
            )
            
            if st.button("🎯 ANALISAR ESPECÍFICOS", type="primary"):
                if symbols_input:
                    symbols = [s.strip().upper() for s in symbols_input.split(',')]
                    with st.spinner(f"🔍 Analisando {len(symbols)} ativos específicos..."):
                        ranking = self.sniper.analyze_on_demand(symbols)
                        
                        if ranking:
                            st.success(f"📊 Análise de {len(symbols)} ativos concluída")
                            
                            # Converte para DataFrame
                            df_data = []
                            for i, ativo in enumerate(ranking, 1):
                                df_data.append({
                                    "Posição": i,
                                    "Ativo": ativo["ativo"],
                                    "Direção": ativo["direcao"],
                                    "Score": ativo["score"],
                                    "RSI": ativo["dados"]["rsi"],
                                    "MACD": ativo["dados"]["macd"],
                                    "Volume": ativo["dados"]["volume"],
                                    "Funding": f"{ativo['dados']['funding']:.4f}",
                                    "Combo Patterns": ', '.join(ativo['dados'].get('combo_patterns_long' if ativo['direcao'] == 'LONG' else 'combo_patterns_short', []))
                                })
                            
                            df = pd.DataFrame(df_data)
                            st.dataframe(df, use_container_width=True)
                        else:
                            st.warning("Nenhum resultado encontrado")
                else:
                    st.warning("Digite pelo menos um símbolo para analisar")
        
        st.divider()
        
        # COMANDO VIA DASHBOARD
        st.markdown("### 💬 COMANDO VIA DASHBOARD")
        
        command_input = st.text_input(
            "Digite comando (ex: /analyze BTCUSDT,ETHUSDT)",
            placeholder="/analyze BTCUSDT,ETHUSDT",
            help="Comandos disponíveis: /analyze, /ranking, /status"
        )
        
        if st.button("🚀 EXECUTAR COMANDO", type="primary"):
            if command_input.startswith('/'):
                parts = command_input.split(' ', 1)
                command = parts[0]
                args = parts[1] if len(parts) > 1 else ""
                
                if command == '/analyze':
                    if args:
                        symbols = [s.strip().upper() for s in args.split(',')]
                        with st.spinner(f"🔍 Executando /analyze {args}..."):
                            ranking = self.sniper.analyze_on_demand(symbols)
                            if ranking:
                                st.success(f"✅ Comando executado: {command} {args}")
                                st.dataframe(pd.DataFrame([{
                                    "Ativo": ativo["ativo"],
                                    "Direção": ativo["direcao"],
                                    "Score": ativo["score"]
                                } for ativo in ranking[:6]]), use_container_width=True)
                            else:
                                st.warning("Nenhum resultado encontrado")
                    else:
                        st.info("Use: /analyze BTCUSDT,ETHUSDT")
                
                elif command == '/ranking':
                    with st.spinner("📊 Executando /ranking..."):
                        ranking_df = self.get_live_ranking()
                        st.success("✅ Comando executado: /ranking")
                        st.dataframe(ranking_df, use_container_width=True)
                
                elif command == '/status':
                    st.success("✅ Comando executado: /status")
                    st.info("🟢 Sistema Online - Node NΞØ Ativo")
                
                else:
                    st.error(f"❌ Comando não reconhecido: {command}")
            else:
                st.warning("Comandos devem começar com /")
        
        st.divider()
        
        # ESTATÍSTICAS DO SISTEMA
        st.markdown("### 📈 ESTATÍSTICAS DO SISTEMA")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Threshold Atual", f"{self.sniper.threshold}/10")
        
        with col2:
            st.metric("Ativos Monitorados", len(self.sniper.assets))
        
        with col3:
            # Performance do tracker
            try:
                summary = self.sniper.tracker.get_performance_summary()
                st.metric("Hit Rate", f"{summary['hit_rate']:.1%}")
            except:
                st.metric("Hit Rate", "N/A")
        
        with col4:
            st.metric("Status", "🟢 ATIVO")
    
    def run(self):
        """Executa o dashboard"""
        # Sidebar
        with st.sidebar:
            st.header("🥷 SNIPER NEØ")
            st.markdown("**Sistema de Trading Automatizado**")
            
            # Status
            st.success("🟢 Sistema Ativo")
            
            # Configurações rápidas
            st.subheader("⚙️ Configurações")
            auto_refresh = st.checkbox("Auto-refresh", value=True)
            refresh_interval = st.slider("Intervalo (segundos)", 30, 300, 60)
            
            if auto_refresh:
                st.info(f"Atualização automática a cada {refresh_interval}s")
        
        # Conteúdo principal
        self.render_header()
        st.divider()
        
        # Tabs
        tab1, tab2, tab3 = st.tabs(["📊 Ranking", "📋 Alertas", "⚙️ Controles"])
        
        with tab1:
            self.render_ranking()
        
        with tab2:
            self.render_alerts_history()
        
        with tab3:
            self.render_controls()
        
        # Auto-refresh removido para evitar problemas
        # Use o botão "Atualizar Ranking" para refresh manual

def main():
    """Função principal"""
    dashboard = SniperDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
