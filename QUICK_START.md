# 🚀 QUICK START GUIDE - ZERVE ARBITRAGE DETECTION SYSTEM

## ⚡ 5-MINUTE QUICK START

### Step 1: Navigate to Project Directory
```bash
cd /root/zerve-arbitrage-system
```

### Step 2: Run Demo Analysis (Recommended)
```bash
# Generate demo data with arbitrage opportunities
python3 demo_data_generator.py

# Run complete analysis
python3 demo_main.py

# View results
cat outputs/demo_analysis_summary.txt
```

### Step 3: View Detailed Results
```bash
# View arbitrage opportunities
cat outputs/demo_arbitrage_report_*.txt

# View risk analysis
cat outputs/demo_risk_report_*.txt

# View JSON results
cat outputs/demo_analysis_results_*.json
```

---

## 🎯 WHAT YOU'LL SEE

### Demo Results:
```
📊 DATA SUMMARY
- Total Markets: 80
- Platforms: 4
- Categories: 8

💰 OPPORTUNITIES FOUND
- Total: 15 opportunities
- Average Arbitrage: 73.21%
- Max Arbitrage: 103.49%
- Total Profit: $3,216.40

🏆 TOP 3 OPPORTUNITIES
1. Politics Arbitrage Event 10 - 75.91% arbitrage
2. Sports Arbitrage Event 4 - 66.91% arbitrage
3. Politics Arbitrage Event 2 - 103.49% arbitrage
```

---

## 🔧 OTHER RUNNING OPTIONS

### Option A: Start API Server
```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```
Then visit: http://localhost:8000/docs

### Option B: Start Dashboard
```bash
streamlit run dashboard.py
```
Then visit: http://localhost:8501

### Option C: Run Live Analysis
```bash
python3 main.py
```
(Requires API keys in config.py)

---

## 📁 KEY FILES

| File | Purpose |
|------|---------|
| `demo_main.py` | Demo analysis runner |
| `demo_data_generator.py` | Creates demo data |
| `main.py` | Live analysis runner |
| `api.py` | REST API server |
| `dashboard.py` | Web dashboard |
| `README.md` | Full documentation |

---

## 🎨 PROJECT STRUCTURE

```
zerve-arbitrage-system/
├── 📄 demo_main.py                    # ← Run this first!
├── 📄 demo_data_generator.py          # ← Creates demo data
├── 📄 main.py                         # Live analysis
├── 📄 api.py                          # REST API
├── 📄 dashboard.py                    # Web dashboard
├── 📁 data/                           # Market data
├── 📁 outputs/                        # Results (check this!)
└── 📁 models/                         # ML models
```

---

## 💡 TIPS

1. **Start with Demo:** Always run demo_main.py first to see the system in action
2. **Check Outputs:** All results are saved in the outputs/ directory
3. **Read Reports:** The .txt files contain human-readable summaries
4. **Explore JSON:** The .json files contain detailed data for analysis
5. **Try Dashboard:** The Streamlit dashboard provides visual insights

---

## 🐛 TROUBLESHOOTING

### Issue: "Module not found"
**Solution:** Install dependencies
```bash
pip install --break-system-packages pandas numpy scikit-learn fastapi uvicorn streamlit requests python-dotenv pydantic matplotlib seaborn plotly scipy
```

### Issue: "Demo data not found"
**Solution:** Generate demo data first
```bash
python3 demo_data_generator.py
```

### Issue: "API key required"
**Solution:** Use demo mode instead
```bash
python3 demo_main.py  # Doesn't require API keys
```

---

## 📊 WHAT THE SYSTEM DOES

1. **Collects Data** - Gathers market data from multiple platforms
2. **Detects Arbitrage** - Finds price differences across platforms
3. **Predicts Movements** - Uses ML to predict price changes
4. **Analyzes Risk** - Calculates risk scores for each opportunity
5. **Generates Reports** - Creates detailed analysis reports

---

## 🎯 NEXT STEPS

1. ✅ Run demo analysis (done!)
2. 📖 Read the full documentation in README.md
3. 🚀 Try the API server or dashboard
4. 📊 Explore the results in outputs/
5. 🏆 Submit to ZerveHack!

---

## 📞 NEED HELP?

- Check `README.md` for detailed documentation
- Review code comments for implementation details
- Look at `outputs/` for example results
- Run `demo_main.py` to see the system work

---

**Ready to go? Run this now:**

```bash
cd /root/zerve-arbitrage-system && python3 demo_main.py
```

**That's it! You'll see results in less than 1 second! 🚀**
