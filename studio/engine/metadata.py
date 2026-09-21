#!/usr/bin/env python3
"""
metadata.py — generate localised YouTube metadata for a release.

Localisation of titles and descriptions is the single highest-leverage action in
the whole strategy (see ../global-sleep-brand/01-markets-and-language.md): the
audio carries no language, so one upload can serve every market and only the
metadata has to change.

The phrasings below are NATIVE SEARCH QUERIES, not translations. A machine
translation of "Deep Sleep Music" into German gives "Tiefer Schlaf Musik", which
nobody searches for; the real query is "Einschlafmusik". Every string here was
chosen as the phrase the market actually types.

  python3 metadata.py --release releases/batch-01.json --out releases/batch-01
"""
import argparse, json, os, sys

LANGS = ["en", "es", "pt", "de", "ja"]

LANG_NAME = {"en": "English", "es": "Español", "pt": "Português (BR)",
             "de": "Deutsch", "ja": "日本語"}

# YouTube localization keys
LANG_CODE = {"en": "en", "es": "es", "pt": "pt-BR", "de": "de", "ja": "ja"}

DUR = {
    "en": lambda h: f"{h} Hours" if h != 1 else "1 Hour",
    "es": lambda h: f"{h} Horas" if h != 1 else "1 Hora",
    "pt": lambda h: f"{h} Horas" if h != 1 else "1 Hora",
    "de": lambda h: f"{h} Stunden" if h != 1 else "1 Stunde",
    "ja": lambda h: f"{h}時間",
}

ORIGINALITY = {
    "en": ("All audio on this channel is original, synthesised and mixed in house. "
           "Visuals are original artwork, animated and edited by hand."),
    "es": ("Todo el audio de este canal es original, sintetizado y mezclado por "
           "nosotros. Los visuales son obra original, animada y editada a mano."),
    "pt": ("Todo o áudio deste canal é original, sintetizado e mixado por nós. "
           "Os visuais são obra original, animada e editada à mão."),
    "de": ("Alle Klänge dieses Kanals sind Eigenproduktionen, selbst synthetisiert "
           "und abgemischt. Die Bilder sind eigene Werke, von Hand animiert."),
    "ja": ("このチャンネルの音はすべてオリジナルで、自分で合成・ミックスしています。"
           "映像もオリジナル作品です。"),
}

DISCLAIMER = {
    "en": ("This is ambient sound for relaxation and background listening. It is not "
           "medical advice and not a treatment for any condition. If you have "
           "persistent problems with sleep, please consult a qualified healthcare "
           "professional."),
    "es": ("Este es sonido ambiental para relajarse y escuchar de fondo. No es un "
           "consejo médico ni un tratamiento para ninguna afección. Si tienes "
           "problemas persistentes de sueño, consulta a un profesional de la salud."),
    "pt": ("Este é um som ambiente para relaxamento e escuta de fundo. Não é "
           "aconselhamento médico nem tratamento para qualquer condição. Se você tem "
           "problemas persistentes de sono, consulte um profissional de saúde."),
    "de": ("Dies ist Umgebungsklang zum Entspannen und für den Hintergrund. Es ist "
           "keine medizinische Beratung und keine Behandlung. Bei anhaltenden "
           "Schlafproblemen wenden Sie sich bitte an medizinisches Fachpersonal."),
    "ja": ("これはリラックスと環境音としての音源です。医療的な助言でも、"
           "何らかの症状の治療でもありません。睡眠の悩みが続く場合は専門医にご相談ください。"),
}

HEADPHONES = {"en": "Best with headphones or a soft speaker",
              "es": "Mejor con auriculares o un altavoz suave",
              "pt": "Melhor com fones de ouvido ou uma caixa de som suave",
              "de": "Am besten mit Kopfhörern oder einem leisen Lautsprecher",
              "ja": "ヘッドホンか小さめのスピーカーでどうぞ"}

DURATION_LABEL = {"en": "Duration", "es": "Duración", "pt": "Duração",
                  "de": "Länge", "ja": "長さ"}

