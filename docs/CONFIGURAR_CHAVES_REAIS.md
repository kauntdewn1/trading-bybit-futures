# 🔑 COMO CONFIGURAR CHAVES REAIS - SNIPER NEØ

## **📋 SITUAÇÃO ATUAL**

### **⚠️ Status Atual**

- **Sistema**: Funcionando com bypass temporário
- **Chaves**: Usando chaves de bypass (não reais)
- **Modo**: TESTNET (seguro)
- **Status**: Pronto para configurar chaves reais

## **🔑 COMO OBTER SUAS CHAVES DE TESTNET**

### **1. Acesse o Bybit Testnet**

- **URL**: https://testnet.bybit.com
- **Crie uma conta** ou faça login

### **2. Crie uma API Key**

- Vá em: **Account** → **API Management**
- Clique em: **Create New Key**
- Configure:
  - **Label**: `SNIPER_NEØ_TEST`
  - **Permissions**: `Read`, `Trade`
  - **IP Restriction**: (opcional)

### **3. Copie as Chaves**

- **API Key**: Copie a chave gerada
- **API Secret**: Copie o secret gerado

## **⚙️ COMO CONFIGURAR NO SISTEMA**

### **Método 1: Script Automático (Recomendado)**

1. **Abra o arquivo**: `set_real_keys.py`
2. **Edite as linhas**:
   ```python
   API_KEY = "SUA_API_KEY_AQUI"        # Substitua pela sua API Key
   API_SECRET = "SUA_API_SECRET_AQUI"   # Substitua pela sua API Secret
   TELEGRAM_TOKEN = "SEU_TELEGRAM_TOKEN_AQUI"  # Opcional
   ```
3. **Execute**: `python set_real_keys.py`

### **Método 2: Edição Direta do .env**

1. **Abra o arquivo**: `.env`
2. **Substitua as linhas**:
   ```env
   API_KEY=bypass_testnet_api_key_12345678901234567890
   API_SECRET=bypass_testnet_secret_12345678901234567890
   ```
   Por:
   ```env
   API_KEY=SUA_API_KEY_REAL_AQUI
   API_SECRET=SUA_API_SECRET_REAL_AQUI
   ```

## **🧪 TESTANDO A CONFIGURAÇÃO**

### **1. Teste de Segurança**
```bash
python test_security.py
```

### **2. Teste de Conexão**
```bash
python sniper_dashboard.py
```

### **3. Teste do Telegram**
```bash
python telegram_sniper_enhanced.py
```

## **✅ RESULTADO ESPERADO**

### **Com Chaves Reais**
- ✅ Conexão estabelecida com sucesso
- ✅ Sistema funcionando sem bypass
- ✅ Logs de segurança normais
- ✅ Operações em TESTNET funcionando

### **Sem Chaves Reais**
- ❌ Erro de conexão
- ⚠️ Bypass temporário ativo
- ⚠️ Logs de bypass

## **⚠️ AVISOS IMPORTANTES**

### **🔒 Segurança**
- **Use APENAS chaves de TESTNET**
- **NUNCA use chaves de produção**
- **Mantenha suas chaves seguras**
- **NÃO compartilhe arquivos .env**

### **🧪 Teste**
- **Teste sempre em TESTNET primeiro**
- **Verifique se as operações são simuladas**
- **Confirme que não há dinheiro real envolvido**

## **🚀 PRÓXIMOS PASSOS**

### **1. Configure suas chaves**
- Siga os passos acima
- Use o script `set_real_keys.py`

### **2. Teste o sistema**
- Execute `python test_security.py`
- Execute `python sniper_dashboard.py`

### **3. Desenvolva com segurança**
- Sistema funcionando com chaves reais
- Operações em TESTNET
- Logs de segurança ativos

## **📞 SUPORTE**

Se tiver problemas:
1. Verifique se as chaves estão corretas
2. Confirme que são chaves de TESTNET
3. Execute `python test_security.py`
4. Consulte os logs de segurança

---

**🎯 OBJETIVO: Configurar chaves reais de TESTNET para desenvolvimento seguro!**
