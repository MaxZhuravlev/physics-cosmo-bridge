# Как Запустить Wolfram Тесты - Простая Инструкция

**Цель**: Получить spatial hypergraph данные
**Время**: 5-10 минут
**Награда**: Theorems CONDITIONAL → UNCONDITIONAL!

---

## КОМАНДЫ (Copy-Paste в Terminal)

```bash
cd /Users/Max_1/Projects/PhysicsResearch/cosmological-unification/structural-bridge-via-uniqueness-theorems

# TEST 1: Spatial Ollivier-Ricci (КРИТИЧНЫЙ!)
wolframscript -file src/SPATIAL_CRITICAL_TEST.wl | tee output/spatial_results.txt

# TEST 2: Spatial Dirac (bonus)
wolframscript -file src/SPATIAL_DIRAC_TEST.wl | tee output/dirac_results.txt
```

---

## ЧТО СМОТРЕТЬ

### TEST 1: Spatial Ricci (ГЛАВНЫЙ)

Ищите в выводе:
```
Average curvature: 0.XXX
```

**КРИТЕРИИ**:
- κ > 0.1 → ✅ CONFIRMED (continual limit empirically proven!)
- κ > 0.01 → ⚠️  PARTIAL (some evidence)
- κ ≈ 0 → ❌ FLAT (similar to toy models)

### TEST 2: Spatial Dirac

Ищите:
```
Alpha: 0.XXX
Error: 0.XXX
```

**КРИТЕРИИ**:
- α ≠ 0 AND error < 0.30 → ✅ NEW PHYSICS!
- α = 0 → ❌ DEGENERATE (similar to toy models)

---

## ПОСЛЕ ЗАПУСКА

Скопируйте output и вставьте в Claude Code:

```bash
# Вариант 1: Показать мне файл
cat output/spatial_results.txt

# Вариант 2: Auto-analyze
source venv/bin/activate
python src/analyze_wolfram_output.py output/spatial_results.txt
```

Я проанализирую и обновлю:
- Theorem statuses
- Publication draft
- Final assessment

---

## ЕСЛИ ЧТО-ТО НЕ РАБОТАЕТ

Просто скопируйте весь output (даже если с ошибками) - я разберусь!

---

**Удачи! Это может быть решающий тест!**

κ ≠ 0 на spatial graphs = все theorems становятся unconditional.
