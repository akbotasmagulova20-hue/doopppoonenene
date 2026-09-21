# 06 — SUNO И ЧАСТОТЫ

## ЧАСТЬ 1: SUNO — ПРАВОВАЯ БАЗА

### 1.1 Что удалось установить

**[ПРОВЕРИТЬ ЛИЧНО]** — прямой доступ к `suno.com/terms-of-service` и `help.suno.com`
из среды сборки заблокирован. Данные ниже собраны из вторичных источников
(см. список в `00-MASTER-BLUEPRINT.md`). **Перед первой загрузкой на YouTube откройте
эти две страницы сами и перечитайте разделы про Outputs и Commercial Use.**

| Вопрос | Что указывают источники (2026) |
|---|---|
| **Бесплатный план** | Только личное, **некоммерческое** использование. Монетизированный YouTube — коммерческое использование. **Бесплатный план не подходит.** |
| **Pro (~$10/мес)** | Даёт права на коммерческое использование сгенерированного |
| **Premier (~$30/мес)** | То же + больший объём генераций |
| **После отмены подписки** | Треки, созданные на платном плане, сохраняют коммерческую лицензию |
| **Формулировка «владение»** | В обновлённых условиях (после соглашения с Warner Music Group) слово «Ownership» применительно к пользователю **убрано**. Формально «автором» аудио остаётся Suno, а пользователю предоставляется **бессрочная лицензия** на коммерческую эксплуатацию |
| **Гарантия авторского права** | Suno прямо заявляет, что **не гарантирует**, что на Output возникнет авторское право |
| **Индемнификация** | Suno **не защищает** вас от претензий третьих лиц. Юридический риск и расходы — ваши |

### 1.2 Что это значит практически

**Плюсы:** платный план даёт легальную базу для монетизации на YouTube и дистрибуции
на стриминги. Это рабочая схема, которой пользуются тысячи каналов.

**Риски, которые надо принять осознанно:**

1. **Возможное отсутствие авторского права на трек.** В США Бюро регистрации авторских
   прав придерживается позиции, что произведения без достаточного человеческого
   творческого вклада не подлежат регистрации. Практический вывод: **ваш вклад должен
   быть реальным** — аранжировка, монтаж, сведение, мастеринг, структурирование в
   многочасовую композицию. Это и правовая защита, и защита от YouTube-политики
   inauthentic content.

2. **Отсутствие индемнификации.** Если кто-то заявит, что ваш трек похож на его
   произведение, разбираться будете вы. Митигация: не имитировать конкретных артистов
   (см. правила промтов ниже).

3. **Content ID — главная практическая ловушка.** Если вы дистрибутируете треки на
   Spotify/Apple Music через дистрибьютора **с включённым YouTube Content ID**,
   система может начать **выдавать претензии на ваши же YouTube-видео** и на видео
   ваших зрителей. Правила:
   - При дистрибуции **отключайте YouTube Content ID / «YouTube Music»-монетизацию**
     для треков, которые уже опубликованы у вас на канале в составе длинных видео,
   - ЛИБО убедитесь, что ваш канал привязан и claims автоматически разрешаются в вашу пользу,
   - Никогда не отдавайте в Content ID материал, содержащий чистые полевые записи
     (дождь, шум) — это провоцирует ложные претензии по всей платформе и может
     привести к санкциям со стороны дистрибьютора.

4. **Изменение условий.** Suno находится в активной перестройке лицензионной модели
   после соглашений с мейджор-лейблами. **Перечитывайте ToS раз в квартал.**

### 1.3 Жёсткие правила промтинга (чтобы не создать проблему)

- ⛔ **Никогда** не называть живых или недавно умерших исполнителей, названия групп,
  названия конкретных песен, названия лейблов.
- ⛔ Не использовать «in the style of [артист]» — даже если модель это принимает.
- ⛔ Не использовать функции, имитирующие конкретный голос или конкретную запись.
- ✅ Описывать **жанр, инструменты, темп, тональность, настроение, пространство**.
- ✅ Использовать нейтральные жанровые ориентиры: «ambient», «neoclassical»,
  «drone», «minimal piano» — это категории, а не чужая интеллектуальная собственность.
- ✅ Всегда включать `[Instrumental]` и явный запрет вокала.
- ✅ Сохранять все исходники генераций и все проектные файлы монтажа — это ваше
  доказательство человеческого вклада при апелляции.

### 1.4 Обязательный пост-процессинг (превращает генерацию в ваше произведение)

Никогда не загружайте вывод Suno напрямую. Минимальная обработка каждого трека:

