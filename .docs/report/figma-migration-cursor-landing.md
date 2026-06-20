# Звіт про міграцію лендингу в Figma

**Джерело:** `landings/cursor-generated-index.html`
**План:** [`.docs/plans/figma-migration-cursor-landing.md`](../plans/figma-migration-cursor-landing.md)
**Figma-файл:** https://www.figma.com/design/vpYlUuFExfzEf61sNkVY0O (plan **FreeMode**, file key `vpYlUuFExfzEf61sNkVY0O`)
**Дата виконання:** 2026-06-20
**Статус:** ✅ виконано (всі 8 кроків плану)

---

## Що зроблено (за кроками плану)

### Крок 1 — Design tokens ✅
Створено 4 колекції змінних з прив'язкою CSS-імен через `codeSyntax` (WEB → `var(--name)`):
- **color** (9): bg, surface, surface-2, border, text, muted, accent, accent-dim, warm — з коректними scopes
- **space** (6): space-1…space-6 (8→64)
- **radius** (3): radius, radius-lg, radius-pill (12/16/999)
- **size** (2): max (1100), nav-h (72)

Текстові стилі (8): `Display/H1`, `Heading/Card`, `Body/Default`, `Body/Lead`, `Button/Label`, `Label/Section`, `Mono/Small`, `Mono/Badge`.

### Крок 2 — Сторінки та сітка ✅
Сторінки: `01 Tokens`, `02 Components`, `03 Desktop`, `04 Responsive`. Контент-контейнер 1100px, padding 24, gap між секціями 64.

### Крок 3 — Компоненти ✅ (13)
Badge (variant set: default/accent/warm), Button (primary/ghost), Skill chip, Lang chip, Section label, Nav link, Project link, Contact link, Stat, About card, Avatar (градієнт-ринг + реальне фото), Timeline item, Project card (variant set: default/featured). Усі прив'язані до змінних.

### Крок 4–5 — Desktop + drawer ✅
- **Desktop 1440** (`node 9:2`): усі 8 секцій (header з навігацією, hero, about, skills, projects-bento, experience, contact, footer).
- **Mobile menu (open)** (`node 22:142`): overlay drawer з 5 пунктами меню.

### Крок 6 — Адаптив ✅
- **Mobile 390** (`node 17:2`): hero вертикально (аватар зверху), 1-колонковий контент, bento в стовпчик, навігація → гамбургер.
- **Tablet 820** (`node 23:142`): 2-колонковий bento (featured на всю ширину), 1-колонковий about, desktop-навігація.

### Крок 7 — Декор ✅
Два радіальні градієнти-світіння (accent зверху-зліва, warm знизу-справа) як абсолютні шари за контентом; градієнтний H1 (accent→warm); градієнт-ринг аватара.

### Крок 8 — QA ✅
Кожну секцію звірено зі скриншотами; макет візуально відповідає рендеру HTML.

---

## Відхилення від плану (свідомі)

1. **Токени в 4 окремих колекціях** замість групування в одній — для чистоти і незалежних режимів.
2. **`Body` і `Body-muted` ділять один text-style** — Figma text styles не зберігають колір; muted застосовується через колірну змінну при використанні.
3. **Noise-overlay (opacity 3.5%) не відтворено** — фрактальний шум потребує растрового зображення; візуально незначущий, пропущено.

---

## Технічні нотатки / пастки, які зустрілись

- **`ALL_FILLS` не комбінується** з `FRAME_FILL`/`SHAPE_FILL`/`TEXT_FILL` у scopes змінних.
- **Opacity на variable-bound paint** не зберігається через spread/`Object.assign` — лише через clone-modify-reassign (`JSON.parse(JSON.stringify(node.fills))` → set opacity → reassign).
- **Інстанси з `defaultVariant.createInstance()` + `setProperties`** зберігають fill попереднього варіанта як override — довелось окремо чинити opacity warm/accent badge-інстансів на обох сторінках.
- **Зміна `layoutMode` (HORIZONTAL→VERTICAL)** скидає `FILL`/`HUG` дітей — після перемикання треба переустановлювати `layoutSizingHorizontal/Vertical`, інакше колонка стискається і текст роздуває висоту.
- **Реальний аватар** завантажено через MCP `upload_assets` (`createImageAsync` з URL у пісочниці не спрацював).

---

## Можливі доопрацювання (follow-up)

- Прибрати візуальне накладання компонентів на сторінці `02 Components` (косметика канви, не впливає на інстанси).
- Іконка close (X) у drawer виглядає радше як «‹» — за бажання вирівняти два повернуті прямокутники.
- Hover/focus стани кнопок/карток — додати окремими варіантами (зараз лише базові стани).
- Винести компоненти в published-бібліотеку + Code Connect, якщо планується design-to-code.