# ---------------------------------------------------------------------------
# theme -> language -> title template, opening paragraph, keywords, playlist
# {d} is the localised duration string.
# ---------------------------------------------------------------------------
T = {
"rain": {
 "en": ("Rain Sounds for Sleeping • {d} • No Music, No Thunder",
        "Steady rain against a window at night. No music, no thunder and no sudden "
        "changes — the loudest gusts have been removed so nothing wakes you.",
        ["rain sounds for sleeping", "rain sounds no music", "rain on window",
         "sleep sounds", "rain sounds for sleeping 8 hours", "rain ambience"],
        "Rain for Sleeping"),
 "es": ("Sonido de Lluvia para Dormir • {d} • Sin Música ni Truenos",
        "Lluvia constante contra la ventana por la noche. Sin música, sin truenos y "
        "sin cambios bruscos.",
        ["sonido de lluvia para dormir", "lluvia para dormir sin música",
         "sonidos para dormir", "lluvia en la ventana", "ruido de lluvia"],
        "Lluvia para Dormir"),
 "pt": ("Som de Chuva para Dormir • {d} • Sem Música e Sem Trovão",
        "Chuva constante na janela durante a noite. Sem música, sem trovão e sem "
        "mudanças bruscas.",
        ["som de chuva para dormir", "chuva para dormir sem música",
         "sons para dormir", "chuva na janela", "barulho de chuva"],
        "Som de Chuva"),
 "de": ("Regengeräusche zum Einschlafen • {d} • Ohne Musik",
        "Gleichmäßiger Regen am Fenster in der Nacht. Ohne Musik, ohne Donner und "
        "ohne plötzliche Wechsel.",
        ["regengeräusche zum einschlafen", "regen zum schlafen ohne musik",
         "einschlafhilfe regen", "regen am fenster", "naturgeräusche schlafen"],
        "Regen zum Einschlafen"),
 "ja": ("【睡眠用】雨の音 • {d} • 音楽なし・雷なし",
        "夜の窓に降り続く雨の音。音楽も雷もなく、急な変化もありません。",
        ["雨の音 睡眠用", "雨の音 作業用", "睡眠用bgm 雨", "環境音 雨", "寝落ち 雨の音"],
        "雨の音"),
},
"fireplace": {
 "en": ("Fireplace Crackling • {d} • No Music",
        "A slow wood fire that never quite goes out. No music, no wind, no voices — "
        "only the crackle of burning logs.",
        ["fireplace sounds", "fireplace crackling no music", "fire sounds for sleeping",
         "crackling fireplace 8 hours", "cozy fireplace ambience"],
        "Night Ambience"),
 "es": ("Chimenea Crepitante • {d} • Sin Música",
        "Un fuego de leña lento que nunca se apaga. Sin música, sin viento, sin voces.",
        ["sonido de chimenea", "chimenea crepitante", "fuego para dormir",
         "sonido de fuego relajante"],
        "Ambiente Nocturno"),
 "pt": ("Lareira Crepitante • {d} • Sem Música",
        "Um fogo de lenha lento que nunca se apaga. Sem música, sem vento, sem vozes.",
        ["som de lareira", "lareira crepitante", "som de fogo para dormir",
         "fogueira para dormir"],
        "Ambiente Noturno"),
 "de": ("Kaminfeuer Geräusche • {d} • Ohne Musik",
        "Ein langsames Holzfeuer, das nie ganz ausgeht. Ohne Musik, ohne Wind, "
        "ohne Stimmen.",
        ["kaminfeuer geräusche", "kaminfeuer zum einschlafen", "feuer knistern",
         "lagerfeuer geräusche"],
        "Nachtatmosphäre"),
 "ja": ("【睡眠用】暖炉の音 • {d} • 音楽なし",
        "静かに燃え続ける薪の音。音楽も風の音も声もありません。",
        ["暖炉の音", "焚き火の音 睡眠用", "暖炉 睡眠用bgm", "環境音 焚き火"],
        "夜の環境音"),
},
"ocean": {
 "en": ("Ocean Waves • {d} • No Music",
        "Waves washing over black volcanic sand at night. The loudest breakers have "
        "been taken out so the night stays even.",
        ["ocean waves sounds", "ocean sounds for sleeping", "waves sounds no music",
         "sea sounds sleep", "ocean waves 10 hours"],
        "Nature Sounds"),
 "es": ("Sonido de Olas del Mar • {d} • Sin Música",
        "Olas rompiendo sobre arena volcánica negra por la noche, sin picos bruscos.",
        ["sonido de olas del mar", "sonido del mar para dormir", "olas para dormir",
         "sonidos de la naturaleza"],
        "Sonidos de la Naturaleza"),
 "pt": ("Som de Ondas do Mar • {d} • Sem Música",
        "Ondas quebrando na areia vulcânica escura à noite, sem picos bruscos.",
        ["som de ondas do mar", "som do mar para dormir", "ondas para dormir",
         "sons da natureza"],
        "Sons da Natureza"),
 "de": ("Meeresrauschen zum Einschlafen • {d} • Ohne Musik",
        "Wellen auf schwarzem Vulkansand bei Nacht, ohne laute Brecher.",
        ["meeresrauschen", "meeresrauschen zum einschlafen", "wellen zum schlafen",
         "naturgeräusche meer"],
        "Naturgeräusche"),
 "ja": ("【睡眠用】波の音 • {d} • 音楽なし",
        "夜の黒い砂浜に寄せる波の音。大きく崩れる波は取り除いてあります。",
        ["波の音 睡眠用", "海の音 睡眠", "自然音 波", "波の音 作業用"],
        "自然の音"),
},
"wind": {
 "en": ("Winter Wind • {d} • Snow and Wind for Sleep",
        "Wind moving across snow outside a cabin. Long slow gusts, nothing sharp.",
        ["winter wind sounds", "wind sounds for sleeping", "blizzard sounds sleep",
         "snow storm sounds", "wind ambience"],
        "Nature Sounds"),
 "es": ("Viento de Invierno • {d} • Sonido para Dormir",
        "Viento sobre la nieve junto a una cabaña. Ráfagas largas y lentas.",
        ["sonido de viento para dormir", "viento y nieve", "sonido de ventisca",
         "sonidos de la naturaleza"],
        "Sonidos de la Naturaleza"),
 "pt": ("Vento de Inverno • {d} • Som para Dormir",
        "Vento sobre a neve ao lado de uma cabana. Rajadas longas e lentas.",
        ["som de vento para dormir", "vento e neve", "som de nevasca",
         "sons da natureza"],
        "Sons da Natureza"),
 "de": ("Wintersturm Geräusche • {d} • Zum Einschlafen",
        "Wind über Schnee vor einer Hütte. Lange, langsame Böen, nichts Schroffes.",
        ["windgeräusche einschlafen", "schneesturm geräusche", "wind zum schlafen",
         "naturgeräusche winter"],
        "Naturgeräusche"),
 "ja": ("【睡眠用】冬の風の音 • {d} • 雪と風",
        "山小屋の外、雪の上を渡る風の音。ゆっくりとした長い風だけです。",
        ["風の音 睡眠用", "吹雪 音", "自然音 風", "冬 環境音"],
        "自然の音"),
},
"stream": {
 "en": ("Forest Stream • {d} • Water Over Stones",
        "A slow stream running over smooth stones in deep forest. Birds fade out "
        "after the first hour so the night stays quiet.",
        ["forest stream sounds", "river sounds for sleeping", "water sounds 8 hours",
         "creek sounds sleep", "nature sounds sleep"],
        "Nature Sounds"),
 "es": ("Sonido de Arroyo en el Bosque • {d} • Agua sobre Piedras",
        "Un arroyo lento entre piedras en el bosque profundo.",
        ["sonido de arroyo", "sonido de agua para dormir", "río para dormir",
         "sonidos de la naturaleza"],
        "Sonidos de la Naturaleza"),
 "pt": ("Som de Riacho na Floresta • {d} • Água sobre Pedras",
        "Um riacho lento entre pedras na floresta profunda.",
        ["som de riacho", "som de água para dormir", "rio para dormir",
         "sons da natureza"],
        "Sons da Natureza"),
 "de": ("Bachplätschern im Wald • {d} • Wasser über Steinen",
        "Ein langsamer Bach über glatte Steine tief im Wald.",
        ["bachplätschern", "wassergeräusche einschlafen", "bach im wald",
         "naturgeräusche wald"],
        "Naturgeräusche"),
 "ja": ("【睡眠用】森の小川の音 • {d} • 水と石",
        "深い森を流れる小川の音。鳥の声は最初の一時間で静かに消えます。",
        ["小川の音 睡眠用", "川の音 睡眠", "自然音 水", "森の音 作業用"],
        "自然の音"),
},
"city": {
 "en": ("Night City Ambience • {d} • A Sleeping City at 4 AM",
        "A city at its quietest hour: a distant hum, faint rain, nothing else.",
        ["night city ambience", "city sounds for sleeping", "urban ambience",
         "city hum sleep", "night ambience"],
        "Night Ambience"),
 "es": ("Ciudad de Noche • {d} • Ambiente Urbano para Dormir",
        "La ciudad en su hora más tranquila: un zumbido lejano y algo de lluvia.",
        ["ciudad de noche sonido", "ambiente urbano para dormir", "ruido de ciudad"],
        "Ambiente Nocturno"),
 "pt": ("Cidade à Noite • {d} • Ambiente Urbano para Dormir",
        "A cidade na sua hora mais silenciosa: um zumbido distante e um pouco de chuva.",
        ["cidade à noite som", "ambiente urbano para dormir", "barulho de cidade"],
        "Ambiente Noturno"),
 "de": ("Nächtliche Stadt • {d} • Stadtatmosphäre zum Einschlafen",
        "Die Stadt in ihrer ruhigsten Stunde: ein fernes Summen, leiser Regen.",
        ["stadt geräusche nacht", "stadtatmosphäre einschlafen", "großstadt rauschen"],
        "Nachtatmosphäre"),
 "ja": ("【睡眠用】深夜の街の音 • {d} • 午前4時の街",
        "一番静かな時間の街。遠いざわめきと、かすかな雨だけ。",
        ["街の音 睡眠用", "都会 環境音", "夜の街 音", "環境音 睡眠"],
        "夜の環境音"),
},
"space": {
 "en": ("Space Ambient • {d} • Deep Drone for Sleep",
        "Low sub frequencies and slowly drifting textures. Nothing here resembles a "
        "melody, and nothing ever arrives.",
        ["space ambient music", "space sleep music", "dark ambient sleep",
         "deep drone sleep", "sci fi ambient"],
        "Night Ambience"),
 "es": ("Ambiente Espacial • {d} • Música para Dormir",
        "Frecuencias graves y texturas que se desplazan muy despacio. Sin melodía.",
        ["ambiente espacial música", "música espacial para dormir",
         "dark ambient dormir"],
        "Ambiente Nocturno"),
 "pt": ("Ambiente Espacial • {d} • Música para Dormir",
        "Frequências graves e texturas que se deslocam muito devagar. Sem melodia.",
        ["ambiente espacial música", "música espacial para dormir",
         "dark ambient dormir"],
        "Ambiente Noturno"),
 "de": ("Weltraum Ambient • {d} • Einschlafmusik",
        "Tiefe Frequenzen und sehr langsam driftende Texturen. Ohne Melodie.",
        ["weltraum ambient", "einschlafmusik ambient", "dark ambient schlafen"],
        "Nachtatmosphäre"),
 "ja": ("【睡眠用BGM】宇宙アンビエント • {d} • 深い低音",
        "低い持続音と、ゆっくり漂うテクスチャ。旋律はありません。",
        ["宇宙 bgm 睡眠", "アンビエント 睡眠用", "ダークアンビエント", "睡眠用bgm 深い"],
        "夜の環境音"),
},
"brown": {
 "en": ("Brown Noise • {d} • Deep and Soft for Sleep",
        "Continuous brown noise: deeper and softer than white noise, with the harsh "
        "high frequencies rolled off.",
        ["brown noise", "brown noise for sleeping", "brown noise 10 hours",
         "brown noise black screen", "deep noise sleep"],
        "Noise for Sleep"),
 "es": ("Ruido Marrón • {d} • Profundo y Suave para Dormir",
        "Ruido marrón continuo: más profundo y suave que el ruido blanco.",
        ["ruido marrón", "ruido marrón para dormir", "ruido marrón 10 horas"],
        "Ruido para Dormir"),
 "pt": ("Ruído Marrom • {d} • Profundo e Suave para Dormir",
        "Ruído marrom contínuo: mais profundo e suave que o ruído branco.",
        ["ruído marrom", "ruído marrom para dormir", "ruído marrom 10 horas"],
        "Ruído para Dormir"),
 "de": ("Braunes Rauschen • {d} • Tief und Weich zum Einschlafen",
        "Durchgehendes braunes Rauschen: tiefer und weicher als weißes Rauschen.",
        ["braunes rauschen", "braunes rauschen einschlafen", "rauschen zum schlafen"],
        "Rauschen zum Schlafen"),
 "ja": ("ブラウンノイズ • {d} • 深くやわらかい睡眠用ノイズ",
        "途切れないブラウンノイズ。ホワイトノイズより低く、耳に刺さる高音を抑えています。",
        ["ブラウンノイズ", "ブラウンノイズ 睡眠", "ノイズ 睡眠用", "ブラウンノイズ 10時間"],
        "睡眠用ノイズ"),
},
"pink": {
 "en": ("Pink Noise • {d} • Black Screen",
        "Continuous pink noise on a fully black screen — energy spread evenly across "
        "the octaves. The black screen saves battery and will not light a dark room.",
        ["pink noise", "pink noise for sleeping", "pink noise black screen",
         "pink noise 10 hours", "masking sound sleep"],
        "Noise for Sleep"),
 "es": ("Ruido Rosa • {d} • Pantalla Negra",
        "Ruido rosa continuo en pantalla completamente negra. Ahorra batería y no "
        "ilumina la habitación.",
        ["ruido rosa", "ruido rosa para dormir", "ruido rosa pantalla negra"],
        "Ruido para Dormir"),
 "pt": ("Ruído Rosa • {d} • Tela Preta",
        "Ruído rosa contínuo em tela totalmente preta. Economiza bateria e não "
        "ilumina o quarto.",
        ["ruído rosa", "ruído rosa para dormir", "ruído rosa tela preta"],
        "Ruído para Dormir"),
 "de": ("Rosa Rauschen • {d} • Schwarzer Bildschirm",
        "Durchgehendes rosa Rauschen auf schwarzem Bildschirm. Spart Akku und "
        "erhellt den Raum nicht.",
        ["rosa rauschen", "rosa rauschen einschlafen", "schwarzer bildschirm rauschen"],
        "Rauschen zum Schlafen"),
 "ja": ("ピンクノイズ • {d} • 黒画面",
        "真っ黒な画面で流れ続けるピンクノイズ。画面が暗いので部屋を明るくしません。",
        ["ピンクノイズ", "ピンクノイズ 睡眠", "黒画面 睡眠用", "ノイズ 10時間"],
        "睡眠用ノイズ"),
},
"sleepmusic": {
 "en": ("Deep Sleep Music • {d} • Soft Rain and Ambient Pads",
        "Slow ambient pads under soft rain. The sequence never repeats in the same "
        "order, and the level recedes gently over the first part of the night.",
        ["deep sleep music", "sleep music", "ambient sleep music",
         "music for sleeping", "relaxing sleep music"],
        "Deep Sleep Collection"),
 "es": ("Música para Dormir Profundamente • {d} • Lluvia Suave y Ambiente",
        "Pads ambientales lentos bajo lluvia suave. La secuencia nunca se repite igual.",
        ["música para dormir profundamente", "música para dormir",
         "música relajante para dormir", "música ambiental para dormir"],
        "Música para Dormir"),
 "pt": ("Música para Dormir Profundo • {d} • Chuva Suave e Ambiente",
        "Pads ambientais lentos sob chuva suave. A sequência nunca se repete igual.",
        ["música para dormir profundo", "música para dormir",
         "música relaxante para dormir", "música ambiente para dormir"],
        "Música para Dormir"),
 "de": ("Einschlafmusik • {d} • Sanfter Regen und Flächen",
        "Langsame Klangflächen unter leisem Regen. Die Abfolge wiederholt sich nie "
        "in derselben Reihenfolge.",
        ["einschlafmusik", "entspannungsmusik zum einschlafen", "musik zum einschlafen",
         "schlafmusik"],
        "Einschlafmusik"),
 "ja": ("【睡眠用BGM】深い眠りのための音楽 • {d} • やさしい雨とパッド",
        "やわらかな雨の下でゆっくり流れるパッド。同じ順番で繰り返すことはありません。",
        ["睡眠用bgm", "寝る前に聴く音楽", "眠れる音楽", "リラックス音楽 睡眠"],
        "睡眠用BGM"),
},
}