1. **Обрезка** вступления/концовки до «бесшовного» фрагмента
2. **EQ:** high-shelf −3…−6 дБ выше 10 кГц (убрать «звенящие» AI-артефакты, которые
   мешают засыпанию), high-pass 30–40 Гц (убрать неслышимый низ, который ест битрейт)
3. **Многополосная компрессия** мягко, ratio ≤2:1 — выровнять динамику
4. **Reverb** общий (hall, 4–7 с) поверх всех треков — склеивает разные генерации в
   единое звуковое пространство. **Это главный приём**, превращающий 8 разрозненных
   генераций в одно произведение.
5. **Слой полевой записи** (дождь/шум/ветер) на всю длину — дополнительно склеивает
6. **Кроссфейды и перестановка блоков** (см. `04-longform-and-seo.md`)
7. **Мастеринг** до −14 LUFS, True Peak ≤ −1 dBTP

Эти 7 шагов — не «для красоты». Это ровно то, что отличает **вашу аранжировку**
от «загрузил вывод генератора».

---

## ЧАСТЬ 2: 50 ПРОМТОВ ДЛЯ SUNO

**Универсальный хвост промта** (добавлять ко всем):
```
[Instrumental] no vocals, no voice, no lyrics, no drums, no percussion, no sudden changes,
no build-ups, no drops, constant dynamics, seamless, loopable, slow harmonic rhythm,
long reverb tails, warm analog texture, low-pass filtered highs
```

### Sleep Pads (1–10)

1. `Ambient sleep drone, 50 BPM, D minor, deep warm synthesizer pads, very slow attack, sub-bass foundation at 40Hz, no melody, endless sustain, cinematic hall reverb`
2. `Minimal ambient for deep sleep, 48 BPM, A minor, two layered analog pads slowly detuning against each other, soft tape saturation, no rhythm`
3. `Dark warm ambient, 45 BPM, C minor, low mellotron-like strings, extremely slow chord changes every 40 seconds, muffled and distant`
4. `Soft ambient lullaby, 52 BPM, F major, felted piano with heavy damping, sparse single notes, wide reverb, warm and safe`
5. `Deep sleep ambient, 44 BPM, G minor, granular texture pad, continuous evolving drone, no transients, underwater feeling`
6. `Night ambient, 50 BPM, E minor, glass-like sustained tones, very high reverb, no bass movement, floating and weightless`
7. `Slow ambient for insomnia, 46 BPM, B flat minor, hollow wooden resonance, breathing pad that swells and recedes every 30 seconds`
8. `Warm analog ambient, 50 BPM, D major, vintage synthesizer strings, soft chorus, tape wow and flutter, nostalgic and calm`
9. `Ambient sleep music, 42 BPM, A flat major, choir-like wordless pad with no articulation, cathedral reverb, extremely soft`
10. `Minimal drone for sleep, 40 BPM, C drone, single sustained tone with slowly shifting overtones, meditative, hypnotic, unchanging`

### Piano / Neoclassical (11–18)

11. `Neoclassical sleep piano, 52 BPM, E minor, felt piano, very sparse notes with long silences, soft pedal, intimate close recording with room tone`
12. `Minimal piano for relaxation, 55 BPM, A minor, slow arpeggios, damped strings, warm reverb, gentle and repetitive without becoming a melody`
13. `Night piano ambient, 50 BPM, F minor, single notes over a sustained pad, extremely quiet, distant and reflective`
14. `Calm piano with rain texture, 54 BPM, C major, felted keys, soft background noise floor, cozy and warm`
15. `Neoclassical ambient, 48 BPM, D minor, piano and cello in long sustained notes, no vibrato, restrained and still`
16. `Piano and ambient pad, 50 BPM, G major, delicate upper register notes over a slow low pad, gentle and bright but not sharp`
17. `Slow piano meditation, 46 BPM, B minor, sparse chords with very long decay, heavy sustain pedal, contemplative`
18. `Music box style ambient, 58 BPM, F major, soft metallic tones, slow and gentle, nursery feeling without sentimentality`

### Strings / Orchestral Ambient (19–24)

19. `Ambient strings for sleep, 45 BPM, D minor, slow sustained string section, no vibrato, no crescendo, warm and enveloping`
20. `Cinematic calm strings, 48 BPM, A minor, cellos and violas in long tones, very slow bow changes, orchestral hall`
21. `Minimal string drone, 42 BPM, G minor, layered violins holding a single chord, subtle detuning, ethereal`
22. `Neoclassical night, 50 BPM, E flat major, strings and soft brass in a slowly breathing chord, distant and majestic but quiet`
23. `Chamber ambient, 52 BPM, C minor, small string ensemble, intimate recording, slow and sorrowful without drama`
24. `Ambient orchestral texture, 44 BPM, B flat major, blurred strings processed with long reverb, almost unrecognizable as orchestra`

