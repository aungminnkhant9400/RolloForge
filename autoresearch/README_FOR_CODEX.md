# AutoResearch Framework for nnU-Net

Karpathy-style autoresearch for hyperparameter optimization on GPU.

## What This Does

1. **Generate** random hyperparameter configurations
2. **Train** nnU-Net for N epochs (quick experiments)
3. **Evaluate** validation Dice score
4. **Log** all results
5. **Iterate** overnight, keeping best configs

## Files

- `autoresearch.py` - Main framework (I wrote this)
- `config.yaml` - Hyperparameter search space (I wrote this)
- `experiments.json` - Auto-generated results log
- `best_config.json` - Auto-generated best configuration

## Usage

```bash
# On GPU server (inside ROLLO container)
cd /workspace/autoresearch
python autoresearch.py --config config.yaml --iterations 10
```

## What Codex Should Implement

### 1. Bayesian Optimization (Priority: HIGH)
Replace random search with Bayesian optimization using `scikit-optimize`:

```python
from skopt import gp_minimize

# Use Gaussian Process to model performance landscape
# Suggest next hyperparameters based on previous results
# More efficient than random search
```

### 2. nnU-Net Integration (Priority: HIGH)
- Replace placeholder `_build_command()` with actual nnU-Net API
- Parse actual nnU-Net output files (progress.png, training_log.txt)
- Extract real Dice scores from validation

### 3. Parallel GPU Support (Priority: MEDIUM)
Run multiple experiments simultaneously:
```python
# If 8 GPUs available, run 8 experiments in parallel
# Each GPU gets one configuration
# 8x speedup
```

### 4. Visualization Dashboard (Priority: MEDIUM)
Generate HTML report with:
- Learning curves
- Hyperparameter importance
- Best config visualization

### 5. Resume Capability (Priority: LOW)
If interrupted, resume from last checkpoint instead of starting over.

## For Codex

**Task:** Pick one item above and implement it.

**Start with:** Bayesian optimization (most impact)

**Files to modify:**
- `autoresearch.py` - Add BayesianOptimizer class
- Keep my structure, enhance with new capabilities

**Test:** Run with 3 iterations to verify works

## Example Output

```
[1/10] Running experiment: exp_20250327_210001_1234
Hyperparameters: {'learning_rate': 0.0015, 'batch_size': 2, ...}
Status: success
Metrics: {'dice': 0.7234, 'loss': 0.4456}
Duration: 450.2s

Current Top 3:
  1. exp_20250327_210001_1234: Dice=0.7234
  2. ...
  3. ...
```
