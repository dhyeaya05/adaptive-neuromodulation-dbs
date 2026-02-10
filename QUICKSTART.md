# 🚀 Quick Start Guide
## Get Running in 15 Minutes

---

## Step 1: Clone and Navigate
```bash
cd adaptive-neuromodulation-dbs
```

## Step 2: Setup Environment
```bash
# Run automated setup
python scripts/setup_project.py

# Or manual setup:
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Step 3: Launch First Notebook
```bash
# Activate environment if not already
source venv/bin/activate

# Start Jupyter
jupyter notebook notebooks/01_brain_model_setup.ipynb
```

## Step 4: Run Cells
- Execute each cell from top to bottom
- First run will download TVB data (~500 MB)
- Full notebook takes ~5-10 minutes

---

## 🎯 Expected Output

After running Notebook 1, you should have:
- ✅ Brain connectivity visualization
- ✅ Simulated beta oscillations (~20 Hz)
- ✅ Power spectral density plot
- ✅ Beta power time series
- ✅ Baseline data saved

**Look for this in plots:**
- Peak in power spectrum at 13-30 Hz (beta band)
- Oscillatory activity in time series
- Elevated beta power throughout simulation

---

## 🔧 Troubleshooting

### TVB Installation Issues
```bash
# Try conda instead
conda create -n neuro python=3.9
conda activate neuro
pip install tvb-library tvb-data
```

### Import Errors
```bash
# Ensure you're in correct environment
which python  # Should show venv/bin/python

# Reinstall if needed
pip install -r requirements.txt --force-reinstall
```

### Slow Simulation
Reduce simulation time in notebook:
```python
SIMULATION_LENGTH = 5000  # Change from 10000 to 5000 (5 seconds)
```

---

## 📁 File Structure After Setup

```
adaptive-neuromodulation-dbs/
├── venv/                          # Virtual environment
├── data/
│   └── simulation_results/        # Generated plots here
├── notebooks/
│   └── 01_brain_model_setup.ipynb # Start here!
├── src/                           # Your Python modules
└── docs/                          # Documentation
```

---

## ⏭️ Next Steps

1. **Day 1 Morning**: Complete Notebook 1 (brain model)
2. **Day 1 Afternoon**: Create Notebook 2 (PID controller)
3. **Day 2**: Advanced control + ML
4. **Day 3**: Polish + portfolio materials

See `docs/PROJECT_ROADMAP.md` for detailed timeline.

---

## 💡 Pro Tips

- **Save often**: Notebooks auto-save, but use Ctrl+S
- **Clear outputs**: Before committing, `Cell → All Output → Clear`
- **Take screenshots**: Every good plot → save as PNG
- **Comment code**: Future you will thank you
- **Git commit frequently**: After each notebook section

---

## 🆘 Getting Help

**Issues?**
1. Check `docs/PROJECT_ROADMAP.md` for troubleshooting
2. Review TVB documentation: https://docs.thevirtualbrain.org/
3. Check GitHub Issues for similar problems

**Working?**
Congrats! You're on your way to an amazing portfolio project! 🎉

Continue to Notebook 2 to implement your first controller.
