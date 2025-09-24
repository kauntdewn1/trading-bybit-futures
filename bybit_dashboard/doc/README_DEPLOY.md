# 🥷 Bybit Futures Trading Dashboard - Deploy

## 🚀 Deploy Rápido

### Streamlit Cloud (Recomendado)
1. Faça push para GitHub
2. Acesse [share.streamlit.io](https://share.streamlit.io)
3. Conecte com GitHub
4. Selecione este repositório
5. Main file: `app.py`
6. Deploy!

### Heroku
```bash
# Criar Procfile
echo "web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0" > Procfile

# Deploy
git add .
git commit -m "Deploy futures dashboard"
git push heroku main
```

### Railway
1. Conecte com GitHub
2. Selecione este repositório
3. Deploy automático

## 🔧 Configuração

### Variáveis de Ambiente
Crie arquivo `.env` com:
```
API_KEY=sua_api_key
API_SECRET=sua_api_secret
TELEGRAM_TOKEN=seu_telegram_token
```

### Permissões da API
- Ative Futures Trading na Bybit
- Configure whitelist de IP (opcional)

## 📊 Funcionalidades

- ✅ Dashboard em tempo real
- ✅ Análise de Futures
- ✅ Indicadores técnicos
- ✅ Gestão de risco
- ✅ Bot do Telegram
- ✅ Node NΞØ integrado

## ⚠️ Avisos

- Teste sempre em testnet primeiro
- Use gestão de risco adequada
- Nunca arrisque mais do que pode perder