### Space / Cosmic (25–30)

25. `Space ambient, 40 BPM, atonal drone, deep sub frequencies, slowly panning textures, vast and empty, science fiction atmosphere`
26. `Cosmic drone, 38 BPM, C drone, metallic shimmering overtones over a low hum, enormous sense of scale, weightless`
27. `Deep space sleep music, 42 BPM, D minor, distant pad layers with extreme reverb, occasional low swell every 60 seconds`
28. `Orbital ambient, 45 BPM, A minor, machine-like low hum with soft harmonic pad, sterile and calm`
29. `Nebula ambient, 40 BPM, F minor, granular clouds of sound, no clear notes, continuous evolving texture`
30. `Alien ocean ambient, 44 BPM, G minor, deep resonant tones with slow modulation, mysterious and vast`

### Nature-blended (31–38)

31. `Ambient with rain texture, 50 BPM, A minor, soft pad under a continuous rain-like noise layer, cozy and enclosed`
32. `Forest ambient, 48 BPM, E minor, warm woody pad with airy high texture, natural and organic`
33. `Ocean ambient, 46 BPM, D major, slow swelling pad matching the rhythm of waves, spacious and open`
34. `Winter ambient, 44 BPM, B minor, cold glassy tones, sparse and crystalline, feeling of snow and silence`
35. `Fireplace ambient, 52 BPM, C major, warm low pad with gentle crackling texture, intimate and safe`
36. `Mountain ambient, 42 BPM, G minor, wide airy drone with distant wind texture, high altitude feeling`
37. `Jungle night ambient, 48 BPM, A minor, humid warm pad with subtle organic movement, dense and alive`
38. `Desert ambient, 40 BPM, D minor, dry open drone with slow sand-like texture, vast and still`

### Focus / Study (39–44)

39. `Focus ambient, 65 BPM, A minor, steady soft pad with a very gentle pulse, consistent energy, no surprises, designed for concentration`
40. `Study music, 68 BPM, C major, minimal warm synth with subtle repeating figure, clean and unobtrusive`
41. `Deep work ambient, 62 BPM, E minor, continuous texture with a barely perceptible rhythm, flowing and steady`
42. `Coding ambient, 70 BPM, G minor, clean digital textures, repetitive and hypnotic, low emotional content`
43. `Library ambient, 60 BPM, D major, soft warm pad with paper-like high texture, quiet and academic`
44. `Productivity ambient, 66 BPM, B flat major, mellow sustained tones with light movement, encouraging but calm`

### Meditation (45–50)

45. `Meditation ambient, 40 BPM, C drone, singing bowl-like resonant tones with very long decay, spacious, contemplative`
46. `Breathing meditation music, 38 BPM, A minor, pad that swells over 6 seconds and releases over 6 seconds, continuous cycle`
47. `Temple ambient, 42 BPM, D drone, deep resonant metal tones, cavernous reverb, ancient and still`
48. `Zen ambient, 44 BPM, E minor, sparse plucked tones over silence, extremely minimal, patient`
49. `Healing-style ambient, 40 BPM, F major, warm harmonic drone with slowly shifting overtones, gentle and enveloping`
50. `Mindfulness ambient, 46 BPM, G major, soft continuous pad with no events at all, completely uneventful by design`

### Как использовать промты для одного видео

Для 3-часового видео: взять **один промт**, сгенерировать **8–12 вариаций**
(меняя одно слово — инструмент, тональность, температуру), затем склеить по методике
из `04-longform-and-seo.md`. Это даёт единое звучание при отсутствии слышимого повтора.

**Не использовать один и тот же промт для нескольких видео на канале** — получите
одинаково звучащие треки, что и слушателю заметно, и под политику попадает.

---

## ЧАСТЬ 3: ЧАСТОТЫ — НАУКА И МАРКЕТИНГ

### 3.1 Почему этот раздел критически важен

Ниша перенасыщена утверждениями вида «432 Hz исцеляет ДНК», «дельта-волны лечат
бессонницу», «binaural beats заменяют медитацию». Это создаёт три риска:

1. **Политика YouTube о медицинской дезинформации** — заявления о лечении заболеваний
   могут привести к ограничению монетизации или удалению.
2. **Потребительское законодательство** (FTC в США, аналоги в ЕС) — недоказуемые
   заявления о здоровье в коммерческом контенте.
3. **Репутация.** Аудитория wellness становится всё более скептичной.

**Правило канала: описываем ЗВУК, а не ЭФФЕКТ на здоровье.**

---

### 3.2 Разделение: что подтверждено, что нет

#### ✅ Достаточно подтверждено

