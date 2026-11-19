/*
 * Autopilot — реестр дизайнов.
 *
 * Один объект = одна карточка в dashboard.html.
 * Чтобы добавить новый дизайн:
 *   1. скопируйте _template.html в 07-my-design.html (или возьмите любой из шести);
 *   2. допишите сюда объект — пересборка не нужна, обновите dashboard.html.
 *
 * Обязательные поля: id, no, name, tagline, file.
 * Необязательные: thumb (картинка 16:9), accent (цвет), tags.
 * Данные дизайн получает внутри себя (window.D), этот реестр — только про навигацию.
 */
window.DESIGNS = [
  {
    id: "aurora",
    no: "01",
    name: "Аврора",
    tagline: "тёмный glass mission control",
    file: "01-aurora.html",
    thumb: "shots/thumb-01.png",
    accent: "#4df0be",
    tags: ["dark", "glass"]
  },
  {
    id: "editorial",
    no: "02",
    name: "Отчёт",
    tagline: "светлый печатный annual report",
    file: "02-editorial.html",
    thumb: "shots/thumb-02.png",
    accent: "#bf3a1e",
    tags: ["light", "serif"]
  },
  {
    id: "brutal",
    no: "03",
    name: "Пульт",
    tagline: "нео-брутализм и тикер",
    file: "03-brutal.html",
    thumb: "shots/thumb-03.png",
    accent: "#d8ff3e",
    tags: ["lime", "brutal"]
  },
  {
    id: "terminal",
    no: "04",
    name: "Терминал",
    tagline: "CRT-консоль и фосфор",
    file: "04-terminal.html",
    thumb: "shots/thumb-04.png",
    accent: "#70ff9a",
    tags: ["dark", "mono"]
  },
  {
    id: "blueprint",
    no: "05",
    name: "Чертёж",
    tagline: "blueprint и размерные линии",
    file: "05-blueprint.html",
    thumb: "shots/thumb-05.png",
    accent: "#1849a9",
    tags: ["light", "technical"]
  },
  {
    id: "bento",
    no: "06",
    name: "Бенто",
    tagline: "пастель и мягкие карточки",
    file: "06-bento.html",
    thumb: "shots/thumb-06.png",
    accent: "#5a4bdb",
    tags: ["light", "soft"]
  },
];

