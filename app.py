import base64
import re
from html import escape
from datetime import date, timedelta
from pathlib import Path
import streamlit as st
from engine import RULES, executar_inferencia

st.set_page_config(
    page_title="DermaTech | Clínica de Estética",
    page_icon="✳",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE = Path(__file__).parent
ASSETS = BASE / "assets"


def image_data_uri(filename):
    path = ASSETS / filename
    suffix = path.suffix.lower()
    mime = "image/png" if suffix == ".png" else "image/jpeg"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def render_photo_card(filename, title, subtitle, description, tag=None, wide=False):
    image_uri = image_data_uri(filename)
    aspect_class = "wide" if wide else ""
    tag_html = f'<span class="tag">{escape(tag)}</span>' if tag else ""
    st.markdown(
        f'''<article class="photo-card">
          <div class="photo-frame {aspect_class}"><img src="{image_uri}" alt="{escape(title)}"></div>
          <div class="photo-copy">{subtitle}<h3>{escape(title)}</h3>{description}{tag_html}</div>
        </article>''',
        unsafe_allow_html=True,
    )


st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap');
:root{--paper:#f7f6f1;--ink:#25372f;--forest:#29463a;--sage:#e5e9df;--clay:#bd7864;--line:#e4e2d9;--white:#fffefa;}
.stApp{background:var(--paper);color:var(--ink);font-family:'DM Sans',sans-serif;}
[data-testid="stSidebar"]{display:none!important;}
header[data-testid="stHeader"],.stAppHeader,[data-testid="stToolbar"],[data-testid="stDecoration"],#MainMenu,[data-testid="stStatusWidget"]{display:none!important;visibility:hidden!important;height:0!important;}
.stAppViewContainer .main .block-container{padding-top:1.15rem!important;max-width:1500px!important;}
.st-key-top_navigation{background:#29463a;border:1px solid #29463a;border-radius:18px;padding:.75rem 1rem;margin-bottom:1.55rem;box-shadow:0 8px 22px rgba(25,55,41,.10);}
.st-key-top_navigation [data-testid="stHorizontalBlock"]{align-items:center!important;gap:.5rem!important;}
.st-key-top_navigation .brand{padding:.25rem 0;color:#fff!important;}
.st-key-top_navigation .brand small{color:#dce8dd!important;}
.st-key-top_navigation [data-testid="stButton"]>button{width:100%!important;min-height:2.65rem!important;white-space:nowrap!important;background:rgba(255,255,255,.10)!important;color:#fff!important;-webkit-text-fill-color:#fff!important;border:1px solid rgba(255,255,255,.20)!important;border-radius:999px!important;}
.st-key-top_navigation [data-testid="stButton"]>button[kind="primary"]{background:#e5e9df!important;color:#29463a!important;-webkit-text-fill-color:#29463a!important;border-color:#e5e9df!important;}
h1,h2,h3{font-family:'Playfair Display',Georgia,serif!important;color:var(--ink)!important;}
h1{font-size:2.5rem!important;line-height:1.12!important;}
.brand{font-family:'DM Sans',sans-serif;font-weight:700;font-size:1.65rem;color:var(--forest);letter-spacing:-1px;}
.brand small{display:block;font-size:.57rem;letter-spacing:2px;color:#657168;font-weight:700;}
.eyebrow{color:var(--clay);font-size:.72rem;letter-spacing:2px;font-weight:700;text-transform:uppercase;}
.hero,.about-hero{background:linear-gradient(120deg,#e8e9df,#f7f3eb);border:1px solid var(--line);border-radius:24px;padding:2rem;margin:.5rem 0 1.2rem;}
.card,.about-values,.proposal-card,.access-panel{background:var(--white);border:1px solid var(--line);border-radius:17px;padding:1rem 1.15rem;margin:.35rem 0;height:100%;}
.stat-card{background:#fffefa;border:1px solid var(--line);border-radius:15px;padding:1.05rem 1.2rem;min-height:110px;}
.stat-card small{font-size:.68rem;letter-spacing:1px;color:#68746a;font-weight:700;}
.stat-card strong{display:block;font-size:2rem;color:var(--forest);line-height:1.3;}
.stat-card span{font-size:.78rem;color:#68746a;}
.muted{color:#68746a;font-size:.9rem;}
.tag{display:inline-block;background:#e9eee5;color:#405d47;padding:.3rem .6rem;border-radius:8px;font-size:.75rem;font-weight:700;}
.rule-id{display:inline-block;background:#edf2eb;color:#405d47;border-radius:8px;padding:.32rem .55rem;font-size:.75rem;font-weight:700;margin-right:.5rem;}
.rule-meta{font-size:.7rem;color:#718074;font-weight:700;letter-spacing:1px;text-transform:uppercase;}
.photo-card{overflow:hidden;background:#fffefa;border:1px solid var(--line);border-radius:17px;padding:0;height:100%;display:flex;flex-direction:column;}
.photo-frame{width:100%;aspect-ratio:4/3;overflow:hidden;background:#e9e9e1;}
.photo-frame img{display:block;width:100%;height:100%;object-fit:cover;object-position:center;}
.photo-frame.wide{aspect-ratio:16/9;}
.photo-copy{padding:1rem 1.1rem 1.15rem;flex:1;}
.staff-role{font-size:.7rem;letter-spacing:1px;text-transform:uppercase;color:#9b6d5d;font-weight:700;}
.responsibility-box{background:#f4f5ef;border:1px solid #e6e9e0;border-radius:12px;padding:.8rem .9rem;margin:.8rem 0;}
.proposal-step{display:flex;gap:.85rem;align-items:flex-start;background:#fffefa;border:1px solid var(--line);border-radius:14px;padding:1rem;margin:.45rem 0;}
.proposal-step .number{flex:0 0 2rem;height:2rem;border-radius:10px;background:#e9eee5;color:#405d47;display:flex;align-items:center;justify-content:center;font-weight:700;}
.proposal-highlight{border-top:1px solid var(--line);padding-top:.9rem;margin-top:1rem;color:var(--forest);font-weight:700;}
.fact-card{background:#fffefa;border:1px solid var(--line);border-radius:13px;padding:.85rem 1rem;margin:.25rem 0;min-height:74px;}
.fact-card small{color:#68746a;font-size:.75rem;}
.fact-card strong{display:block;color:var(--ink);margin-top:.2rem;}
div[data-testid="stButton"]>button,div[data-testid="stFormSubmitButton"]>button{background:#29463a!important;color:#fff!important;border:1px solid #29463a!important;border-radius:999px!important;font-weight:700!important;padding:.62rem 1.15rem!important;}
.st-key-booking_panel{max-width:1120px;width:100%;margin:.4rem auto 1.5rem!important;background:#fffefa;border:1px solid #dfe5da;border-radius:20px;padding:1.15rem 1.3rem!important;}
.review-card{background:#fffefa;border:1px solid #dfe5da;border-radius:18px;padding:1.35rem 1.55rem;box-shadow:0 8px 24px rgba(37,55,47,.06);min-height:210px;}
.review-card .review-stars{color:#b8873e;font-size:1.05rem;letter-spacing:2px;margin-bottom:.5rem;}
.review-label{font-size:.68rem;color:#77877a;letter-spacing:1px;text-transform:uppercase;font-weight:700;}
.review-count{text-align:center;color:#58705d;font-size:.72rem;font-weight:700;letter-spacing:1.15px;padding:.65rem .35rem;}
.status-banner{border-radius:13px;padding:1rem 1.2rem;margin:.8rem 0 1.1rem;font-weight:700;color:#fff!important;}
.status-banner.success{background:#173f32;}
.status-banner.error{background:#873d43;}
.allergy-warning{display:flex;flex-direction:column;gap:.25rem;padding:.85rem 1rem;margin:.55rem 0 1rem;border:1px solid #e6d28b;border-left:4px solid #bd8b24;border-radius:12px;background:#fff8df;color:#4c3a12;}
.trace-start,.trace-finish{background:#eef2eb;border:1px solid #dce5da;border-radius:14px;padding:1rem 1.1rem;margin:.55rem 0;}
.trace-finish{background:#e7eee6;border-color:#cbd9cb;}
.trace-kicker{display:block;color:#627568;font-size:.65rem;font-weight:800;letter-spacing:1.1px;margin-bottom:.45rem;}
.trace-step{background:#fffefa;border:1px solid #dfe5da;border-left:4px solid #829b83;border-radius:12px;padding:.85rem 1rem;margin:.65rem 0 .65rem 1rem;}
.trace-number{font-size:.64rem;font-weight:800;color:#718174;background:#eef2eb;border-radius:6px;padding:.25rem .4rem;margin-right:.4rem;}
.trace-meta{display:block;color:#7b887d;font-size:.68rem;font-weight:700;margin-top:.45rem;}
.site-footer{margin-top:3rem;padding:1.9rem 2rem 1.2rem;background:#29463a;border-radius:22px;color:#eef4ed;}
.site-footer-inner{display:flex;justify-content:space-between;align-items:flex-start;gap:2rem;flex-wrap:wrap;}
.site-footer-brand{font-weight:700;font-size:1.35rem;color:#fff!important;}
.site-footer-brand small{display:block;font-size:.57rem;letter-spacing:2px;color:#d4e1d5!important;}
.site-footer-meta{font-size:.72rem;color:#cbd9cc!important;margin-top:1.15rem;padding-top:.85rem;border-top:1px solid rgba(255,255,255,.22);}
footer{visibility:hidden!important;}
</style>
""",
    unsafe_allow_html=True,
)

STAFF = [
    {"name": "Helena Martins", "role": "Biomedicina estética", "focus": "Acne e oleosidade", "responsibility": "Organiza o encaminhamento inicial de pessoas que relatam acne e oleosidade, reunindo as informações importantes para a avaliação presencial.", "bio": "Seu atendimento começa pela escuta da queixa e pelo registro de informações sobre a rotina de cuidados, a duração do incômodo e as características relatadas pelo cliente.", "photo": "helena.jpg"},
    {"name": "Mariana Costa", "role": "Fisioterapia dermatofuncional", "focus": "Firmeza e flacidez", "responsibility": "Recebe os encaminhamentos iniciais relacionados a firmeza e flacidez da pele, organizando as informações para avaliação individual.", "bio": "Na etapa inicial, procura compreender a principal preocupação do cliente, há quanto tempo ela é percebida e quais aspectos precisam ser aprofundados presencialmente.", "photo": "mariana.jpg"},
    {"name": "Caio Nogueira", "role": "Dermatologia", "focus": "Manchas, melasma e sensibilidade", "responsibility": "É a referência de encaminhamento inicial para relatos de manchas, melasma, sensibilidade e vermelhidão, que precisam de avaliação profissional cuidadosa.", "bio": "Sua atuação no fluxo da DermaTech é acolher relatos relacionados a alterações de tonalidade e sensibilidade da pele.", "photo": "caio.jpg"},
    {"name": "Beatriz Almeida", "role": "Estética e cosmetologia", "focus": "Ressecamento e prevenção", "responsibility": "Organiza o primeiro atendimento de clientes que relatam ressecamento ou procuram orientação preventiva sobre cuidados com a pele.", "bio": "Dedica atenção à descrição dos hábitos de cuidado, à sensação de ressecamento e às expectativas do cliente.", "photo": "beatriz.jpg"},
    {"name": "Luiza Fernandes", "role": "Biomedicina estética", "focus": "Linhas, rugas e olheiras", "responsibility": "É a referência inicial para queixas envolvendo linhas, rugas e olheiras, direcionando o cliente para uma avaliação compatível com o relato apresentado.", "bio": "No primeiro contato, busca identificar qual aspecto mais incomoda o cliente e registrar há quanto tempo a queixa está presente.", "photo": "luiza.jpg"},
    {"name": "Rafael Mendes", "role": "Fisioterapia dermatofuncional", "focus": "Cicatrizes e textura", "responsibility": "Recebe os encaminhamentos iniciais relacionados a cicatrizes de acne e irregularidades de textura, apoiando a organização da avaliação presencial.", "bio": "Seu eixo de atendimento considera o histórico relatado, a região de interesse e a principal expectativa do cliente.", "photo": "rafael.jpg"},
]

COMPLAINTS = [
    "Acne e oleosidade", "Manchas e melasma", "Linhas e rugas",
    "Firmeza e flacidez da pele", "Ressecamento da pele", "Sensibilidade e vermelhidão",
    "Poros dilatados e textura irregular", "Olheiras", "Cicatrizes de acne",
    "Cuidados preventivos", "Outras queixas",
]

REVIEWS = [
    ("Juliana R.", "Gostei muito da forma como fui recebida desde o primeiro contato. A triagem foi simples de responder, mas me deu espaço para explicar o que estava me incomodando e há quanto tempo percebia isso."),
    ("Marcos A.", "O que mais gostei foi a organização do atendimento. As perguntas ajudaram a reunir informações que eu provavelmente esqueceria de comentar na hora."),
    ("Fernanda L.", "Desde a chegada, achei o ambiente tranquilo e acolhedor. Recebi orientações sobre como seria a avaliação e saí sabendo qual seria a próxima etapa."),
    ("Rafael C.", "Consegui consultar as opções de horário e enviar minha solicitação sem dificuldade. As informações sobre o profissional de referência estavam bem explicadas."),
]

APPOINTMENT_SLOTS = [
    "09:00", "09:45", "10:30", "11:15",
    "13:00", "13:45", "14:30", "15:15",
    "16:00", "16:45", "17:30", "18:15", "19:00",
]
FIXED_CLOSURES = {(1, 1), (12, 25)}

for key, default in [("bookings", []), ("result", None), ("result_input", None), ("booking_feedback", None), ("review_index", 0), ("page", "Início")]:
    if key not in st.session_state:
        st.session_state[key] = default

nav_items = ["Início", "Nova triagem", "Recepção", "Sobre nós"]
with st.container(key="top_navigation"):
    nav_cols = st.columns([2.5, 1.0, 1.35, 1.0, 1.0], vertical_alignment="center")
    with nav_cols[0]:
        st.markdown('<div class="brand">✳ DermaTech<small>CLÍNICA DE ESTÉTICA</small></div>', unsafe_allow_html=True)
    for col, nav_item in zip(nav_cols[1:], nav_items):
        with col:
            if st.button(
                nav_item,
                key=f"top_nav_{nav_item}",
                use_container_width=True,
                type="primary" if nav_item == st.session_state.page else "secondary",
            ):
                st.session_state.page = nav_item
                st.rerun()


def available_slots_for(day, professional):
    occupied = {
        item.get("horario")
        for item in st.session_state.bookings
        if item.get("data") == day.isoformat() and item.get("profissional") == professional
    }
    return [slot for slot in APPOINTMENT_SLOTS if slot not in occupied]


def is_unavailable_day(day, professional):
    if day <= date.today() or day.weekday() == 6 or (day.month, day.day) in FIXED_CLOSURES:
        return True
    return not available_slots_for(day, professional)


def first_available_day(professional, start=None, horizon=180):
    start = start or (date.today() + timedelta(days=1))
    for offset in range(horizon):
        candidate = start + timedelta(days=offset)
        if not is_unavailable_day(candidate, professional):
            return candidate
    return None


def render_reviews():
    idx = st.session_state.review_index % len(REVIEWS)
    name, comment = REVIEWS[idx]
    _, center, _ = st.columns([1.15, 5.7, 1.15])
    with center:
        st.markdown(
            f'''<div class="review-card">
                <div class="review-stars">★★★★★</div>
                <div class="review-label">Experiência de atendimento</div>
                <h3>{escape(name)}</h3>
                <p>“{escape(comment)}”</p>
                <div class="review-label">Relato demonstrativo da clínica</div>
            </div>''',
            unsafe_allow_html=True,
        )
        prev_col, count_col, next_col = st.columns([1, 4, 1], vertical_alignment="center")
        with prev_col:
            if st.button("←", key="review_prev", use_container_width=True):
                st.session_state.review_index = (idx - 1) % len(REVIEWS)
                st.rerun()
        with count_col:
            st.markdown(f'<div class="review-count">AVALIAÇÃO {idx + 1} DE {len(REVIEWS)}</div>', unsafe_allow_html=True)
        with next_col:
            if st.button("→", key="review_next", use_container_width=True):
                st.session_state.review_index = (idx + 1) % len(REVIEWS)
                st.rerun()


def render_home():
    st.markdown('<div class="hero"><div class="eyebrow">Cuidado que começa com escuta</div><h1>Tecnologia e cuidado para a saúde da sua pele.</h1><p>Uma clínica de estética que une avaliação especializada, tecnologia e atendimento personalizado para orientar seu próximo passo.</p></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    for col, (icon, title, desc) in zip((c1, c2, c3), [
        ("✳", "Triagem inteligente", "Informações organizadas por um sistema especialista."),
        ("♡", "Encaminhamento personalizado", "Direcionamento inicial conforme a queixa informada."),
        ("✓", "Avaliação profissional", "A decisão sobre cuidados acontece presencialmente."),
    ]):
        with col:
            st.markdown(f'<div class="card"><span class="tag">{icon}</span><h3>{title}</h3><p class="muted">{desc}</p></div>', unsafe_allow_html=True)

    st.markdown("## Principais queixas que atendemos")
    for row in (COMPLAINTS[:4], COMPLAINTS[4:8], COMPLAINTS[8:]):
        cols = st.columns(len(row))
        for col, item in zip(cols, row):
            with col:
                st.markdown(f'<div class="card" style="text-align:center"><b>{item}</b></div>', unsafe_allow_html=True)

    st.markdown("## O que nossos clientes dizem")
    render_reviews()


def render_triage_result(res, facts_input):
    fatos = res["fatos"]
    st.markdown("---")
    if not res.get("conclusao") or not fatos.get("area") or not fatos.get("profissional"):
        st.markdown('<div class="status-banner error">Não foi possível concluir com as informações fornecidas.</div>', unsafe_allow_html=True)
        return

    st.markdown('<div class="status-banner success">Triagem concluída: encaminhamento inicial identificado.</div>', unsafe_allow_html=True)
    st.markdown(f"### {res['conclusao']}")
    st.write(f"**Área sugerida:** {fatos.get('area')}")
    st.write(f"**Profissional de referência:** {fatos.get('profissional')}")
    st.write(f"**Tipo de avaliação:** {fatos.get('tipo_avaliacao')}")

    st.markdown("### Como chegamos a este resultado?")
    fact_items = [
        ("Queixa", "queixa"), ("Gravidade", "gravidade"), ("Duração", "duracao"),
        ("Sensibilidade", "sensibilidade"), ("Alergias", "alergia"), ("Avaliação anterior", "avaliacao_anterior"),
    ]
    if facts_input.get("alergia") == "Sim" and facts_input.get("alergia_detalhe"):
        fact_items.append(("Alergia informada", "alergia_detalhe"))
    for start in range(0, len(fact_items), 3):
        cols = st.columns(3)
        for col, (label, key) in zip(cols, fact_items[start:start + 3]):
            with col:
                st.markdown(f'<div class="fact-card"><small>{label}</small><strong>{escape(str(facts_input.get(key, "—")))}</strong></div>', unsafe_allow_html=True)

    st.markdown("### Rastreio do motor de inferência")
    with st.expander("Acompanhar o raciocínio passo a passo", expanded=True):
        initial_lines = "<br>".join(f"<b>{escape(str(k))}:</b> {escape(str(v))}" for k, v in facts_input.items() if v not in ("", None))
        st.markdown(f'<div class="trace-start"><span class="trace-kicker">PONTO DE PARTIDA · FATOS INFORMADOS</span><div>{initial_lines}</div></div>', unsafe_allow_html=True)
        for rule in res["regras"]:
            derived = rule.get("fatos_derivados") or {}
            derived_lines = "<br>".join(f"<b>{escape(str(k))}:</b> {escape(str(v))}" for k, v in derived.items()) if derived else "Confirmação de fatos já presentes."
            st.markdown(
                f'<div class="trace-step"><div><span class="trace-number">ETAPA {rule.get("etapa", 0):02d}</span>'
                f'<span class="rule-id">{escape(str(rule["id"]))}</span><b>{escape(str(rule["descricao"]))}</b></div>'
                f'<div><b>Condição:</b> <code>{escape(str(rule["condicao"]))}</code></div>'
                f'<div><b>Fato(s) derivado(s):</b><br>{derived_lines}</div>'
                f'<div class="trace-meta">Ciclo {rule.get("ciclo", 1)} · Fator heurístico {rule["cf"]:.0%}</div></div>',
                unsafe_allow_html=True,
            )
        st.markdown(
            f'<div class="trace-finish"><span class="trace-kicker">PONTO DE PARADA</span>'
            f'<b>Encadeamento concluído em {res.get("ciclos", 1)} ciclo(s)</b><br>'
            f'<strong>Conclusão: {escape(str(res.get("conclusao")))}</strong></div>',
            unsafe_allow_html=True,
        )

    st.markdown("### Solicitar agendamento de avaliação")
    matching = [p for p in STAFF if p["name"] == fatos.get("profissional")]
    default_staff = matching[0]["name"] if matching else STAFF[0]["name"]
    names = [p["name"] for p in STAFF] if default_staff == "Equipe DermaTech" else [default_staff] + [p["name"] for p in STAFF if p["name"] != default_staff]

    with st.container(key="booking_panel"):
        chosen = st.selectbox("Profissional de referência", names, key="booking_professional")
        date_key = "booking_date_picker"
        minimum_date = date.today() + timedelta(days=1)
        default_date = first_available_day(chosen)

        if default_date is None:
            st.warning("Não há datas disponíveis para este profissional.")
            chosen_date, slots = None, []
        else:
            current_date = st.session_state.get(date_key)
            if not isinstance(current_date, date) or is_unavailable_day(current_date, chosen):
                st.session_state[date_key] = default_date
            chosen_date = st.date_input("Data desejada", min_value=minimum_date, format="DD/MM/YYYY", key=date_key)
            slots = [] if is_unavailable_day(chosen_date, chosen) else available_slots_for(chosen_date, chosen)
            if not slots:
                st.warning("Não há atendimento disponível nesta data. Escolha outro dia.")

        if chosen_date and slots:
            with st.form("booking_form"):
                chosen_time = st.selectbox("Horário disponível", slots)
                c1, c2 = st.columns(2)
                with c1:
                    full_name = st.text_input("Nome completo", placeholder="Digite seu nome")
                    email = st.text_input("E-mail", placeholder="voce@exemplo.com")
                with c2:
                    phone = st.text_input("Telefone / WhatsApp", placeholder="(21) 99999-9999")
                    st.text_input("Data selecionada", value=chosen_date.strftime("%d/%m/%Y"), disabled=True)
                book = st.form_submit_button("Solicitar agendamento", use_container_width=True)
        else:
            book = False

        if book:
            email_ok = bool(re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email.strip()))
            phone_digits = re.sub(r"\D", "", phone)
            slots_now = available_slots_for(chosen_date, chosen) if chosen_date else []
            if not chosen_date or is_unavailable_day(chosen_date, chosen) or chosen_time not in slots_now:
                st.session_state.booking_feedback = {"type": "error", "message": "Solicitação não agendada. Horário indisponível."}
            elif not full_name.strip() or not email_ok or len(phone_digits) < 10:
                st.session_state.booking_feedback = {"type": "error", "message": "Solicitação não agendada. Confira nome, e-mail e telefone."}
            else:
                st.session_state.bookings.append({
                    "nome": full_name.strip(),
                    "email": email.strip(),
                    "telefone": phone.strip(),
                    "profissional": chosen,
                    "data": chosen_date.isoformat(),
                    "horario": chosen_time,
                    "area": fatos.get("area", "Avaliação geral"),
                })
                st.session_state.booking_feedback = {"type": "success", "message": "Solicitação agendada com sucesso."}

        feedback = st.session_state.get("booking_feedback")
        if feedback:
            css_class = "success" if feedback["type"] == "success" else "error"
            st.markdown(f'<div class="status-banner {css_class}">{escape(feedback["message"])}</div>', unsafe_allow_html=True)


def render_triage():
    st.markdown('<div class="eyebrow">Atendimento inicial</div><h1>Vamos conhecer melhor sua necessidade.</h1>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        queixa = st.selectbox("Qual é sua principal queixa?", COMPLAINTS, key="triage_queixa")
        gravidade = st.selectbox("Como você descreveria o incômodo?", ["Leve", "Moderada", "Intensa"], key="triage_gravidade")
        duracao = st.selectbox("Há quanto tempo percebe essa queixa?", ["Até 3 meses", "De 3 a 6 meses", "Mais de 6 meses", "Não sei informar"], key="triage_duracao")
    with c2:
        sensibilidade = st.selectbox("Sua pele costuma apresentar sensibilidade?", ["Não", "Sim", "Não sei informar"], key="triage_sensibilidade")
        alergia = st.selectbox("Possui alergias conhecidas que queira informar?", ["Não", "Sim", "Não sei informar"], key="triage_alergia")
        alergia_detalhe = ""
        if alergia == "Sim":
            alergia_detalhe = st.text_input("Qual alergia devemos registrar?", key="triage_alergia_detalhe")
        avaliacao_anterior = st.selectbox("Já realizou avaliação profissional para essa queixa?", ["Não", "Sim"], key="triage_avaliacao_anterior")

    if st.button("Analisar respostas", use_container_width=True, type="primary"):
        if alergia == "Sim" and not alergia_detalhe.strip():
            st.session_state.result = None
            st.markdown('<div class="allergy-warning"><strong>Informe sua alergia</strong><span>Escreva qual alergia deseja informar antes de analisar a triagem.</span></div>', unsafe_allow_html=True)
        else:
            facts_input = {
                "queixa": queixa, "gravidade": gravidade, "duracao": duracao,
                "sensibilidade": sensibilidade, "alergia": alergia,
                "alergia_detalhe": alergia_detalhe.strip() if alergia == "Sim" else "",
                "avaliacao_anterior": avaliacao_anterior,
            }
            st.session_state.result = executar_inferencia(facts_input)
            st.session_state.result_input = facts_input
            st.session_state.booking_feedback = None

    if st.session_state.result:
        render_triage_result(st.session_state.result, st.session_state.get("result_input", {}))


def render_reception():
    st.markdown('<div class="eyebrow">Área interna demonstrativa</div><h1>Recepção DermaTech</h1><p class="muted">Acompanhe as solicitações de avaliação realizadas nesta sessão.</p>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    stats = [
        ("SOLICITAÇÕES NESTA SESSÃO", len(st.session_state.bookings), "Registros demonstrativos"),
        ("AGENDAMENTOS", len(st.session_state.bookings), "Horários solicitados"),
        ("REGRAS CADASTRADAS", len(RULES), "Base de conhecimento"),
    ]
    for col, (label, value, foot) in zip((c1, c2, c3), stats):
        with col:
            st.markdown(f'<div class="stat-card"><small>{label}</small><strong>{value}</strong><span>{foot}</span></div>', unsafe_allow_html=True)

    st.markdown("### Solicitações recentes")
    if st.session_state.bookings:
        for booking in reversed(st.session_state.bookings):
            st.markdown(
                f'''<div class="card"><div class="rule-meta">{booking['data']} · {booking['horario']}</div>
                <h3>{escape(booking['nome'])}</h3><p class="muted">{escape(booking['email'])} · {escape(booking['telefone'])}</p>
                <b>{escape(booking['profissional'])}</b><p class="muted">{escape(booking['area'])}</p></div>''',
                unsafe_allow_html=True,
            )
    else:
        st.markdown('<div class="card"><h3>Nenhuma solicitação por aqui ainda.</h3><p class="muted">Quando uma avaliação for solicitada nesta sessão, ela aparecerá nesta lista.</p></div>', unsafe_allow_html=True)


def render_about():
    st.markdown('<div class="about-hero"><div class="eyebrow">SOBRE NÓS · DERMATECH</div><h1>Uma clínica feita para acolher.</h1><p>Reunimos profissionais de diferentes áreas e uma experiência de atendimento que combina escuta, informação e tecnologia.</p></div>', unsafe_allow_html=True)
    st.markdown("## Nossa equipe")
    for start in range(0, len(STAFF), 3):
        cols = st.columns(3)
        for col, person in zip(cols, STAFF[start:start + 3]):
            with col:
                subtitle = f'<div class="staff-role">{escape(person["role"])}</div>'
                description = f'<p class="muted">{escape(person["bio"])}</p><div class="responsibility-box"><b>Responsabilidade na clínica</b><p class="muted">{escape(person["responsibility"])}</p></div>'
                render_photo_card(person["photo"], person["name"], subtitle, description, person["focus"])


if st.session_state.page == "Início":
    render_home()
elif st.session_state.page == "Nova triagem":
    render_triage()
elif st.session_state.page == "Recepção":
    render_reception()
elif st.session_state.page == "Sobre nós":
    render_about()

st.markdown('<div class="site-footer"><div class="site-footer-inner"><div class="site-footer-brand">✳ DermaTech<small>CLÍNICA DE ESTÉTICA</small></div></div><div class="site-footer-meta">© 2026 DermaTech. Todos os direitos reservados.</div></div>', unsafe_allow_html=True)