def build(item):
    """Return {lang: {title, description, tags, playlist}} for one video."""
    theme, hours = item["theme"], item["hours"]
    out = {}
    for lang in LANGS:
        title_tpl, lead, kw, playlist = T[theme][lang]
        d = DUR[lang](hours)
        title = title_tpl.format(d=d)
        if len(title) > 100:
            print(f"warning: {item['slug']} [{lang}] title is {len(title)} chars "
                  f"(YouTube limit 100)", file=sys.stderr)
        tags = list(kw)
        desc = "\n\n".join([
            lead,
            f"{DURATION_LABEL[lang]}: {d}\n{HEADPHONES[lang]}",
            ORIGINALITY[lang],
            DISCLAIMER[lang],
            " ".join("#" + t.replace(" ", "") for t in item.get("hashtags", [])),
        ]).strip()
        out[lang] = {"title": title, "description": desc, "tags": tags,
                     "playlist": playlist}
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--release", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    spec = json.load(open(a.release, encoding="utf-8"))
    os.makedirs(a.out, exist_ok=True)

    api_payload = {}
    for item in spec["videos"]:
        loc = build(item)
        api_payload[item["slug"]] = {
            LANG_CODE[l]: {"title": v["title"], "description": v["description"]}
            for l, v in loc.items()}

        lines = [f"# {item['slug']}", "",
                 f"- preset: `{item['preset']}`  ·  mode: `{item['mode']}`  ·  "
                 f"{item['hours']} h  ·  seed `{item['seed']}`",
                 f"- render: `{item['render']}`",
                 f"- thumbnail: `{item['thumb']}`", ""]
        for l in LANGS:
            v = loc[l]
            lines += [f"## {LANG_NAME[l]} ({LANG_CODE[l]})", "",
                      "**Title**", "```", v["title"], "```", "",
                      "**Description**", "```", v["description"], "```", "",
                      "**Tags**", "```", ", ".join(v["tags"]), "```", "",
                      f"**Playlist:** {v['playlist']}", ""]
        with open(os.path.join(a.out, f"{item['slug']}.md"), "w",
                  encoding="utf-8") as f:
            f.write("\n".join(lines))

    with open(os.path.join(a.out, "localizations.json"), "w",
              encoding="utf-8") as f:
        json.dump(api_payload, f, ensure_ascii=False, indent=2)

    print(f"wrote {len(spec['videos'])} metadata files + localizations.json "
          f"to {a.out}")


if __name__ == "__main__":
    main()
