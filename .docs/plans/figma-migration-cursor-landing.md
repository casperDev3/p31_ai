# План міграції лендингу в Figma

**Джерело:** `landings/cursor-generated-index.html`
**Ціль:** відтворити лендинг у Figma як design-ready макет (токени → компоненти → секції → адаптив)
**Підхід:** code → design через Figma MCP (skills `figma-use`, `figma-generate-design`, `figma-generate-library`)
**Дата:** 2026-06-20

---

## 0. Контекст і передумови

- Лендинг — односторінковий dark-theme портфоліо (Ігор Лялюк / RED Solutions), один HTML-файл з inline `<style>` і `<script>`.
- Уся візуальна система побудована на CSS-змінних (`:root`) — це готова мапа design tokens.
- Шрифти: **DM Sans** (400–800) і **JetBrains Mono** (400, 500) з Google Fonts.
- 8 логічних секцій + sticky-навігація + мобільний drawer.
- Адаптив на 3 брейкпоінтах: `900px`, `768px`, `560px`.

**Перед стартом перевірити:**
- [ ] Figma MCP підключено (`whoami` повертає акаунт).
- [ ] Є цільовий Figma-файл або створити новий (skill `figma-create-new-file`).
- [ ] DM Sans і JetBrains Mono доступні в Figma (інакше enable через Google Fonts у файлі).

---

## 1. Інвентаризація design tokens

Витягнути з `:root` у Figma Variables (collection `tokens`, режими: один `Default`, dark).

### 1.1 Кольори (collection `color`)
| Token | Значення | Призначення |
|---|---|---|
| `bg` | `#0a0c10` | фон сторінки |
| `surface` | `#12151c` | картки, бейджі, кнопки-ghost |
| `surface-2` | `#181c26` | вкладені поверхні (lang-chip, project-links) |
| `border` | `#2a3140` | рамки |
| `text` | `#eef0f4` | основний текст |
| `muted` | `#9aa3b5` | другорядний текст |
| `accent` | `#3dd6c3` | акцент (бірюзовий) |
| `accent-dim` | `#3dd6c320` | акцент 12.5% alpha |
| `warm` | `#e8b84a` | теплий акцент (жовтий) |

> Прозорі похідні (`#3dd6c344`, `#e8b84a18`, `#0a0c10cc` тощо) задати як окремі токени або як fill з opacity на місці використання.

### 1.2 Spacing (collection `space`, тип number)
`space-1=8`, `space-2=16`, `space-3=24`, `space-4=32`, `space-5=48`, `space-6=64`

### 1.3 Radius
`radius=12`, `radius-lg=16`, `radius-pill=999`

### 1.4 Розміри/типографіка
- `max=1100` (контентна ширина), `nav-h=72`
- Текстові стилі (Figma text styles):
  - `H1` — DM Sans 800, ~52px (clamp 2.2–3.25rem), line-height 1.1, letter-spacing -0.03em
  - `Section label` — JetBrains Mono 500, 11.5px, uppercase, letter-spacing 0.14em, колір accent
  - `Body` — DM Sans 400, 16px, line-height 1.6
  - `Body-muted` — DM Sans 400, 16px, колір muted
  - `Card title` — DM Sans 700, 17px
  - `Mono small` — JetBrains Mono 500, 11–13px (badge / year / stars / lang-chip)

**Чек:** [ ] усі токени створені і прив'язані; жодного хардкоду кольору в наступних кроках.

---

## 2. Налаштування файлу та сітки

- [ ] Створити сторінки Figma: `01 Tokens`, `02 Components`, `03 Desktop`, `04 Responsive`.
- [ ] Базовий desktop-фрейм: ширина 1440, контент-контейнер 1100 по центру, паддінги `space-3` (24) по боках.
- [ ] Layout grid на контент-контейнері: max-width 1100, центрований.
- [ ] Глобальний фон: `bg` + два radial-gradient (accent зверху-зліва, warm знизу-справа) + ледь помітний noise-overlay (opacity ~3.5%) — як декоративний шар поверх фону.

---

## 3. Побудова компонентів (сторінка `02 Components`)

Будувати з auto-layout і прив'язкою до токенів. Для кожного — варіанти (properties).

1. **Badge** — pill, JetBrains Mono uppercase. Variants: `default`, `accent`, `warm`.
2. **Button** — auto-layout, min-height 44. Variants: `primary` (fill accent, text bg), `ghost` (border, transparent). + hover-стан окремим варіантом за бажанням.
3. **Skill chip** — surface + border, radius 12, min-height 44.
4. **Stat card** — value (велике) + label (mono uppercase), center, surface+border.
5. **Nav link** — desktop-варіант (muted→text hover) і drawer-варіант (більший, з border).
6. **Section label** — mono-заголовок + 32×2 риска-роздільник знизу.
7. **About card** — surface, radius-lg, h3 + p.
8. **Lang chip** — mono, surface-2, колір warm.
9. **Project link** — кнопка-посилання (surface-2), варіант з `↗` для зовнішніх.
10. **Project card** — головний композитний компонент:
    - Slots: pinned-мітка (опц.), header (title + stars/lang-chip), description, project-links.
    - Variants: `default`, `featured` (займає 2×2 у bento, більший title 1.35rem).
