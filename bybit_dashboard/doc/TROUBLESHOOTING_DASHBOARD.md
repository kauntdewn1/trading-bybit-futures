# 🔧 TROUBLESHOOTING DASHBOARD - BOTÕES NÃO APARECEM

## **🚨 PROBLEMA IDENTIFICADO**

Os botões não estão aparecendo no dashboard. Vou te ajudar a resolver isso.

---

## **✅ SOLUÇÕES IMPLEMENTADAS**

### **1️⃣ BOTÕES MOVIDOS PARA O HEADER**
- **Antes:** Botões estavam apenas na aba "Controles"
- **Agora:** Botões principais estão no header (visível sempre)
- **Localização:** Logo após as métricas de status

### **2️⃣ BOTÕES ADICIONAIS NA ABA RANKING**
- **Novos botões:** Análise Completa, Configurações, Estatísticas
- **Localização:** Aba "📊 Ranking"
- **Funcionalidade:** Controles rápidos sem sair da aba

---

## **🔍 COMO VERIFICAR**

### **Passo 1: Teste Simples**
```bash
streamlit run test_dashboard_simple.py
```
- Deve mostrar 4 botões de teste
- Se não aparecer, problema é com Streamlit

### **Passo 2: Dashboard Principal**
```bash
streamlit run sniper_dashboard.py
```
- Deve mostrar botões no header
- Deve mostrar botões na aba Ranking

### **Passo 3: Verificar Localização**
1. **Header:** Logo após "Sistema de Trading Automatizado"
2. **Aba Ranking:** Logo após "TOP 6 ATIVOS RANQUEADOS"
3. **Aba Controles:** Controles avançados completos

---

## **🛠️ POSSÍVEIS CAUSAS**

### **1️⃣ Cache do Streamlit**
```bash
# Limpar cache
streamlit cache clear
# Ou reiniciar o servidor
```

### **2️⃣ Versão do Streamlit**
```bash
# Verificar versão
streamlit --version
# Atualizar se necessário
pip install --upgrade streamlit
```

### **3️⃣ Erro de Importação**
- Verificar se todos os módulos estão instalados
- Verificar se não há erros de sintaxe

### **4️⃣ Problema de CSS**
- CSS customizado pode estar interferindo
- Testar sem CSS primeiro

---

## **🚀 SOLUÇÕES ALTERNATIVAS**

### **Opção 1: Dashboard Simplificado**
Se o problema persistir, use o dashboard básico:

```python
import streamlit as st

st.title("🥷 SNIPER DASHBOARD")
st.markdown("### 🎯 AÇÕES RÁPIDAS")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🔎 ANALISAR TUDO", type="primary"):
        st.success("Análise executada!")

with col2:
    if st.button("📊 TOP 6 ATIVOS"):
        st.info("Ranking gerado!")

with col3:
    if st.button("♻️ REINICIAR"):
        st.success("Sistema reiniciado!")

with col4:
    if st.button("💀 MODO FÚRIA", type="secondary"):
        st.error("Modo fúria ativado!")
```

### **Opção 2: Comandos via Input**
```python
command = st.text_input("Digite comando:", placeholder="/analyze")
if st.button("Executar"):
    if command == "/analyze":
        st.success("Análise executada!")
```

---

## **📋 CHECKLIST DE VERIFICAÇÃO**

- [ ] Streamlit está instalado e funcionando
- [ ] Não há erros de importação
- [ ] Cache foi limpo
- [ ] Servidor foi reiniciado
- [ ] Botões estão no header (não só na aba Controles)
- [ ] CSS não está interferindo
- [ ] Versão do Streamlit é compatível

---

## **🎯 PRÓXIMOS PASSOS**

1. **Execute o teste simples:**
   ```bash
   streamlit run test_dashboard_simple.py
   ```

2. **Se funcionar, execute o dashboard principal:**
   ```bash
   streamlit run sniper_dashboard.py
   ```

3. **Verifique se os botões aparecem:**
   - No header (logo após as métricas)
   - Na aba Ranking
   - Na aba Controles

4. **Se ainda não aparecer:**
   - Limpe o cache: `streamlit cache clear`
   - Reinicie o servidor
   - Verifique a versão do Streamlit

---

## **💡 DICAS IMPORTANTES**

- **Botões estão no HEADER agora** (não só na aba Controles)
- **Use `use_container_width=True`** para botões responsivos
- **Verifique se não há erros** no console do Streamlit
- **Teste com dashboard simples** primeiro

---

**🎯 Os botões devem aparecer logo após as métricas de status no header do dashboard.**
