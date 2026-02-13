# CLAUDE.md — structural-bridge-via-uniqueness-theorems

> Формальный мост между космологическими программами Wolfram и Vanchurin.
> Организовано по @uu Knowledge Pyramid (minimal).

---

## IDENTITY

```yaml
project: "structural-bridge-via-uniqueness-theorems"
short_name: "wolfram-vanchurin-bridge"
type: theoretical-physics-research
level: L2-project

purpose: |
  Формальное доказательство структурного моста между космологическими
  программами Wolfram и Vanchurin через теоремы единственности.
  Из одной аксиомы (каузальная инвариантность) вывести гравитацию,
  квантовую механику, динамику обучения, стрелу времени и метрическое тождество.

git:
  org: "github.com/ProVibecodium"
  account: "ProVibecodium"
  repo: "physics-cosmo-bridge"
```

---

## POSITION

```
PhysicsResearch/
└── cosmological-unification/
    └── structural-bridge-via-uniqueness-theorems/    <- ТЫ ЗДЕСЬ
        ├── CLAUDE.md               # Этот файл
        ├── vos/                    # Спецификация исследования
        │   ├── value-transformation.md
        │   ├── scope-boundaries.md
        │   └── integration-contract.md
        ├── resources/              # Статьи, ссылки, внешние данные
        │   └── README.md
        ├── experience/             # Накопленные инсайты (10+ сессий)
        │   ├── insights/
        │   └── patterns/
        ├── src/                    # Код экспериментов (Python, Wolfram)
        └── output/                 # Результаты, графики, черновики
```

---

## KEY FILES

| Приоритет | Файл | Когда читать |
|-----------|------|--------------|
| **1** | `vos/value-transformation.md` | ЧТО доказываем и ЗАЧЕМ |
| **2** | `vos/scope-boundaries.md` | Границы: IN/OUT |
| **3** | `experience/insights/dialogue-analysis-10-sessions.md` | Полный анализ 10+ сессий |
| **4** | `vos/integration-contract.md` | Что гарантируем (deliverables) |
| **5** | `resources/README.md` | Описание источников |
| **6** | `src/` | Код экспериментов |

---

## RESEARCH SUMMARY

```yaml
thesis: |
  Каузальная инвариантность (CI) Вольфрама через теоремы Лавлока и Амари
  однозначно фиксирует ключевые структуры Ванчурина.
  Из одной аксиомы выведены: гравитация, КМ, динамика обучения,
  стрела времени, метрическое тождество Fisher = Riemann.

proof_chains:
  lovelock_chain: |
    CI → диффеоморфизмная симметрия (Горард 2020) →
    теорема Лавлока (1971) → единственность тензора Онзагера Ванчурина (Eq. 93)
    Статус: ДОКАЗАНА (1 допущение: континуальный предел)

  amari_chain: |
    персистентность наблюдателя → Конант-Эшби →
    Fisher-информация → Амари (1998) → единственность Eq. 3.4 Ванчурина
    Статус: ДОКАЗАНА (2 допущения: континуальный предел + персистентность)

  quantum_sector: |
    CI → 5/5 аксиом Кирибеллы выполняются в мультивее:
    1. Causality: CI → DAG → нет обратной причинности
    2. Perfect distinguishability: G = A^T A положительно определена
    3. Ideal compression: rate-distortion, наблюдение = сжатие
    4. Local distinguishability: 1134/1134 null_dim = 0
    5. Purification: мультивей = compact structure (eta, epsilon)
    Статус: ДОКАЗАНА

  dirac_prediction: |
    M+M- ~ alpha*M^2 через ориентацию переходов по descendants.
    Ошибка 1.2-15% на toy models. Единственное предсказание,
    которого НЕТ ни у Вольфрама, ни у Ванчурина.
    Статус: ПРЕДВАРИТЕЛЬНО (нужна проверка на гиперграфах)

  arrow_of_time: |
    dL/dt = -g^{ij}(d_i L)(d_j L) <= 0 (g положительно определена)
    + каузальный граф ацикличен (из CI).
    Необратимость — структурная необходимость, не зависит от начальных условий.
    Статус: ДОКАЗАНА

falsifiable_tests:
  - "CI-breaking test: forced ordering p = 0.0215 (значимо)"
  - "Rate-distortion: rho = 0.47, p = 0.0002"
  - "4 фальсифицируемых предсказания сформулированы"

honest_failures:
  - "Конфлюэнтность ≠ унитарность (отклонение 0.67-1.0)"
  - "CIC = log_2(3) не подтвердилась (H ~ 1.22, не 1.585)"
  - "d_eff ~ 1.6 — артефакт кодирования, не фундаментальное свойство"
  - "Спектральная размерность d_s ~ 2, не 1.6"
  - "Lambda = rate-distortion не константа (от 2.4 до 1955)"

originality_assessment: |
  ~60% работы — переоткрытие и систематизация известного.
  Реально новое:
  - Связка через Лавлок (никто не применял)
  - G = A^T A для Local Distinguishability (оригинальная конструкция)
  - M+M- ~ alpha*M^2 через descendants-ориентацию
  - d_eff = артефакт (честный негативный результат)
```