11. **Timeline item** — grid `year | content`, ліва лінія-border + крапка-маркер (accent). Variant `last` (без лінії знизу).
12. **Contact link** — велика кнопка-посилання, min-height 48.
13. **Avatar** — коло 160×160 з градієнтною обводкою (accent→warm) під аватаром.

**Чек:** [ ] кожен компонент використовує variables, має auto-layout, коректні constraints.

---

## 4. Складання desktop-макета (сторінка `03 Desktop`)

Збирати секцію за секцією зверху вниз, vertical auto-layout, gap між секціями = `space-6` (64).

1. **Site header (sticky nav)** — logo `IL.dev` (крапка accent) + desktop nav (5 пунктів) + nav-toggle (прихований на desktop). Окремо змакетувати `scrolled`-стан (фон `#0a0c10cc` + blur + нижня рамка) як варіант/окремий фрейм.
2. **Hero** — grid 1fr/auto:
   - Ліворуч: hero-badges (3 шт.) → H1 з градієнтним «Ігор Лялюк» → hero-role → CTA row (primary + 2 ghost).
   - Праворуч: avatar з градієнт-рингом + stats-grid (3 stat-картки: 74 / 26 / 4+).
3. **About** — section label + grid 2 колонки: 2 абзаци + about-card «Зараз».
4. **Skills** — section label + flex-wrap 12 skill-chips.
5. **Projects (bento)** — section label + grid 3 колонки, auto-rows ~180:
   - `flowi-mobile-app` — featured (span 2×2), pinned, ★2.
   - + 5 звичайних карток: Red-Gulp-Template-v1, p31_ai, crystal_palace_camp (2 links), fire-tetris (2 links), news-app-pv421.
6. **Experience** — section label + 3 timeline-items (2021— / Зараз / 2025–26).
7. **Contact** — section label + contact-intro + 2 contact-links (GitHub, redcode.in.ua).
8. **Footer** — 2 рядки: © 2026 Ігор Лялюк · RED Solutions / cursor-note (mono, сірий).

**Чек:** [ ] контент і тексти дослівно відповідають HTML; [ ] інстанси компонентів, не копії.

---

## 5. Мобільне меню (drawer)

- Змакетувати `nav-drawer` overlay: повноекранний фон `#0a0c10f5` + blur, вертикальний список 5 пунктів (drawer-варіант nav-link з border).
- Стан nav-toggle: іконка-гамбургер 22×22, кнопка 44×44.

---

## 6. Адаптивні варіанти (сторінка `04 Responsive`)

Зробити окремі фрейми під ключові брейкпоінти і відобразити зміни layout:

- **≤900px (tablet):** projects-bento → 2 колонки; featured → span 2×1; about-grid → 1 колонка.
- **≤768px (mobile-L):** hero → 1 колонка, центрування; hero-aside зверху (order -1); stats max-width 100%; projects → 1 колонка; featured → span 1.
- **≤560px (mobile-S):** desktop nav прихована → показати nav-toggle; timeline → 1 колонка.

**Чек:** [ ] перевірити кожен брейкпоінт; [ ] auto-layout «wrap» для chips/badges працює.

---

## 7. Декор і фінальні деталі

- [ ] Глобальні gradient-overlay (accent / warm radial) + noise як декоративні шари за контентом.
- [ ] Градієнтний текст у H1 (accent→warm) — fill через linear gradient на текстовому шарі.
- [ ] Градієнт-ринг навколо avatar (accent→warm, opacity 0.6).
- [ ] Focus-стани (outline accent) — задокументувати як annotation (опц.).
- [ ] Hover-стани кнопок/карток — окремими варіантами або в нотатках.

---

## 8. Перевірка та здача

- [ ] Візуально звірити Figma-макет із рендером HTML у браузері (side-by-side).
- [ ] Перевірити, що всі кольори/відступи прив'язані до variables (нема хардкоду).
- [ ] `get_screenshot` фінального фрейму → порівняти з оригіналом.
- [ ] Прибрати службові/чернеткові фрейми.
- [ ] (Опц.) Code Connect: змапити Figma-компоненти на майбутні код-компоненти.

---

## Порядок виконання (швидкий чеклист)

1. Tokens (кольори, spacing, radius, type styles) → Figma Variables.
2. Налаштувати файл, сторінки, сітку, фон.
3. Побудувати компоненти з варіантами.
4. Зібрати desktop-секції зверху вниз.
5. Додати мобільний drawer.
6. Зробити адаптивні фрейми (900 / 768 / 560).
7. Декор + градієнти + стани.
8. QA, скриншот-порівняння, прибирання.

> Виконання write-дій у Figma — лише після завантаження skill `figma-use` (MANDATORY перед `use_figma`) та `figma-generate-design` для посекційного складання.