| Утверждение | Статус |
|---|---|
| Прослушивание спокойной музыки перед сном связано с улучшением субъективного качества сна | Подтверждается систематическими обзорами; эффект от малого до умеренного |
| Маскирующий шум (белый/розовый/коричневый) снижает заметность внезапных посторонних звуков | Физика маскировки — базовая акустика, не оспаривается |
| Медленная музыка с узким динамическим диапазоном воспринимается как расслабляющая | Устойчивый результат психологии музыки |
| Постоянный фоновый звук может уменьшать субъективную «громкость» тиннитуса для части людей | Используется как элемент sound therapy; эффект индивидуален |

#### ⚠️ Смешанные / слабые доказательства

| Утверждение | Статус |
|---|---|
| **Бинауральные ритмы** улучшают сон, снижают тревожность | Систематический обзор 2026 (Acta Neuropsychiatrica) по молодым взрослым: эффект **от малого до умеренного**, но **высокая методологическая гетерогенность**, малые выборки, нужны предрегистрированные исследования. Мета-анализ 2025 по периоперационной тревожности показал эффективность. **Итог: «есть признаки эффекта, доказательная база слабая».** |
| **Розовый шум** улучшает глубокий сон / память | Есть отдельные лабораторные исследования со стимуляцией во время медленноволнового сна, но обобщать на «слушать розовый шум ночью» нельзя |
| **Коричневый шум** и концентрация при СДВГ | Популярное утверждение, серьёзной доказательной базы нет. **Не делать заявлений про СДВГ.** |
| Музыка снижает уровень кортизола | Есть исследования, но эффект зависит от контекста; не подаётся как гарантия |

#### ❌ Не подтверждено / маркетинговые мифы

| Утверждение | Статус |
|---|---|
| **432 Hz — «частота исцеления»**, «частота Вселенной», «резонирует с ДНК» | **Не подтверждено.** Исследование 2017 не нашло изменений электрической активности мозга. Исследование 2019 показало небольшое снижение ЧСС/давления, но на крошечной нерандомизированной выборке — невозможно отделить эффект частоты от ожидания и общей релаксации. Современный взгляд: эффект определяется не «волшебной частотой», а восприятием и контекстом |
| **440 Hz — «заговор» / вредная частота** | Полностью конспирологическое утверждение. 440 Hz — просто международный стандарт настройки (ISO 16) |
| Дельта/тета-волны «переключают» мозг в нужное состояние по команде | Упрощение. Частота бита ≠ частота мозговой активности. Entrainment — гипотеза с неоднозначными данными |
| «Solfeggio frequencies» (528 Hz «ремонтирует ДНК» и т.д.) | Псевдонаучная конструкция XX века. Никакой доказательной базы |
| «Эта музыка вылечит вашу бессонницу/тревожность/депрессию» | **Категорически нельзя. Это медицинское заявление.** |

---

### 3.3 Практические формулировки: что писать вместо

| ❌ Нельзя | ✅ Можно |
|---|---|
| «Лечит бессонницу» | «Ambient music designed for a calm bedtime routine» |
| «432 Hz heals your DNA» | «Tuned to A=432 Hz — a warmer, slightly lower tuning that some listeners prefer» |
| «Delta waves put your brain into deep sleep» | «Low-frequency ambient textures with a slow, steady character» |
| «Binaural beats cure anxiety» | «Binaural ambience — best experienced with headphones» |
| «Brown noise fixes ADHD focus» | «Brown noise — a deep, low-frequency sound many people use while working» |
| «Scientifically proven to…» | «Many listeners use this for…» |

### 3.4 Обязательный дисклеймер

Добавлять в описание **каждого** видео, где упоминаются частоты, шум, сон или медитация:

> This is ambient music intended for relaxation and background listening.
> It is not medical advice and not a treatment for any condition.
> If you have persistent problems with sleep, anxiety or concentration,
> please consult a qualified healthcare professional.

Локализовать этот текст на все языки метаданных.

### 3.5 Можно ли вообще использовать «432 Hz» в заголовках?

**Да** — как описание строя, а не как обещание эффекта. Запрос «432 hz sleep music»
имеет реальный поисковый объём, и игнорировать его нерационально. Формула:
- ✅ `Sleep Music in 432 Hz Tuning • 8 Hours • Warm Ambient`
- ❌ `432 Hz Healing Frequency • Repair Your Body While You Sleep`

В описании можно добавить честную строку:
> 432 Hz is an alternative tuning standard. Claims about special healing properties
> are not supported by scientific evidence — we use it simply because many listeners
> find the slightly lower tuning warmer.

Это одновременно защищает вас и отличает от конкурентов, которые обещают чудеса.
