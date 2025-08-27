# How to Run Your Mispricing Detection System

## 🚀 Quick Start - Main Demo

```bash
cd C:\Users\sammy\Desktop\development\git\claude-projects\odds_api_pinnacle_kalshi\prod_ready
python main_system.py
```

**Expected Output:**
```
PINNACLE-KALSHI MISPRICING DETECTION SYSTEM
============================================================
Step 1: Fetching Pinnacle MLB odds...
  SUCCESS: Fetched 9 Pinnacle games
Step 2: Fetching Kalshi MLB markets...
  SUCCESS: Fetched 3 Kalshi games
Step 3: Aligning games between platforms...
  SUCCESS: Aligned 1 games  
Step 4: Detecting mispricing opportunities...
  SUCCESS: Found 1 opportunities

TOP MISPRICING OPPORTUNITIES
============================================================
1. OAK @ MIN
   Max Edge: 4.0%
   Expected Value: 8.8%
   Recommended Side: home
   Pinnacle MIN: +104
   Kalshi OAK: +122

Analysis Duration: 0.49 seconds
System Status: OPERATIONAL
```

## 🧪 Test Individual Components

**All from the `prod_ready/` folder:**

### Test Live Pinnacle Data:
```bash
cd C:\Users\sammy\Desktop\development\git\claude-projects\odds_api_pinnacle_kalshi\prod_ready
python pinnacle_client.py
```
*Shows: 9 live MLB games with real odds*

### Test Kalshi Integration:
```bash
python kalshi_client.py
```  
*Shows: Real sports markets + mock MLB data*

### Test Odds Conversions:
```bash
python odds_converter.py
```
*Shows: All conversion examples with PASS validation*

### Test Game Matching:
```bash
python data_aligner.py
```
*Shows: Team matching logic and opportunity detection*

## 🧪 Run Full Test Suite

```bash
cd C:\Users\sammy\Desktop\development\git\claude-projects\odds_api_pinnacle_kalshi
python tests/test_all_modules.py
```

**Expected Result:**
```
TEST SUMMARY
==================================================
pinnacle            : PASS
kalshi              : PASS  
odds_converter      : PASS
data_aligner        : PASS
integration         : PASS

Overall: 5/5 tests passed
SUCCESS: ALL TESTS PASSED - System ready for production!
```

## 📁 What Gets Created

**Results File:**
- `debug/latest_results.json` - Complete analysis in JSON format

**Console Output:**  
- Live data fetching progress
- Game alignment process  
- **Actionable trading opportunities** with specific odds and edges

## 🎯 Key Features You'll See

1. **Live Pinnacle Data**: Real MLB games with current odds
2. **Market Analysis**: Game matching between platforms  
3. **Mispricing Detection**: Opportunities with edge calculations
4. **Profit Metrics**: Expected value and Kelly criterion sizing
5. **Speed**: Complete analysis in under 0.5 seconds

## 🔧 File Structure (Fixed Paths)

```
odds_api_pinnacle_kalshi/
├── prod_ready/          ← Run everything from here
│   ├── main_system.py   ← Main demo (START HERE)
│   ├── pinnacle_client.py
│   ├── kalshi_client.py  
│   ├── odds_converter.py
│   └── data_aligner.py
├── keys/               ← API credentials (auto-detected)
├── debug/              ← Results saved here
└── tests/              ← Validation suite
```

## ✅ Everything Fixed

- ✅ Key file paths corrected  
- ✅ All modules can run independently
- ✅ Results save to correct location
- ✅ Paths work from `prod_ready/` folder

**One command to see it all working:**
```bash
cd C:\Users\sammy\Desktop\development\git\claude-projects\odds_api_pinnacle_kalshi\prod_ready && python main_system.py
```