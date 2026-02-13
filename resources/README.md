# Resources — structural-bridge-via-uniqueness-theorems

> Вводные данные для исследования.

---

## Reference Papers

### Primary (используются в цепочках доказательства)

| Paper | Author(s) | Used For |
|-------|-----------|----------|
| arXiv:2008.01540 | Vanchurin (2020) | "The World as a Neural Network" — целевые уравнения моста |
| arXiv:2012.15821 | Vanchurin (2021) | "Towards a Theory of Machine Learning" — Eq. 3.4 динамика |
| Gorard (2020) | Jonathan Gorard | CI → диффеоморфизмная симметрия (основа цепочки Лавлока) |
| Lovelock (1971) | David Lovelock | Единственность тензора Эйнштейна в D >= 4 |
| Amari (1998) | Shun-ichi Amari | Единственность натурального градиента |
| Chiribella et al. | Chiribella, D'Ariano, Perinotti | Информационный вывод квантовой теории |

### Secondary (контекст и проверка)

| Paper | Used For |
|-------|----------|
| Shannon rate-distortion | Нижняя граница потерь обучения |
| Ollivier-Ricci curvature | Проверка кривизны на дискретных графах |
| Conant-Ashby (good regulator) | Обоснование персистентности наблюдателя |

---

## Computational Resources

```yaml
python_packages:
  - numpy: "Линейная алгебра, матричные операции"
  - scipy: "Оптимизация, собственные значения"
  - networkx: "Графовые структуры (мультивей, каузальные графы)"
  - matplotlib: "Визуализация результатов"

wolfram_optional:
  - "Wolfram Engine (бесплатно для разработчиков)"
  - "SetReplace package (ResourceFunction)"
  - "Для экспериментов на настоящих гиперграфах"
```

---

## Previous Session Data

```yaml
location: "experience/insights/dialogue-analysis-10-sessions.md"
content: "Полный анализ 10+ AI-assisted research sessions"
includes:
  - "10 ключевых находок (3 критических, 4 важных, 1 средняя)"
  - "5 честных провалов"
  - "Структура решения (3 цепочки + предсказание + тесты)"
  - "Приоритеты дальнейших действий"
```

---

## How to Add Resources

```bash
# PDF статьи — сохранять в resources/papers/
mkdir -p papers && cp ~/Downloads/paper.pdf papers/

# Внешний код — submodule
git submodule add https://github.com/... resources/external-code/

# Данные экспериментов — output/, не resources/
# resources/ = INPUT, output/ = RESULTS
```
