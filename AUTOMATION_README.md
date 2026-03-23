# EnergieRapport Automatisering

## Overzicht

Dit project implementeert een cost-effectieve automatisering voor het dagelijks updaten van het EnergieRapport met een hybride aanpak:
- **Dagelijkse updates** (19:00 CET): Prijsdata zonder AI
- **Wekelijkse analyse** (Zondag 20:00 CET): Volledige AI-gedreven geopolitieke analyse
- **Crisis-detectie**: Automatische AI-analyse bij prijsschokken >10%

## Architectuur

### Components

```
.github/workflows/
└── energy-report.yml          # GitHub Actions workflow

scripts/
├── data_collector.py          # Verzamelt marktdata van meerdere bronnen
├── crisis_detector.py         # Detecteert significante prijsschokken
├── ai_analyzer.py             # Claude AI voor geopolitieke analyse
└── report_updater.py          # Update JSX en HTML bestanden

data/                          # Gegenereerde data (niet in git)
├── latest_prices.json         # Huidige prijzen
├── previous_prices.json       # Vorige dag voor vergelijking
├── crisis_report.json         # Crisis detectie resultaten
└── ai_analysis.json           # AI analyse output
```

### Workflow

1. **Data Collection** (`data_collector.py`)
   - Verzamelt TTF, Belpex, EU Storage, Brent van meerdere bronnen
   - Verifieert data met ±2% threshold tussen bronnen
   - Slaat op naar `data/latest_prices.json`

2. **Crisis Detection** (`crisis_detector.py`)
   - Vergelijkt huidige met vorige dag prijzen
   - Detecteert schokken >10% voor TTF, Belpex, Brent
   - Detecteert storage wijzigingen >5%
   - Triggert AI-analyse bij crisis

3. **AI Analysis** (`ai_analyzer.py`)
   - Gebruikt Claude Haiku (meest cost-effectief)
   - Analyseert marktdynamiek en geopolitiek
   - Genereert consumentenadvies
   - Alleen bij weekly run of crisis

4. **Report Update** (`report_updater.py`)
   - Update `src/EnergieRapport.jsx`
   - Update `public/offline.html`
   - Synchroniseert KPIs, grafieken, datums

## Setup

### 1. GitHub Secrets Configureren

Voeg toe in GitHub repository settings → Secrets and variables → Actions:

```
ANTHROPIC_API_KEY=sk-ant-...
```

### 2. Lokale Development

```bash
# Installeer dependencies
pip install -r requirements.txt

# Test data collection
python scripts/data_collector.py

# Test crisis detection
python scripts/crisis_detector.py

# Test AI analysis (vereist API key)
export ANTHROPIC_API_KEY=sk-ant-...
python scripts/ai_analyzer.py

# Test report update
python scripts/report_updater.py
```

### 3. Manuele Trigger

Via GitHub Actions UI:
1. Ga naar Actions tab
2. Selecteer "EnergieRapport Auto-Update"
3. Klik "Run workflow"
4. Optioneel: enable "Force AI analysis"

## Kosten Analyse

### GitHub Actions
- **Gratis**: 2000 minuten/maand voor private repos
- **Gebruik**: ~5 min/dag × 30 dagen = 150 min/maand
- **Kosten**: €0

### Claude API (Haiku)
- **Input**: $0.25 per 1M tokens
- **Output**: $1.25 per 1M tokens
- **Wekelijks gebruik**: ~2000 tokens input + 1000 tokens output
- **Maandelijkse kosten**: ~$0.50 + ~$1.25 = **~$1.75/maand**

### Crisis Triggers
- Gemiddeld 1-2× per maand extra
- **Extra kosten**: ~$0.50/maand

**Totaal: ~€2-3/maand** voor volledige automatisering

## Data Bronnen

### TTF Aardgas
- ICE Endex API
- Trading Economics
- Investing.com

### Belpex Elektriciteit
- EPEX SPOT
- ENTSO-E Transparency Platform
- dayaheadmarket.eu

### EU Gas Storage
- AGSI+ (Gas Infrastructure Europe)
- Bruegel
- Energy Dashboard

### Brent Crude
- EIA API
- Trading Economics
- Yahoo Finance

## Monitoring

### Logs
GitHub Actions logs tonen:
- Data collection status
- Crisis detection results
- AI analysis triggers
- Update success/failure

### Notificaties
Bij failure:
- GitHub Actions email notificatie
- Workflow status badge in README

## Troubleshooting

### Data Collection Fails
```bash
# Check bronnen handmatig
python scripts/data_collector.py

# Bekijk logs
cat data/latest_prices.json
```

### AI Analysis Fails
```bash
# Verify API key
echo $ANTHROPIC_API_KEY

# Test API connectivity
python scripts/ai_analyzer.py
```

### Report Update Fails
```bash
# Check file permissions
ls -la src/EnergieRapport.jsx public/offline.html

# Test update logic
python scripts/report_updater.py
```

## Development Workflow

### Nieuwe Features
```bash
# Maak feature branch
git checkout -b feature/new-data-source

# Implementeer wijzigingen
# Test lokaal
python scripts/data_collector.py

# Commit en push
git add .
git commit -m "Add new data source"
git push origin feature/new-data-source

# Create PR naar main
```

### Testing
```bash
# Test volledige workflow lokaal
./scripts/test_workflow.sh

# Test individuele componenten
pytest tests/
```

## Toekomstige Verbeteringen

- [ ] Implementeer echte API integraties voor data bronnen
- [ ] Voeg unit tests toe voor alle scripts
- [ ] Implementeer data caching voor rate limiting
- [ ] Voeg Slack/Discord notificaties toe
- [ ] Creëer dashboard voor monitoring
- [ ] Implementeer A/B testing voor AI prompts
- [ ] Voeg historische data analyse toe

## Support

Voor vragen of problemen:
1. Check GitHub Actions logs
2. Review `data/*.json` bestanden
3. Test scripts lokaal met debug logging
4. Open GitHub issue met logs

## License

Zie hoofdproject LICENSE
