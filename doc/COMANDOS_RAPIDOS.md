# ⚡ COMANDOS RÁPIDOS - SNIPER NEØ

## **🚀 EXECUÇÃO IMEDIATA**

### **DASHBOARD (PRINCIPAL)**
```bash
streamlit run sniper_dashboard.py
```

### **TELEGRAM BOT (ATUALIZADO)**
```bash
python telegram_sniper_enhanced.py
```

### **ANÁLISE MANUAL**
```bash
python analyze_on_demand.py
```

---

## **📱 COMANDOS TELEGRAM**

### **ANÁLISE COMPLETA**
```
/analyze
```

### **ANÁLISE ESPECÍFICA**
```
/analyze BTCUSDT,ETHUSDT
```

### **TOP 6 ATIVOS**
```
/ranking
```

### **STATUS**
```
/status
```

### **MODO FÚRIA**
```
/mode_furia
```

### **REINICIAR**
```
/restart
```

### **AJUDA**
```
/help
```

---

## **🎮 DASHBOARD - BOTÕES PRINCIPAIS**

### **HEADER (SEMPRE VISÍVEL)**

- **🔎 ANALISAR TUDO** - Análise completa
- **📊 TOP 6 ATIVOS** - Ranking
- **♻️ REINICIAR ENGINE** - Reinicia sistema
- **💀 MODO FÚRIA** - Threshold 3.0

### **ABA RANKING**

- **🔄 Atualizar Ranking** - Força atualização
- **🔍 Análise Completa** - Executa análise
- **⚙️ Configurações** - Vai para controles
- **📊 Estatísticas** - Hit rate

### **ABA CONTROLES**

- **Slider Threshold** - 0.0 a 10.0
- **Botões Rápidos** - Conservador/Moderado/Agressivo
- **Input Ativos** - `BTCUSDT,ETHUSDT,SOLUSDT`
- **Comandos** - `/analyze`, `/ranking`, `/status`

---

## **⚙️ CONFIGURAÇÕES RÁPIDAS**

### **THRESHOLD**

- **7.0:** Conservador (padrão)
- **5.0:** Moderado
- **3.0:** Agressivo

### **INTERPRETAÇÃO SCORES**

- **8-10:** Excelente oportunidade
- **6-7:** Boa oportunidade
- **4-5:** Moderada
- **0-3:** Evitar

---

## **🔍 CHAT_ID TELEGRAM**

### **MÉTODO RÁPIDO**

1. Procure `@userinfobot` no Telegram
2. Envie qualquer mensagem
3. Copie o chat_id que ele retornar

### **SCRIPT**

```bash
python get_chat_id.py
```

---

## **🔧 PROBLEMAS COMUNS**

### **DASHBOARD NÃO CARREGA**

```bash
streamlit cache clear
streamlit run sniper_dashboard.py --logger.level debug
```

### **BOTÕES NÃO FUNCIONAM**

- Recarregue a página (F5)
- Use "♻️ REINICIAR ENGINE"

### **BOT NÃO RESPONDE**

- Verifique se está rodando: `python telegram_sniper_enhanced.py`
- Use `/restart` no Telegram

---

## **📊 FLUXO RÁPIDO**

### **1️⃣ ANÁLISE**

- Dashboard: Clique "🔎 ANALISAR TUDO"
- Telegram: Envie `/analyze`

### **2️⃣ VALIDAÇÃO**

- Dashboard: Veja "📊 TOP 6 ATIVOS"
- Telegram: Envie `/ranking`

### **3️⃣ EXECUÇÃO**

- Bybit: Execute o trade
- Monitore: Dashboard ou Telegram

---

**🎯 COMANDOS ESSENCIAIS PARA OPERAR RAPIDAMENTE!**