---

## TASK SUMMARY

```yaml
Goal: "Публикуемый результат: формальный мост Wolfram <-> Vanchurin"

Priority_1_immediate:
  - "Отправить заметку Ванчурину с цепочкой Лавлока"
  - "Ответ на его вопрос из arXiv:2008.01540: 'can symmetries be derived from first principles?'"

Priority_1_technical:
  - "Континуальный предел: проверить kappa != 0 на настоящих гиперграфах"
  - "Дирак на гиперграфах: M+M- ~ alpha*M^2 с естественной ориентацией гиперрёбер"

Priority_2:
  - "arXiv preprint (фиксация приоритета)"
  - "Публикация в рецензируемом журнале"
  - "Механизм K ~ N^alpha (alpha ~ 0.76, корреляция с конфлюэнтностью r = -0.68)"
```

---

## RESOURCES

```yaml
key_papers:
  - "Vanchurin: arXiv:2008.01540, arXiv:2012.15821"
  - "Gorard 2020: Relativistic Properties of Wolfram Model"
  - "Lovelock 1971: Einstein Tensor uniqueness"
  - "Amari 1998: Natural Gradient"
  - "Chiribella et al: Informational derivation of QM"

computational_tools:
  - "Python (numpy, scipy, networkx) для числовых экспериментов"
  - "Wolfram Engine + SetReplace для гиперграфов"

previous_sessions:
  count: "10+ AI-assisted research sessions"
  stored: "experience/insights/dialogue-analysis-10-sessions.md"
```

---

## PROTOCOLS

```yaml
При работе над проектом:
  1. Читай vos/ для понимания целей и границ
  2. Проверяй experience/ — что уже доказано, что провалилось
  3. Код в src/, результаты в output/
  4. Новые инсайты (положительные И отрицательные) в experience/insights/
  5. Черновики статей в output/drafts/

При вычислительном эксперименте:
  1. Формулируй гипотезу ПЕРЕД запуском
  2. Документируй параметры и результат
  3. Фиксируй негативные результаты наравне с позитивными
  4. Проверяй зависимость от кодирования/представления

При контакте с авторами:
  1. Подготовь краткую заметку (1-2 страницы)
  2. Сфокусируйся на конкретном вопросе из их работы
  3. Покажи что знаком с их результатами
  4. Будь честен насчёт допущений и ограничений

При коммитах:
  - Conventional commits (feat:, fix:, docs:)
  - Reference finding/theorem in message
```

---

## NAVIGATION

```bash
# К VOS
cat vos/value-transformation.md

# К ресурсам
ls resources/

# К родительской проблематике
cd ../ && cat CLAUDE.md

# К бенефициару
cd ../../ && cat CLAUDE.md

# Запуск с PE
# cw--pe3 ~/Projects/PhysicsResearch/cosmological-unification/structural-bridge-via-uniqueness-theorems/
```

---

## CURRENT STATE

```yaml
status: "research-in-progress"
created: 2026-02-13

completed:
  - "10+ AI-assisted research sessions"
  - "Цепочка Лавлока: CI → Лавлок → единственность Eq. 93 (доказана)"
  - "Цепочка Амари: персистентность → Амари → единственность Eq. 3.4 (доказана)"
  - "Квантовый сектор: 5/5 аксиом Кирибеллы (доказаны)"
  - "Стрела времени: dL/dt <= 0 (доказана)"
  - "Fisher = Riemann (доказано из Лавлока)"
  - "CI-breaking test: p = 0.0215 (значимо)"
  - "5 честных провалов задокументированы"
  - "Дирак M+M- ~ alpha*M^2 (предварительно, toy models)"

next:
  - "Отправить заметку Ванчурину"
  - "Континуальный предел на гиперграфах"
  - "Дирак на настоящих гиперграфах"
  - "arXiv preprint"
  - "Организация кода экспериментов в src/"
```

---

## META

```yaml
follows: "@uu Knowledge Pyramid (minimal)"
parent_hierarchy:
  - PhysicsResearch (beneficiary)
  - cosmological-unification (problematics)
  - this project
```

---

*structural-bridge-via-uniqueness-theorems: формальный мост Wolfram-Vanchurin через теоремы единственности.*
