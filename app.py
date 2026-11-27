import base64
import json
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
    """Lê uma imagem local e retorna uma URI para cartões HTML com corte uniforme."""
    path = ASSETS / filename
    suffix = path.suffix.lower()
    mime = "image/png" if suffix == ".png" else "image/jpeg"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def render_photo_card(filename, title, subtitle, description, tag=None, wide=False):
    """Renderiza foto e conteúdo no mesmo cartão, com dimensões consistentes."""
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

# Identidade visual DermaTech — preserva a paleta e o estilo aprovados.
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap');
:root{--paper:#f7f6f1;--ink:#25372f;--forest:#29463a;--sage:#e5e9df;--clay:#bd7864;--line:#e4e2d9;--white:#fffefa;}
.stApp{background:var(--paper);color:var(--ink);font-family:'DM Sans',sans-serif;}
/* Navegação horizontal no topo: substitui a sidebar padrão do Streamlit. */
[data-testid="stSidebar"]{display:none!important;}
header[data-testid="stHeader"],.stAppHeader,[data-testid="stToolbar"],[data-testid="stDecoration"],#MainMenu,[data-testid="stStatusWidget"]{display:none!important;visibility:hidden!important;height:0!important;}
.stAppViewContainer .main .block-container{padding-top:1.15rem!important;max-width:1500px!important;}
.st-key-top_navigation{background:#29463a;border:1px solid #29463a;border-radius:18px;padding:.75rem 1rem;margin-bottom:1.55rem;box-shadow:0 8px 22px rgba(25,55,41,.10);}
.st-key-top_navigation [data-testid="stHorizontalBlock"]{align-items:center!important;gap:.5rem!important;}
.st-key-top_navigation .brand{padding:.25rem 0;color:#fff!important;}
.st-key-top_navigation .brand small{color:#dce8dd!important;}
.st-key-top_navigation [data-testid="stButton"]>button{width:100%!important;min-height:2.65rem!important;white-space:nowrap!important;background:rgba(255,255,255,.10)!important;color:#fff!important;-webkit-text-fill-color:#fff!important;border:1px solid rgba(255,255,255,.20)!important;border-radius:999px!important;}
.st-key-top_navigation [data-testid="stButton"]>button:hover{background:rgba(255,255,255,.20)!important;color:#fff!important;-webkit-text-fill-color:#fff!important;}
.st-key-top_navigation [data-testid="stButton"]>button[kind="primary"],.st-key-top_navigation [data-testid="stBaseButton-primary"]{background:#e5e9df!important;color:#29463a!important;-webkit-text-fill-color:#29463a!important;border-color:#e5e9df!important;}
.st-key-top_navigation [data-testid="stButton"]>button[kind="primary"] *, .st-key-top_navigation [data-testid="stBaseButton-primary"] *{color:#29463a!important;-webkit-text-fill-color:#29463a!important;}
h1,h2,h3{font-family:'Playfair Display',Georgia,serif!important;color:var(--ink)!important;}
h1{font-size:2.5rem!important;line-height:1.12!important;}
.brand{font-family:'DM Sans',sans-serif;font-weight:700;font-size:1.65rem;color:var(--forest);letter-spacing:-1px;}
.brand small{display:block;font-size:.57rem;letter-spacing:2px;color:#657168;font-weight:700;}
.eyebrow{color:var(--clay);font-size:.72rem;letter-spacing:2px;font-weight:700;text-transform:uppercase;}
.hero{background:linear-gradient(120deg,#e8e9df,#f7f3eb);border:1px solid var(--line);border-radius:24px;padding:2rem;margin:.5rem 0 1.2rem;}
.hero p{color:#58665d;max-width:680px;}
.card{background:var(--white);border:1px solid var(--line);border-radius:17px;padding:1rem 1.15rem;margin:.35rem 0;height:100%;}
.muted{color:#68746a;font-size:.9rem;}
.tag{display:inline-block;background:#e9eee5;color:#405d47;padding:.3rem .6rem;border-radius:8px;font-size:.75rem;font-weight:700;}
.rule-card{background:#fffefa;border:1px solid #e1e6dc;border-radius:15px;padding:1rem 1.05rem;margin:.45rem 0;min-height:175px;}
.rule-id{display:inline-block;background:#edf2eb;color:#405d47;border-radius:8px;padding:.32rem .55rem;font-size:.75rem;font-weight:700;margin-right:.5rem;}
.rule-meta{font-size:.7rem;color:#718074;font-weight:700;letter-spacing:1px;text-transform:uppercase;}
.knowledge-hero{background:linear-gradient(120deg,#e7ece3,#f8f5ee);border:1px solid #dce3d8;border-radius:20px;padding:1.4rem 1.6rem;margin:.8rem 0 1.2rem;}
.stat-card{background:#fffefa;border:1px solid var(--line);border-radius:15px;padding:1.05rem 1.2rem;min-height:110px;}
.stat-card small{font-size:.68rem;letter-spacing:1px;color:#68746a;font-weight:700;}
.stat-card strong{display:block;font-size:2rem;color:var(--forest);line-height:1.3;}
.stat-card span{font-size:.78rem;color:#68746a;}
.access-panel{background:#fffefa;border:1px solid var(--line);border-radius:17px;padding:1.2rem;margin:1rem 0;}
.photo-card{overflow:hidden;background:#fffefa;border:1px solid var(--line);border-radius:17px;padding:0;height:100%;display:flex;flex-direction:column;}
.photo-frame{width:100%;aspect-ratio:4/3;overflow:hidden;background:#e9e9e1;}
.photo-frame img{display:block;width:100%;height:100%;object-fit:cover;object-position:center;border-radius:0!important;}
.photo-frame.wide{aspect-ratio:16/9;}
.photo-copy{padding:1rem 1.1rem 1.15rem;flex:1;}
.photo-copy h3{margin:.45rem 0 .55rem;}
.home-experience-photo{width:100%;height:100%;min-height:270px;max-height:360px;object-fit:cover;border-radius:18px;}
.staff-role{font-size:.7rem;letter-spacing:1px;text-transform:uppercase;color:#9b6d5d;font-weight:700;}
.fact-card{background:#fffefa;border:1px solid var(--line);border-radius:13px;padding:.85rem 1rem;margin:.25rem 0;min-height:74px;}
.fact-card small{color:#68746a;font-size:.75rem;}
.fact-card strong{display:block;color:var(--ink);margin-top:.2rem;}
/* Todos os botões escuros usam texto branco com prioridade sobre o tema do Streamlit. */
div[data-testid="stButton"]>button,div[data-testid="stFormSubmitButton"]>button,div.stButton>button,div.stFormSubmitButton>button{
  background:#29463a!important;color:#ffffff!important;-webkit-text-fill-color:#ffffff!important;
  border:1px solid #29463a!important;border-radius:999px!important;font-weight:700!important;
  padding:.62rem 1.15rem!important;box-shadow:none!important;opacity:1!important;
}
div[data-testid="stButton"]>button *,div[data-testid="stFormSubmitButton"]>button *{color:#ffffff!important;-webkit-text-fill-color:#ffffff!important;opacity:1!important;}
div[data-testid="stButton"]>button:hover,div[data-testid="stFormSubmitButton"]>button:hover{background:#1e382d!important;border-color:#1e382d!important;color:#ffffff!important;-webkit-text-fill-color:#ffffff!important;}
[data-testid="stMetric"]{background:#fffefa;border:1px solid var(--line);padding:1rem;border-radius:14px;}
/* Contraste dos textos e controles no Streamlit */
.stApp,.stApp p,.stApp label,.stApp li,[data-testid="stWidgetLabel"],[data-testid="stWidgetLabel"] *{color:var(--ink)!important;}
[data-testid="stSelectbox"] label,[data-testid="stTextInput"] label,[data-testid="stDateInput"] label,[data-testid="stTextArea"] label,[data-testid="stNumberInput"] label,[data-testid="stMultiSelect"] label{color:#29463a!important;font-weight:700!important;opacity:1!important;}
[data-testid="stSelectbox"] [data-baseweb="select"]>div,[data-testid="stMultiSelect"] [data-baseweb="select"]>div,[data-testid="stTextInput"] input,[data-testid="stDateInput"] input,[data-testid="stTextArea"] textarea,[data-testid="stNumberInput"] input{background:#fffefa!important;color:#25372f!important;border:1px solid #c9d1c5!important;border-radius:10px!important;}
[data-testid="stSelectbox"] [data-baseweb="select"] *,[data-testid="stMultiSelect"] [data-baseweb="select"] *{color:#25372f!important;opacity:1!important;}
[role="listbox"],[role="option"]{background:#fffefa!important;color:#25372f!important;}
[role="option"]:hover{background:#e8eee5!important;}
[data-testid="stForm"]{background:#fffefa!important;border:1px solid #d9ded4!important;border-radius:16px!important;padding:1rem!important;}
[data-testid="stCaptionContainer"],[data-testid="stCaptionContainer"] p{color:#68746a!important;}
[data-testid="stDataFrame"]{border:1px solid var(--line);border-radius:12px;overflow:hidden;}
.about-hero{background:linear-gradient(125deg,#e8ece4,#f5f0e7);border:1px solid var(--line);border-radius:24px;padding:2rem 2.2rem;margin:.5rem 0 1.4rem;}
.about-hero p{max-width:none!important;width:100%;color:#526258;font-size:1rem;line-height:1.8;}
.about-lead{font-size:1.02rem;line-height:1.8;color:#526258;max-width:none!important;width:100%;}
.about-values{background:#fffefa;border:1px solid var(--line);border-radius:16px;padding:1rem 1.1rem;height:100%;}
.about-values h3{margin:.5rem 0;}
.staff-intro{max-width:none!important;width:100%;line-height:1.75;color:#68746a;margin-bottom:1.1rem;}
.photo-copy p{line-height:1.65;}
.environment-note{font-size:.78rem;color:#68746a;margin-top:.5rem;}
.proposal-card{background:#fffefa;border:1px solid var(--line);border-radius:18px;padding:1.2rem 1.35rem;margin:.5rem 0;height:100%;}
.proposal-card h3{margin:.4rem 0 .55rem;}
.proposal-card p{line-height:1.8;color:#526258;margin:.65rem 0;}
.proposal-highlight{border-top:1px solid var(--line);padding-top:.9rem!important;margin-top:1rem!important;color:var(--forest)!important;font-weight:700;}
.responsibility-box{background:#f4f5ef;border:1px solid #e6e9e0;border-radius:12px;padding:.8rem .9rem;margin:.8rem 0;}
.proposal-step{display:flex;gap:.85rem;align-items:flex-start;background:#fffefa;border:1px solid var(--line);border-radius:14px;padding:1rem;margin:.45rem 0;}
.proposal-step .number{flex:0 0 2rem;height:2rem;border-radius:10px;background:#e9eee5;color:#405d47;display:flex;align-items:center;justify-content:center;font-weight:700;}
.review-wrap{max-width:850px;margin:0 auto;}
.review-card{background:#fffefa;border:1px solid #dfe5da;border-radius:18px;padding:1.35rem 1.55rem;box-shadow:0 8px 24px rgba(37,55,47,.06);min-height:210px;}
.review-card .review-stars{color:#b8873e;font-size:1.05rem;letter-spacing:2px;margin-bottom:.5rem;}
.review-card h3{font-family:'DM Sans',sans-serif!important;font-size:1.02rem!important;margin:.2rem 0 .55rem!important;color:#29463a!important;}
.review-card p{color:#43564a;line-height:1.82;font-size:.95rem;margin:.35rem 0 .7rem;}
.review-label{font-size:.68rem;color:#77877a;letter-spacing:1px;text-transform:uppercase;font-weight:700;}
.st-key-review_controls{max-width:850px;margin:.7rem auto 0!important;}
.st-key-review_controls [data-testid="stHorizontalBlock"]{align-items:center!important;gap:1rem!important;}
.st-key-review_controls [data-testid="stButton"]{display:flex!important;justify-content:center!important;}
.st-key-review_controls [data-testid="stButton"]>button{width:3rem!important;min-width:3rem!important;height:2.65rem!important;min-height:2.65rem!important;padding:0!important;border-radius:12px!important;background:#29463a!important;background-color:#29463a!important;color:#ffffff!important;-webkit-text-fill-color:#ffffff!important;border:1px solid #29463a!important;box-shadow:none!important;opacity:1!important;}
.st-key-review_controls [data-testid="stButton"]>button:hover{background:#3c624d!important;background-color:#3c624d!important;border-color:#3c624d!important;color:#ffffff!important;-webkit-text-fill-color:#ffffff!important;}
.st-key-review_controls [data-testid="stButton"]>button *{color:#ffffff!important;-webkit-text-fill-color:#ffffff!important;opacity:1!important;}
.review-count{text-align:center;color:#58705d;font-size:.72rem;font-weight:700;letter-spacing:1.15px;padding:.65rem .35rem;}
.site-footer-inner b{color:#fff!important;}
@media(max-width:700px){.site-footer{padding:1.4rem 1.2rem;border-radius:18px;}.review-card{padding:1rem;}}
footer{visibility:hidden!important;}
.site-footer{margin-top:3rem;padding:1.9rem 2rem 1.2rem;background:#29463a;border:1px solid #29463a;border-radius:22px;color:#eef4ed;}
.site-footer-inner{display:flex;justify-content:space-between;align-items:flex-start;gap:2rem;flex-wrap:wrap;}
.site-footer-brand{font-family:'DM Sans',sans-serif;font-weight:700;font-size:1.35rem;color:#fff!important;letter-spacing:-.5px;}
.site-footer-brand small{display:block;font-size:.57rem;letter-spacing:2px;color:#d4e1d5!important;font-weight:700;margin-top:.2rem;}
.site-footer-copy{font-size:.84rem;line-height:1.75;color:#e1ebe1!important;max-width:520px;margin-top:.55rem;}
.site-footer-meta{font-size:.72rem;color:#cbd9cc!important;margin-top:1.15rem;padding-top:.85rem;border-top:1px solid rgba(255,255,255,.22);}
.about-section{margin:1.6rem 0 2rem;}
.about-section-intro{max-width:none!important;width:100%;color:#5d6b61;font-size:1rem;line-height:1.85;margin:.25rem 0 1.1rem;}
.about-hero-title{font-family:'Playfair Display',Georgia,serif!important;font-size:2.65rem!important;line-height:1.15!important;color:var(--ink)!important;margin:.55rem 0 .8rem!important;}
@media(max-width:900px){[data-testid="stSidebar"] [data-testid="stButton"]>button{padding:.58rem .7rem!important;}}
@media(max-width:900px){.st-key-top_navigation [data-testid="stHorizontalBlock"]{flex-wrap:wrap!important;}.st-key-top_navigation [data-testid="column"]{min-width:118px!important;flex:1 1 118px!important;}}
@media(max-width:700px){h1{font-size:2rem!important;}.hero{padding:1.25rem;}.rule-card{min-height:unset;}.photo-frame{aspect-ratio:4/3;}.home-experience-photo{min-height:220px;max-height:280px;}.stAppViewContainer .main .block-container{padding-left:1rem!important;padding-right:1rem!important;}}

/* Correcoes finais de contraste para alertas e componentes BaseWeb/Streamlit. */
[data-testid="stAlert"] { border-radius: 13px !important; border: 1px solid transparent !important; }
[data-testid="stAlert"] [data-testid="stMarkdownContainer"] p,
[data-testid="stAlert"] p,
[data-testid="stAlert"] span,
[data-testid="stAlert"] [data-testid="stIconMaterial"] { color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; opacity: 1 !important; }
[data-testid="stAlert"] svg { fill: #ffffff !important; color: #ffffff !important; }
[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stMultiSelect"] [data-baseweb="select"] > div { background: #fffefa !important; background-color: #fffefa !important; border: 1px solid #c9d1c5 !important; border-radius: 10px !important; box-shadow: none !important; min-height: 44px !important; }
[data-testid="stSelectbox"] [data-baseweb="select"] [role="combobox"],
[data-testid="stSelectbox"] [data-baseweb="select"] input,
[data-testid="stSelectbox"] [data-baseweb="select"] span,
[data-testid="stMultiSelect"] [data-baseweb="select"] [role="combobox"],
[data-testid="stMultiSelect"] [data-baseweb="select"] input,
[data-testid="stMultiSelect"] [data-baseweb="select"] span { color: #25372f !important; -webkit-text-fill-color: #25372f !important; opacity: 1 !important; background: transparent !important; }
[data-testid="stSelectbox"] [data-baseweb="select"] svg,
[data-testid="stDateInput"] svg { color: #526258 !important; fill: #526258 !important; }
[data-testid="stTextInput"] input,
[data-testid="stDateInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea { color: #25372f !important; -webkit-text-fill-color: #25372f !important; background: #fffefa !important; border: 1px solid #c9d1c5 !important; border-radius: 10px !important; box-shadow: none !important; }
[data-testid="stDateInput"] [data-baseweb="input"] > div { background: #fffefa !important; border: 1px solid #c9d1c5 !important; border-radius: 10px !important; box-shadow: none !important; }
[data-testid="stDateInput"] [data-baseweb="input"] input { border: 0 !important; }
[data-baseweb="popover"] [role="listbox"], [data-baseweb="popover"] [role="option"] { background: #fffefa !important; color: #25372f !important; }
[data-baseweb="popover"] [role="option"]:hover { background: #e8eee5 !important; }
/* Alertas próprias: texto branco legível sobre verde ou vinho. */
.status-banner { border-radius: 13px; padding: 1rem 1.2rem; margin: .8rem 0 1.1rem; font-weight: 700; line-height: 1.55; }
.status-banner.success { background: #173f32; border: 1px solid #173f32; color: #ffffff !important; }
.status-banner.error { background: #873d43; border: 1px solid #873d43; color: #ffffff !important; }
.status-banner * { color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; }
/* Formulário de agendamento menor e centralizado, sem o bloco largo/desalinhado. */
.st-key-booking_panel { max-width: 1120px; width: 100%; margin: .4rem auto 1.5rem !important; background: #fffefa; border: 1px solid #dfe5da; border-radius: 20px; padding: 1.15rem 1.3rem !important; }
.st-key-booking_panel [data-testid="stForm"] { background: transparent !important; border: 0 !important; border-radius: 0 !important; padding: .15rem !important; }
.st-key-booking_panel [data-testid="stSelectbox"] [data-baseweb="select"] > div { min-height: 46px !important; }
.st-key-booking_panel [data-testid="stHorizontalBlock"] { gap: 1rem !important; }
@media(max-width:700px) { .st-key-booking_panel { padding: .85rem !important; border-radius: 16px; } .status-banner { padding: .85rem 1rem; } }

/* Navegação compacta e legível em celulares: marca acima, links em grade 2x2. */
@media(max-width:700px){
  .st-key-top_navigation{
    padding:.75rem!important;
    margin-bottom:1rem!important;
    border-radius:15px!important;
  }
  .st-key-top_navigation [data-testid="stHorizontalBlock"]{
    display:grid!important;
    grid-template-columns:repeat(2,minmax(0,1fr))!important;
    align-items:center!important;
    gap:.45rem!important;
  }
  .st-key-top_navigation [data-testid="column"]{
    width:auto!important;
    min-width:0!important;
    max-width:none!important;
    flex:unset!important;
  }
  .st-key-top_navigation [data-testid="column"]:first-child{
    grid-column:1 / -1!important;
    padding-bottom:.25rem!important;
  }
  .st-key-top_navigation [data-testid="stButton"]>button{
    width:100%!important;
    min-height:2.7rem!important;
    padding:.55rem .45rem!important;
    white-space:normal!important;
    line-height:1.2!important;
    font-size:.86rem!important;
  }
  .stAppViewContainer .main .block-container{
    padding-left:.85rem!important;
    padding-right:.85rem!important;
    padding-top:.8rem!important;
  }
  .st-key-booking_panel{
    max-width:100%!important;
    width:100%!important;
    padding:.8rem!important;
    margin:.35rem 0 1rem!important;
  }
  .st-key-booking_panel [data-testid="stHorizontalBlock"]{
    flex-direction:column!important;
    gap:.35rem!important;
  }
  .st-key-booking_panel [data-testid="column"]{
    width:100%!important;
    min-width:100%!important;
    max-width:100%!important;
    flex:1 1 100%!important;
  }
  .st-key-booking_panel [data-testid="stTextInput"],
  .st-key-booking_panel [data-testid="stDateInput"],
  .st-key-booking_panel [data-testid="stSelectbox"]{
    width:100%!important;
  }
  .st-key-booking_panel [data-testid="stFormSubmitButton"]>button{
    width:100%!important;
    min-height:2.9rem!important;
    white-space:normal!important;
  }
  .status-banner{
    font-size:.9rem!important;
    padding:.85rem .95rem!important;
    overflow-wrap:anywhere!important;
  }
}
@media(max-width:430px){
  .st-key-top_navigation .brand{font-size:1.42rem!important;}
  .st-key-top_navigation .brand small{font-size:.52rem!important;}
  .st-key-top_navigation [data-testid="stButton"]>button{font-size:.8rem!important;}
  .st-key-booking_panel [data-testid="stForm"]{padding:0!important;}
}


.knowledge-back-action{margin-top:1.2rem;padding-top:.4rem;border-top:1px solid var(--line);}


/* Ajustes específicos das duas áreas da captura mobile: navegação e carrossel. */
@media (max-width: 700px) {
  /* A marca ocupa uma linha inteira; os quatro links ficam em uma grade 2 x 2 abaixo. */
  .st-key-top_navigation [data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-wrap: wrap !important;
    align-items: center !important;
    gap: .45rem .5rem !important;
  }
  .st-key-top_navigation [data-testid="stHorizontalBlock"] > [data-testid="column"]:first-child {
    flex: 0 0 100% !important;
    width: 100% !important;
    max-width: 100% !important;
    min-width: 100% !important;
  }
  .st-key-top_navigation [data-testid="stHorizontalBlock"] > [data-testid="column"]:not(:first-child) {
    flex: 1 1 calc(50% - .5rem) !important;
    width: calc(50% - .5rem) !important;
    max-width: calc(50% - .5rem) !important;
    min-width: 0 !important;
  }
  .st-key-top_navigation [data-testid="column"] {
    padding: 0 !important;
  }
  .st-key-top_navigation [data-testid="stButton"] > button {
    width: 100% !important;
    min-height: 2.65rem !important;
    padding: .55rem .35rem !important;
    white-space: normal !important;
    line-height: 1.15 !important;
    font-size: .82rem !important;
    text-align: center !important;
  }

  /* Setas e contador permanecem na mesma linha em celulares. */
  .st-key-review_controls [data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns: 2.75rem minmax(0, 1fr) 2.75rem !important;
    align-items: center !important;
    gap: .45rem !important;
    flex-wrap: nowrap !important;
  }
  .st-key-review_controls [data-testid="stHorizontalBlock"] > [data-testid="column"] {
    width: auto !important;
    min-width: 0 !important;
    max-width: none !important;
    flex: unset !important;
    padding: 0 !important;
  }
  .st-key-review_controls [data-testid="stButton"] {
    width: 100% !important;
  }
  .st-key-review_controls [data-testid="stButton"] > button {
    width: 2.75rem !important;
    min-width: 2.75rem !important;
    height: 2.75rem !important;
    min-height: 2.75rem !important;
    padding: 0 !important;
    border-radius: 12px !important;
    background: #29463a !important;
    background-color: #29463a !important;
    border: 1px solid #29463a !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-size: 1.2rem !important;
  }
  .st-key-review_controls .review-count {
    width: 100% !important;
    white-space: nowrap !important;
    text-align: center !important;
    font-size: .64rem !important;
    letter-spacing: .06em !important;
    padding: .45rem .1rem !important;
  }
}
@media (max-width: 380px) {
  .st-key-top_navigation [data-testid="stButton"] > button {
    font-size: .76rem !important;
  }
  .st-key-review_controls [data-testid="stHorizontalBlock"] {
    grid-template-columns: 2.45rem minmax(0, 1fr) 2.45rem !important;
    gap: .3rem !important;
  }
  .st-key-review_controls [data-testid="stButton"] > button {
    width: 2.45rem !important;
    min-width: 2.45rem !important;
    height: 2.45rem !important;
    min-height: 2.45rem !important;
  }
}


/* Menu sanduíche e carrossel com setas de alto contraste em celulares. */
.st-key-mobile_menu_toggle {display:none!important;}
.st-key-mobile_menu_toggle [data-testid="stButton"]>button{
  background:#e5e9df!important;background-color:#e5e9df!important;
  color:#29463a!important;-webkit-text-fill-color:#29463a!important;
  border:1px solid rgba(255,255,255,.55)!important;border-radius:12px!important;
  width:2.85rem!important;min-width:2.85rem!important;height:2.85rem!important;min-height:2.85rem!important;
  padding:0!important;font-size:1.35rem!important;font-weight:800!important;
}
.st-key-mobile_navigation{
  background:#29463a!important;border:1px solid rgba(255,255,255,.2)!important;
  border-radius:14px!important;padding:.7rem!important;margin:-.85rem 0 1.15rem!important;
}
.st-key-mobile_navigation [data-testid="stButton"]>button{
  width:100%!important;min-height:2.7rem!important;
  background:rgba(255,255,255,.12)!important;background-color:rgba(255,255,255,.12)!important;
  color:#fff!important;-webkit-text-fill-color:#fff!important;
  border:1px solid rgba(255,255,255,.26)!important;border-radius:999px!important;
  white-space:normal!important;
}
.st-key-mobile_navigation [data-testid="stButton"]>button[kind="primary"]{
  background:#e5e9df!important;background-color:#e5e9df!important;
  color:#29463a!important;-webkit-text-fill-color:#29463a!important;
}
.st-key-review_controls [data-testid="stButton"]>button,
.st-key-review_prev [data-testid="stButton"]>button,
.st-key-review_next [data-testid="stButton"]>button{
  background:#29463a!important;background-color:#29463a!important;
  color:#fff!important;-webkit-text-fill-color:#fff!important;
  border:1px solid #29463a!important;border-radius:12px!important;
  min-width:3rem!important;width:3rem!important;height:2.8rem!important;min-height:2.8rem!important;
  opacity:1!important;font-size:1.35rem!important;font-weight:800!important;padding:0!important;
}
.st-key-review_controls [data-testid="stButton"]>button *,
.st-key-review_prev [data-testid="stButton"]>button *,
.st-key-review_next [data-testid="stButton"]>button *{
  color:#fff!important;-webkit-text-fill-color:#fff!important;opacity:1!important;
}
@media(max-width:700px){
  .st-key-top_navigation{
    padding:.75rem .85rem!important;
    margin-bottom:1rem!important;
  }
  .st-key-top_navigation [data-testid="stHorizontalBlock"]{
    display:flex!important;align-items:center!important;flex-wrap:nowrap!important;gap:.5rem!important;
  }
  .st-key-top_navigation [data-testid="stHorizontalBlock"]>[data-testid="column"]:first-child{
    flex:1 1 auto!important;width:auto!important;min-width:0!important;max-width:none!important;
  }
  .st-key-top_navigation [data-testid="stHorizontalBlock"]>[data-testid="column"]:nth-child(2),
  .st-key-top_navigation [data-testid="stHorizontalBlock"]>[data-testid="column"]:nth-child(3),
  .st-key-top_navigation [data-testid="stHorizontalBlock"]>[data-testid="column"]:nth-child(4),
  .st-key-top_navigation [data-testid="stHorizontalBlock"]>[data-testid="column"]:nth-child(5){
    display:none!important;
  }
  .st-key-top_navigation [data-testid="stHorizontalBlock"]>[data-testid="column"]:last-child{
    display:flex!important;flex:0 0 3rem!important;width:3rem!important;min-width:3rem!important;max-width:3rem!important;
  }
  .st-key-mobile_menu_toggle{display:block!important;}
  .st-key-mobile_navigation{display:block!important;}
  .st-key-review_controls{max-width:100%!important;width:100%!important;margin:.65rem auto 0!important;}
  .st-key-review_controls [data-testid="stHorizontalBlock"]{
    display:grid!important;grid-template-columns:3rem minmax(0,1fr) 3rem!important;
    align-items:center!important;gap:.4rem!important;flex-wrap:nowrap!important;
  }
  .st-key-review_controls [data-testid="stHorizontalBlock"]>[data-testid="column"]{
    width:auto!important;min-width:0!important;max-width:none!important;flex:unset!important;padding:0!important;
  }
  .st-key-review_controls [data-testid="stButton"]>button,
  .st-key-review_prev [data-testid="stButton"]>button,
  .st-key-review_next [data-testid="stButton"]>button{
    background:#29463a!important;background-color:#29463a!important;
    color:#fff!important;-webkit-text-fill-color:#fff!important;
    border:1px solid #29463a!important;
    width:2.85rem!important;min-width:2.85rem!important;height:2.85rem!important;min-height:2.85rem!important;
    font-size:1.45rem!important;line-height:1!important;
  }
  .st-key-review_controls .review-count{
    width:100%!important;white-space:nowrap!important;text-align:center!important;
    color:#536358!important;font-size:.68rem!important;letter-spacing:.06em!important;font-weight:700!important;
  }
}
@media(max-width:380px){
  .st-key-top_navigation .brand{font-size:1.3rem!important;}
  .st-key-top_navigation .brand small{font-size:.5rem!important;}
  .st-key-review_controls [data-testid="stHorizontalBlock"]{grid-template-columns:2.55rem minmax(0,1fr) 2.55rem!important;gap:.25rem!important;}
  .st-key-review_controls [data-testid="stButton"]>button{width:2.5rem!important;min-width:2.5rem!important;height:2.5rem!important;min-height:2.5rem!important;}
}


/* Correção final mobile: cabeçalho independente e controles com texto visível. */
.st-key-mobile_navigation_header { display:none!important; }
.st-key-mobile_navigation { display:none!important; }
.st-key-review_controls .stButton button,
.st-key-review_controls [data-testid="stButton"] button,
.st-key-review_controls button {
  background:#fffefa!important;
  background-color:#fffefa!important;
  color:#111111!important;
  -webkit-text-fill-color:#111111!important;
  border:1px solid #d2d6ce!important;
  box-shadow:0 1px 3px rgba(20,35,25,.08)!important;
  opacity:1!important;
  text-shadow:none!important;
}
.st-key-review_controls .stButton button *,
.st-key-review_controls [data-testid="stButton"] button *,
.st-key-review_controls button * {
  color:#111111!important;
  -webkit-text-fill-color:#111111!important;
  opacity:1!important;
}
@media(max-width:700px){
  .st-key-top_navigation {display:none!important;}
  .st-key-mobile_navigation_header{
    display:block!important;
    visibility:visible!important;
    width:100%!important;
    max-width:100%!important;
    overflow:visible!important;
    background:#29463a!important;
    border:1px solid #29463a!important;
    border-radius:16px!important;
    padding:.75rem .8rem!important;
    margin:0 0 1rem!important;
    box-shadow:0 7px 20px rgba(25,55,41,.12)!important;
  }
  .st-key-mobile_navigation_header [data-testid="stHorizontalBlock"]{
    display:flex!important;
    flex-wrap:nowrap!important;
    align-items:center!important;
    justify-content:space-between!important;
    gap:.5rem!important;
    width:100%!important;
  }
  .st-key-mobile_navigation_header [data-testid="column"]:first-child{
    flex:1 1 auto!important;
    width:auto!important;
    min-width:0!important;
    max-width:none!important;
    display:block!important;
  }
  .st-key-mobile_navigation_header [data-testid="column"]:last-child{
    flex:0 0 3.2rem!important;
    width:3.2rem!important;
    min-width:3.2rem!important;
    max-width:3.2rem!important;
    display:block!important;
  }
  .st-key-mobile_navigation_header .brand{
    display:block!important;
    visibility:visible!important;
    color:#ffffff!important;
    font-size:1.42rem!important;
    line-height:1.25!important;
    white-space:nowrap!important;
  }
  .st-key-mobile_navigation_header .brand small{
    display:block!important;
    color:#dce8dd!important;
    font-size:.52rem!important;
    letter-spacing:1.6px!important;
    white-space:nowrap!important;
  }
  .st-key-mobile_navigation_header .st-key-mobile_menu_toggle,
  .st-key-mobile_navigation_header [class*="st-key-mobile_menu_toggle"]{
    display:block!important;
    visibility:visible!important;
    width:3.1rem!important;
    min-width:3.1rem!important;
    max-width:3.1rem!important;
    margin:0!important;
    padding:0!important;
  }
  .st-key-mobile_navigation_header [data-testid="stButton"]{
    display:block!important;
    width:3.1rem!important;
    min-width:3.1rem!important;
    visibility:visible!important;
  }
  .st-key-mobile_navigation_header [data-testid="stButton"] button,
  .st-key-mobile_navigation_header button{
    display:flex!important;
    align-items:center!important;
    justify-content:center!important;
    width:3rem!important;
    min-width:3rem!important;
    max-width:3rem!important;
    height:3rem!important;
    min-height:3rem!important;
    padding:0!important;
    margin:0!important;
    overflow:visible!important;
    border-radius:12px!important;
    background:#fffefa!important;
    background-color:#fffefa!important;
    color:#111111!important;
    -webkit-text-fill-color:#111111!important;
    border:1px solid #d9ded5!important;
    font-family:Arial,sans-serif!important;
    font-size:1.65rem!important;
    font-weight:700!important;
    line-height:1!important;
    opacity:1!important;
  }
  .st-key-mobile_navigation_header [data-testid="stButton"] button *,
  .st-key-mobile_navigation_header button *{
    color:#111111!important;
    -webkit-text-fill-color:#111111!important;
    opacity:1!important;
  }
  .st-key-mobile_navigation{
    display:block!important;
    visibility:visible!important;
    width:100%!important;
    background:#29463a!important;
    border:1px solid rgba(255,255,255,.22)!important;
    border-radius:14px!important;
    padding:.65rem!important;
    margin:-.35rem 0 1.1rem!important;
  }
  .st-key-mobile_navigation [data-testid="stHorizontalBlock"]{
    display:grid!important;
    grid-template-columns:repeat(2,minmax(0,1fr))!important;
    gap:.45rem!important;
  }
  .st-key-mobile_navigation [data-testid="column"]{
    width:auto!important;
    min-width:0!important;
    max-width:none!important;
    flex:unset!important;
    padding:0!important;
  }
  .st-key-mobile_navigation [data-testid="stButton"] button{
    width:100%!important;
    min-height:2.65rem!important;
    padding:.5rem .3rem!important;
    border-radius:999px!important;
    white-space:normal!important;
    color:#ffffff!important;
    -webkit-text-fill-color:#ffffff!important;
    background:rgba(255,255,255,.12)!important;
    border:1px solid rgba(255,255,255,.25)!important;
    font-size:.84rem!important;
  }
  .st-key-mobile_navigation [data-testid="stButton"] button[kind="primary"]{
    color:#29463a!important;
    -webkit-text-fill-color:#29463a!important;
    background:#e5e9df!important;
    border-color:#e5e9df!important;
  }
  /* Carrossel: branco com chevron preto bem visível. */
  .st-key-review_controls{
    display:block!important;
    width:100%!important;
    max-width:100%!important;
    margin:.6rem auto 0!important;
  }
  .st-key-review_controls [data-testid="stHorizontalBlock"]{
    display:grid!important;
    grid-template-columns:2.8rem minmax(0,1fr) 2.8rem!important;
    align-items:center!important;
    gap:.45rem!important;
    width:100%!important;
  }
  .st-key-review_controls [data-testid="column"]{
    min-width:0!important;
    width:auto!important;
    max-width:none!important;
    flex:unset!important;
    padding:0!important;
  }
  .st-key-review_controls [data-testid="stButton"],
  .st-key-review_controls .stButton{
    width:2.8rem!important;
    min-width:2.8rem!important;
    max-width:2.8rem!important;
    margin:0 auto!important;
  }
  .st-key-review_controls [data-testid="stButton"] button,
  .st-key-review_controls .stButton button,
  .st-key-review_controls button{
    display:flex!important;
    align-items:center!important;
    justify-content:center!important;
    width:2.8rem!important;
    min-width:2.8rem!important;
    max-width:2.8rem!important;
    height:2.8rem!important;
    min-height:2.8rem!important;
    padding:0!important;
    border-radius:11px!important;
    background:#fffefa!important;
    background-color:#fffefa!important;
    color:#111111!important;
    -webkit-text-fill-color:#111111!important;
    border:1px solid #cfd5cc!important;
    font-family:Arial,sans-serif!important;
    font-size:1.55rem!important;
    font-weight:700!important;
    line-height:1!important;
    text-shadow:none!important;
    opacity:1!important;
  }
  .st-key-review_controls [data-testid="stButton"] button *,
  .st-key-review_controls .stButton button *,
  .st-key-review_controls button *{
    color:#111111!important;
    -webkit-text-fill-color:#111111!important;
    opacity:1!important;
    text-shadow:none!important;
  }
  .st-key-review_controls .review-count{
    display:block!important;
    width:100%!important;
    text-align:center!important;
    white-space:nowrap!important;
    color:#536358!important;
    font-size:.68rem!important;
    font-weight:700!important;
    letter-spacing:.055em!important;
    padding:.4rem 0!important;
  }
}
@media(max-width:390px){
  .st-key-mobile_navigation_header{padding:.65rem!important;}
  .st-key-mobile_navigation_header .brand{font-size:1.28rem!important;}
  .st-key-mobile_navigation_header [data-testid="column"]:last-child{flex-basis:3rem!important;width:3rem!important;min-width:3rem!important;max-width:3rem!important;}
  .st-key-mobile_navigation_header [data-testid="stButton"] button{width:2.8rem!important;min-width:2.8rem!important;max-width:2.8rem!important;height:2.8rem!important;min-height:2.8rem!important;}
  .st-key-review_controls [data-testid="stHorizontalBlock"]{grid-template-columns:2.6rem minmax(0,1fr) 2.6rem!important;gap:.3rem!important;}
  .st-key-review_controls [data-testid="stButton"] button,.st-key-review_controls .stButton button{width:2.6rem!important;min-width:2.6rem!important;max-width:2.6rem!important;height:2.6rem!important;min-height:2.6rem!important;}
}


/* Override final: alinha o botão do menu dentro do cabeçalho verde, sem ultrapassar a borda. */
@media (max-width: 700px) {
  .st-key-mobile_navigation_header {
    box-sizing: border-box !important;
    width: 100% !important;
    max-width: 100% !important;
    padding: .7rem .72rem !important;
    overflow: hidden !important;
  }
  .st-key-mobile_navigation_header [data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns: minmax(0, 1fr) 2.55rem !important;
    column-gap: .45rem !important;
    align-items: center !important;
    width: 100% !important;
    max-width: 100% !important;
    margin: 0 !important;
    box-sizing: border-box !important;
  }
  .st-key-mobile_navigation_header [data-testid="column"] {
    box-sizing: border-box !important;
    width: auto !important;
    min-width: 0 !important;
    max-width: 100% !important;
    flex: none !important;
    padding: 0 !important;
    margin: 0 !important;
  }
  .st-key-mobile_navigation_header [data-testid="column"]:last-child {
    width: 2.55rem !important;
    min-width: 2.55rem !important;
    max-width: 2.55rem !important;
    justify-self: end !important;
  }
  .st-key-mobile_navigation_header [data-testid="stButton"],
  .st-key-mobile_navigation_header .stButton {
    display: block !important;
    box-sizing: border-box !important;
    width: 2.4rem !important;
    min-width: 2.4rem !important;
    max-width: 2.4rem !important;
    margin: 0 !important;
    padding: 0 !important;
  }
  .st-key-mobile_navigation_header [data-testid="stButton"] > button,
  .st-key-mobile_navigation_header .stButton > button,
  .st-key-mobile_navigation_header button {
    box-sizing: border-box !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 2.35rem !important;
    min-width: 2.35rem !important;
    max-width: 2.35rem !important;
    height: 2.55rem !important;
    min-height: 2.55rem !important;
    max-height: 2.55rem !important;
    margin: 0 !important;
    padding: 0 !important;
    transform: none !important;
    position: relative !important;
    right: auto !important;
    background: #fffefa !important;
    background-color: #fffefa !important;
    color: #111111 !important;
    -webkit-text-fill-color: #111111 !important;
    border: 1px solid #d9ded5 !important;
    border-radius: 11px !important;
    font-family: Arial, sans-serif !important;
    font-size: 1.35rem !important;
    font-weight: 700 !important;
    line-height: 1 !important;
    overflow: hidden !important;
  }
  .st-key-mobile_navigation_header [data-testid="stButton"] > button *,
  .st-key-mobile_navigation_header button * {
    color: #111111 !important;
    -webkit-text-fill-color: #111111 !important;
  }
}


/* Menu mobile mais nítido e com microinterações suaves. */
.st-key-mobile_navigation [data-testid="stButton"]>button{
  background:rgba(255,255,255,.20)!important;
  background-color:rgba(255,255,255,.20)!important;
  color:#ffffff!important;
  -webkit-text-fill-color:#ffffff!important;
  border:1px solid rgba(255,255,255,.34)!important;
  transition:background-color .18s ease, transform .18s ease, box-shadow .18s ease, border-color .18s ease!important;
}
.st-key-mobile_navigation [data-testid="stButton"]>button[kind="primary"]{
  background:#f0f2e9!important;
  background-color:#f0f2e9!important;
  color:#29463a!important;
  -webkit-text-fill-color:#29463a!important;
  border-color:#f0f2e9!important;
}
@media (hover:hover) and (pointer:fine){
  .st-key-mobile_navigation [data-testid="stButton"]>button:hover{
    background:rgba(255,255,255,.30)!important;
    background-color:rgba(255,255,255,.30)!important;
    border-color:rgba(255,255,255,.55)!important;
    transform:translateY(-2px)!important;
    box-shadow:0 5px 12px rgba(9,28,18,.16)!important;
  }
  .st-key-mobile_navigation [data-testid="stButton"]>button[kind="primary"]:hover{
    background:#ffffff!important;
    background-color:#ffffff!important;
    color:#243d31!important;
    -webkit-text-fill-color:#243d31!important;
  }
  .st-key-top_navigation [data-testid="stButton"]>button{
    transition:background-color .18s ease, transform .18s ease, box-shadow .18s ease!important;
  }
  .st-key-top_navigation [data-testid="stButton"]>button:hover{
    transform:translateY(-2px)!important;
    box-shadow:0 5px 12px rgba(9,28,18,.13)!important;
  }
}


/* Estado selecionado no menu: fundo claro, texto escuro e nítido. */
.st-key-mobile_navigation [data-testid="stButton"] > button[kind="primary"],
.st-key-mobile_navigation [data-testid="stBaseButton-primary"],
.st-key-mobile_navigation button[kind="primary"] {
  background: #eef1e8 !important;
  background-color: #eef1e8 !important;
  color: #203b2e !important;
  -webkit-text-fill-color: #203b2e !important;
  border: 1px solid #eef1e8 !important;
  opacity: 1 !important;
}
.st-key-mobile_navigation [data-testid="stButton"] > button[kind="primary"] *,
.st-key-mobile_navigation [data-testid="stBaseButton-primary"] *,
.st-key-mobile_navigation button[kind="primary"] * {
  color: #203b2e !important;
  -webkit-text-fill-color: #203b2e !important;
  opacity: 1 !important;
}
/* Itens não selecionados um pouco mais claros para leitura sobre o painel verde. */
.st-key-mobile_navigation [data-testid="stButton"] > button:not([kind="primary"]) {
  background: rgba(255,255,255,.22) !important;
  background-color: rgba(255,255,255,.22) !important;
  color: #ffffff !important;
  -webkit-text-fill-color: #ffffff !important;
  border-color: rgba(255,255,255,.38) !important;
}
.st-key-mobile_navigation [data-testid="stButton"] > button:not([kind="primary"]) * {
  color: #ffffff !important;
  -webkit-text-fill-color: #ffffff !important;
}
/* Microinterações discretas em cartões e imagens. */
@media (hover: hover) and (pointer: fine) {
  .card,
  .photo-card,
  .rule-card,
  .review-card,
  .stat-card,
  .access-panel,
  .fact-card,
  .complaint,
  .knowledge-hero,
  .about-values {
    transition: transform .2s ease, box-shadow .2s ease, border-color .2s ease !important;
  }
  .card:hover,
  .photo-card:hover,
  .rule-card:hover,
  .review-card:hover,
  .stat-card:hover,
  .access-panel:hover,
  .fact-card:hover,
  .complaint:hover,
  .knowledge-hero:hover,
  .about-values:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 9px 22px rgba(37,55,47,.10) !important;
    border-color: #cbd7c9 !important;
  }
  .photo-frame img,
  .home-experience-photo {
    transition: transform .28s ease !important;
  }
  .photo-card:hover .photo-frame img,
  .home-experience:hover .home-experience-photo {
    transform: scale(1.025) !important;
  }
}


/* Campo de data nativo do Streamlit: calendário padrão no próprio formulário. */
[data-testid="stDateInput"] input {
  background:#fffefa!important;
  color:#25372f!important;
  -webkit-text-fill-color:#25372f!important;
  border:1px solid #c9d1c5!important;
  border-radius:10px!important;
}
[data-testid="stDateInput"] svg {
  color:#526258!important;
  fill:#526258!important;
}
[data-baseweb="calendar"] {
  background:#fffefa!important;
  color:#25372f!important;
}
[data-baseweb="calendar"] button {
  color:#29463a!important;
}
[data-baseweb="calendar"] button[disabled] {
  color:#aeb5ac!important;
}

/* Rastreio visual do encadeamento para frente. */
.trace-start,.trace-finish{background:#eef2eb;border:1px solid #dce5da;border-radius:14px;padding:1rem 1.1rem;margin:.55rem 0;}
.trace-finish{background:#e7eee6;border-color:#cbd9cb;}
.trace-kicker{display:block;color:#627568;font-size:.65rem;font-weight:800;letter-spacing:1.1px;margin-bottom:.45rem;}
.trace-facts{color:#304638;line-height:1.8;font-size:.86rem;}
.trace-step{position:relative;background:#fffefa;border:1px solid #dfe5da;border-left:4px solid #829b83;border-radius:12px;padding:.85rem 1rem;margin:.65rem 0 .65rem 1rem;box-shadow:0 3px 10px rgba(37,55,47,.035);}
.trace-step-heading{display:flex;align-items:center;gap:.5rem;flex-wrap:wrap;color:#29463a;margin-bottom:.55rem;}
.trace-number{font-size:.64rem;font-weight:800;letter-spacing:.7px;color:#718174;background:#eef2eb;border-radius:6px;padding:.25rem .4rem;}
.trace-condition,.trace-derived{color:#4e5f53;font-size:.82rem;line-height:1.65;margin:.35rem 0;}
.trace-condition code{white-space:normal;overflow-wrap:anywhere;color:#29463a;background:#f1f3ed;padding:.12rem .28rem;border-radius:4px;}
.trace-meta{display:block;color:#7b887d;font-size:.68rem;font-weight:700;letter-spacing:.35px;margin-top:.45rem;}
.trace-finish p{color:#536358;font-size:.82rem;line-height:1.6;margin:.3rem 0 .5rem;}
.trace-finish strong{color:#29463a;}
@media(max-width:700px){
 .trace-step{margin-left:.25rem;padding:.75rem .8rem;}
 .trace-step-heading{gap:.4rem;}
 .trace-condition,.trace-derived{font-size:.78rem;}
}


/* Aviso de alergia: contraste próprio para não herdar texto branco do tema global. */
.allergy-warning {
    display: flex;
    flex-direction: column;
    gap: .25rem;
    width: 100%;
    box-sizing: border-box;
    padding: .85rem 1rem;
    margin: .55rem 0 1rem;
    border: 1px solid #e6d28b;
    border-left: 4px solid #bd8b24;
    border-radius: 12px;
    background: #fff8df;
    color: #4c3a12 !important;
    -webkit-text-fill-color: #4c3a12 !important;
    font-size: .9rem;
    line-height: 1.55;
}
.allergy-warning strong,
.allergy-warning span {
    color: #4c3a12 !important;
    -webkit-text-fill-color: #4c3a12 !important;
    opacity: 1 !important;
}
.allergy-warning strong {
    font-size: .92rem;
    font-weight: 750;
}
@media(max-width:700px) {
    .allergy-warning {
        padding: .8rem .85rem;
        font-size: .84rem;
    }
}

</style>
""",
    unsafe_allow_html=True,
)

STAFF = [
    {
        "name":"Helena Martins", "role":"Biomedicina estética", "focus":"Acne e oleosidade",
        "responsibility":"Organiza o encaminhamento inicial de pessoas que relatam acne e oleosidade, reunindo as informações importantes para a avaliação presencial.",
        "bio":"Seu atendimento começa pela escuta da queixa e pelo registro de informações sobre a rotina de cuidados, a duração do incômodo e as características relatadas pelo cliente. Ajuda a preparar uma conversa mais objetiva para a avaliação profissional.",
        "photo":"helena.jpg"
    },
    {
        "name":"Mariana Costa", "role":"Fisioterapia dermatofuncional", "focus":"Firmeza e flacidez",
        "responsibility":"Recebe os encaminhamentos iniciais relacionados a firmeza e flacidez da pele, organizando as informações para avaliação individual.",
        "bio":"Na etapa inicial, procura compreender a principal preocupação do cliente, há quanto tempo ela é percebida e quais aspectos precisam ser aprofundados presencialmente. Seu foco é contribuir para que a avaliação ocorra de forma organizada e individualizada.",
        "photo":"mariana.jpg"
    },
    {
        "name":"Caio Nogueira", "role":"Dermatologia", "focus":"Manchas, melasma e sensibilidade",
        "responsibility":"É a referência de encaminhamento inicial para relatos de manchas, melasma, sensibilidade e vermelhidão, que precisam de avaliação profissional cuidadosa.",
        "bio":"Sua atuação no fluxo da DermaTech é acolher relatos relacionados a alterações de tonalidade e sensibilidade da pele. As informações da triagem servem como ponto de partida; a análise e a definição de conduta são realizadas durante a consulta.",
        "photo":"caio.jpg"
    },
    {
        "name":"Beatriz Almeida", "role":"Estética e cosmetologia", "focus":"Ressecamento e prevenção",
        "responsibility":"Organiza o primeiro atendimento de clientes que relatam ressecamento ou procuram orientação preventiva sobre cuidados com a pele.",
        "bio":"Dedica atenção à descrição dos hábitos de cuidado, à sensação de ressecamento e às expectativas do cliente. Seu papel é ajudar a estruturar essas informações para que a avaliação presencial considere a rotina e as necessidades individuais.",
        "photo":"beatriz.jpg"
    },
    {
        "name":"Luiza Fernandes", "role":"Biomedicina estética", "focus":"Linhas, rugas e olheiras",
        "responsibility":"É a referência inicial para queixas envolvendo linhas, rugas e olheiras, direcionando o cliente para uma avaliação compatível com o relato apresentado.",
        "bio":"No primeiro contato, busca identificar qual aspecto mais incomoda o cliente e registrar há quanto tempo a queixa está presente. A triagem organiza o atendimento, sem antecipar diagnóstico ou indicar procedimentos.",
        "photo":"luiza.jpg"
    },
    {
        "name":"Rafael Mendes", "role":"Fisioterapia dermatofuncional", "focus":"Cicatrizes e textura",
        "responsibility":"Recebe os encaminhamentos iniciais relacionados a cicatrizes de acne e irregularidades de textura, apoiando a organização da avaliação presencial.",
        "bio":"Seu eixo de atendimento considera o histórico relatado, a região de interesse e a principal expectativa do cliente. As respostas ajudam a preparar a avaliação, na qual o profissional poderá compreender melhor cada situação.",
        "photo":"rafael.jpg"
    },
]

COMPLAINTS = [
    "Acne e oleosidade", "Manchas e melasma", "Linhas e rugas",
    "Firmeza e flacidez da pele", "Ressecamento da pele", "Sensibilidade e vermelhidão",
    "Poros dilatados e textura irregular", "Olheiras", "Cicatrizes de acne",
    "Cuidados preventivos", "Outras queixas",
]

# Base de conhecimento: regras de triagem e encaminhamento, não de diagnóstico ou prescrição.
REVIEWS = [
    ("Juliana R.", "Gostei muito da forma como fui recebida desde o primeiro contato. A triagem foi simples de responder, mas me deu espaço para explicar o que estava me incomodando e há quanto tempo percebia isso. Depois, consegui entender quais informações seriam levadas para a avaliação presencial e quais seriam os próximos passos."),
    ("Marcos A.", "O que mais gostei foi a organização do atendimento. As perguntas ajudaram a reunir informações que eu provavelmente esqueceria de comentar na hora, como a duração da queixa e os cuidados que já tinha tentado. A equipe explicou com clareza que o resultado era apenas um encaminhamento inicial e que a avaliação profissional aconteceria presencialmente."),
    ("Fernanda L.", "Desde a chegada, achei o ambiente tranquilo e acolhedor. Tive tempo para explicar minhas dúvidas sem sentir que precisava resumir tudo rapidamente. A conversa foi clara, recebi orientações sobre como seria a avaliação e saí sabendo exatamente qual seria a próxima etapa do atendimento."),
    ("Patrícia M.", "A triagem tornou o primeiro contato mais objetivo. Gostei de conseguir revisar as respostas e entender por que determinadas informações eram importantes para organizar o encaminhamento. Também achei positivo saber quais dados seriam aprofundados durante a conversa com o profissional."),
    ("Rafael C.", "Consegui consultar as opções de horário e enviar minha solicitação sem dificuldade. As informações sobre o profissional de referência e sobre a avaliação presencial estavam bem explicadas. Isso me deixou mais preparado para o primeiro encontro e evitou dúvidas sobre o que aconteceria depois da triagem."),
    ("Aline P.", "Eu não sabia muito bem como explicar minha queixa quando entrei em contato com a clínica. As perguntas me ajudaram a organizar o que eu estava sentindo e a lembrar de detalhes importantes sobre o tempo e a frequência do incômodo. Gostei de receber um encaminhamento explicado, sem promessas de tratamento antes de conversar com o profissional."),
    ("Camila T.", "Achei a experiência bem cuidadosa. O formulário foi fácil de preencher, os textos eram claros e consegui entender a diferença entre a triagem inicial e uma avaliação profissional. A equipe também explicou como as informações seriam usadas para preparar o atendimento, o que tornou o processo mais transparente."),
    ("Eduardo S.", "O atendimento foi organizado do início ao fim. Consegui informar minha principal preocupação, entender qual área seria uma referência inicial e solicitar um horário com tranquilidade. Gostei especialmente de a clínica deixar claro que cada caso precisa ser avaliado presencialmente, respeitando as particularidades de cada pessoa."),
]

for key, default in [("bookings", []),("result", None),("result_input", None),("booking_feedback", None),("review_index", 0),("page", "Início"),("reception_view", "solicitacoes"),("mobile_menu_open", False)]:
    if key not in st.session_state:
        st.session_state[key] = default

# Navegação desktop e mobile separadas para evitar corte do botão sanduíche.
if st.session_state.page == "Conheça mais sobre nós":
    st.session_state.page = "Sobre nós"
nav_items = ["Início", "Nova triagem", "Recepção", "Sobre nós"]

# Cabeçalho desktop: marca e quatro opções na mesma linha.
with st.container(key="top_navigation"):
    nav_cols = st.columns([2.5, 1.0, 1.35, 1.0, 1.0], vertical_alignment="center")
    with nav_cols[0]:
        st.markdown('<div class="brand">✳ DermaTech<small>CLÍNICA DE ESTÉTICA</small></div>', unsafe_allow_html=True)
    for col, nav_item in zip(nav_cols[1:], nav_items):
        with col:
            if st.button(nav_item, key=f"top_nav_{nav_item}", use_container_width=True,
                         type="primary" if nav_item == st.session_state.page else "secondary"):
                st.session_state.page = nav_item
                st.session_state.mobile_menu_open = False
                st.rerun()

# Cabeçalho mobile: marca e botão hambúrguer em colunas próprias.
with st.container(key="mobile_navigation_header"):
    mobile_head_cols = st.columns([6, 1], vertical_alignment="center")
    with mobile_head_cols[0]:
        st.markdown('<div class="brand">✳ DermaTech<small>CLÍNICA DE ESTÉTICA</small></div>', unsafe_allow_html=True)
    with mobile_head_cols[1]:
        if st.button("☰", key="mobile_menu_toggle", help="Abrir menu", use_container_width=True,
                     type="secondary"):
            st.session_state.mobile_menu_open = not st.session_state.mobile_menu_open
            st.rerun()

# Painel de navegação expansível para telas pequenas.
if st.session_state.mobile_menu_open:
    with st.container(key="mobile_navigation"):
        mobile_nav_cols = st.columns(2)
        for col, nav_item in zip(mobile_nav_cols * 2, nav_items):
            with col:
                if st.button(nav_item, key=f"mobile_nav_{nav_item}", use_container_width=True,
                             type="primary" if nav_item == st.session_state.page else "secondary"):
                    st.session_state.page = nav_item
                    st.session_state.mobile_menu_open = False
                    st.rerun()

page = st.session_state.page


def render_reviews():
    """Carrossel de avaliações demonstrativas, com controles compactos e centralizados."""
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
        with st.container(key="review_controls"):
            prev_col, count_col, next_col = st.columns([1, 4, 1], vertical_alignment="center")
            with prev_col:
                if st.button("←", key="review_prev", help="Avaliação anterior", type="primary", use_container_width=True):
                    st.session_state.review_index = (idx - 1) % len(REVIEWS)
                    st.rerun()
            with count_col:
                st.markdown(
                    f'<div class="review-count">AVALIAÇÃO {idx + 1} DE {len(REVIEWS)}</div>',
                    unsafe_allow_html=True,
                )
            with next_col:
                if st.button("→", key="review_next", help="Próxima avaliação", type="primary", use_container_width=True):
                    st.session_state.review_index = (idx + 1) % len(REVIEWS)
                    st.rerun()


def render_home():
    st.markdown('<div class="hero"><div class="eyebrow">Cuidado que começa com escuta</div><h1>Tecnologia e cuidado para a saúde da sua pele.</h1><p>Uma clínica de estética que une avaliação especializada, tecnologia e atendimento personalizado para orientar seu próximo passo.</p></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    benefits = [
        ("✳","Triagem inteligente","Informações organizadas por um sistema especialista."),
        ("♡","Encaminhamento personalizado","Direcionamento inicial conforme a queixa informada."),
        ("✓","Avaliação profissional","A decisão sobre cuidados acontece presencialmente."),
    ]
    for col, (icon, title, desc) in zip((c1,c2,c3), benefits):
        with col:
            st.markdown(f'<div class="card"><span class="tag">{icon}</span><h3>{title}</h3><p class="muted">{desc}</p></div>', unsafe_allow_html=True)

    st.markdown("## Principais queixas que atendemos")
    st.write("Selecione a condição que mais se aproxima da sua queixa ao iniciar a triagem.")
    for row in (COMPLAINTS[:4], COMPLAINTS[4:8], COMPLAINTS[8:]):
        cols = st.columns(len(row))
        for col, item in zip(cols, row):
            with col:
                st.markdown(f'<div class="card" style="text-align:center;min-height:82px;display:flex;align-items:center;justify-content:center"><b>{item}</b></div>', unsafe_allow_html=True)

    st.markdown("## Experiência de atendimento")
    st.markdown(
        '<p class="about-lead">Um primeiro contato simples e organizado: você compartilha sua queixa, entende como as informações serão analisadas e recebe um encaminhamento inicial para continuar o atendimento com a equipe.</p>',
        unsafe_allow_html=True,
    )
    experience_cols = st.columns(3)
    experience_items = [
        ("01", "Conte o que você procura", "Responda às perguntas da triagem no seu ritmo e informe o que considera importante."),
        ("02", "Entenda o encaminhamento", "Veja a área de referência e os fatos e regras que contribuíram para o resultado."),
        ("03", "Converse com a equipe", "Solicite uma avaliação para aprofundar suas necessidades presencialmente."),
    ]
    for col, (number, title, desc) in zip(experience_cols, experience_items):
        with col:
            st.markdown(
                f'<div class="about-values"><span class="tag">ETAPA {number}</span><h3>{title}</h3><p class="muted">{desc}</p></div>',
                unsafe_allow_html=True,
            )

    st.markdown("## O que nossos clientes dizem")
    st.caption("Avaliações demonstrativas criadas para apresentar a experiência de atendimento da DermaTech.")
    render_reviews()



APPOINTMENT_SLOTS = [
    "09:00", "09:45", "10:30", "11:15",
    "13:00", "13:45", "14:30", "15:15",
    "16:00", "16:45", "17:30", "18:15", "19:00",
]

# Dias fixos de fechamento do cenário demonstrativo: domingos, 1º de janeiro e 25 de dezembro.
FIXED_CLOSURES = {(1, 1), (12, 25)}
def available_slots_for(day, professional):
    """Retorna horários livres para o profissional na data escolhida."""
    occupied = {
        item.get("horario")
        for item in st.session_state.bookings
        if item.get("data") == day.isoformat()
        and item.get("profissional") == professional
    }
    return [slot for slot in APPOINTMENT_SLOTS if slot not in occupied]


def is_unavailable_day(day, professional):
    """Bloqueia passado, domingos, datas de recesso e datas sem horários livres."""
    if day <= date.today():
        return True
    if day.weekday() == 6:
        return True
    if (day.month, day.day) in FIXED_CLOSURES:
        return True
    return not available_slots_for(day, professional)


def first_available_day(professional, start=None, horizon=180):
    start = start or (date.today() + timedelta(days=1))
    for offset in range(horizon):
        candidate = start + timedelta(days=offset)
        if not is_unavailable_day(candidate, professional):
            return candidate
    return None


def render_triage_result(res, facts_input):
    fatos = res["fatos"]
    st.markdown("---")
    if (
        not res.get("conclusao")
        or not fatos.get("area")
        or not fatos.get("profissional")
    ):
        st.markdown(
            '<div class="status-banner error">Não foi possível concluir com as informações fornecidas.</div>',
            unsafe_allow_html=True,
        )
        st.info(
            "O sistema não encontrou regras suficientes para definir um encaminhamento inicial. "
            "Revise as respostas ou procure a equipe da clínica para orientação."
        )
        st.markdown("**Informações recebidas**")
        for label, key in [
            ("Queixa", "queixa"),
            ("Gravidade", "gravidade"),
            ("Duração", "duracao"),
            ("Sensibilidade", "sensibilidade"),
            ("Alergias", "alergia"),
            ("Descrição da alergia", "alergia_detalhe"),
            ("Avaliação anterior", "avaliacao_anterior"),
        ]:
            if facts_input.get(key):
                st.write(f"**{label}:** {facts_input[key]}")
        return
    st.markdown('<div class="status-banner success">Triagem concluída: encaminhamento inicial identificado.</div>', unsafe_allow_html=True)
    st.markdown(f"### {res['conclusao'] or 'Avaliação geral'}")
    st.write(f"**Área sugerida:** {fatos.get('area','Avaliação geral')}")
    st.write(f"**Profissional de referência:** {fatos.get('profissional','Equipe DermaTech')}")
    st.write(f"**Tipo de avaliação:** {fatos.get('tipo_avaliacao','Avaliação geral')}")
    st.caption("O encaminhamento organiza o atendimento. A avaliação e qualquer decisão sobre cuidados são realizadas presencialmente por profissional habilitado.")

    st.markdown("### Como chegamos a este resultado?")
    st.markdown("**Fatos informados**")
    fact_items = [
        ("Queixa","queixa"),("Gravidade","gravidade"),("Duração","duracao"),
        ("Sensibilidade","sensibilidade"),("Alergias","alergia"),("Avaliação anterior","avaliacao_anterior")
    ]
    if facts_input.get("alergia") == "Sim" and facts_input.get("alergia_detalhe"):
        fact_items.append(("Alergia informada","alergia_detalhe"))
    for start in range(0, len(fact_items), 3):
        facts_cols = st.columns(3)
        for col, (label, key) in zip(facts_cols, fact_items[start:start+3]):
            with col:
                st.markdown(f'<div class="fact-card"><small>{label}</small><strong>{escape(str(facts_input.get(key,"—")))}</strong></div>', unsafe_allow_html=True)


    st.markdown("### Rastreio do motor de inferência")
    st.caption(
        "A sequência abaixo mostra como o Forward Chaining avaliou as regras, "
        "quais condições foram satisfeitas e quais fatos foram derivados."
    )
    with st.expander("Acompanhar o raciocínio passo a passo", expanded=True):
        initial_fact_lines = "<br>".join(
            f"<b>{escape(str(key))}:</b> {escape(str(value))}"
            for key, value in facts_input.items()
            if value not in ("", None)
        )
        st.markdown(
            f'<div class="trace-start"><span class="trace-kicker">PONTO DE PARTIDA · FATOS INFORMADOS</span>'
            f'<div class="trace-facts">{initial_fact_lines}</div></div>',
            unsafe_allow_html=True,
        )
        for rule in res["regras"]:
            derived = rule.get("fatos_derivados") or {}
            if derived:
                derived_lines = "<br>".join(
                    f"<b>{escape(str(key))}:</b> {escape(str(value))}"
                    for key, value in derived.items()
                )
            else:
                derived_lines = "A conclusão desta regra confirmou fatos já presentes na base."
            st.markdown(
                f'<div class="trace-step">'
                f'<div class="trace-step-heading">'
                f'<span class="trace-number">ETAPA {rule.get("etapa", 0):02d}</span>'
                f'<span class="rule-id">{escape(str(rule["id"]))}</span>'
                f'<b>{escape(str(rule["descricao"]))}</b>'
                f'</div>'
                f'<div class="trace-condition"><b>Condição avaliada:</b> '
                f'<code>{escape(str(rule["condicao"]))}</code></div>'
                f'<div class="trace-derived"><b>Fato(s) derivado(s):</b><br>{derived_lines}</div>'
                f'<div class="trace-meta">Ciclo {rule.get("ciclo", 1)} · Fator heurístico {rule["cf"]:.0%}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        st.markdown(
            f'<div class="trace-finish"><span class="trace-kicker">PONTO DE PARADA</span>'
            f'<b>Encadeamento concluído</b>'
            f'<p>O motor percorreu a base por {res.get("ciclos", 1)} ciclo(s) e encerrou quando '
            f'não encontrou uma nova regra aplicável.</p>'
            f'<strong>Conclusão: {escape(str(res.get("conclusao", "Não identificada")))}</strong></div>',
            unsafe_allow_html=True,
        )

    st.caption(f"Índice heurístico acumulado das regras acionadas: {res['certeza']*100:.1f}% — não representa probabilidade clínica.")

    st.markdown("### Solicitar agendamento de avaliação")
    matching = [p for p in STAFF if p["name"] == fatos.get("profissional")]
    default_staff = matching[0]["name"] if matching else STAFF[0]["name"]
    names = [p["name"] for p in STAFF] if default_staff == "Equipe DermaTech" else [default_staff] + [p["name"] for p in STAFF if p["name"] != default_staff]

    with st.container(key="booking_panel"):
        st.markdown("#### Dados para solicitar sua avaliação")
        st.markdown(
            '<p class="muted">Escolha a pessoa de referência, uma data no calendário e um horário disponível para solicitar sua avaliação.</p>',
            unsafe_allow_html=True,
        )

        chosen = st.selectbox(
            "Profissional de referência",
            names,
            key="booking_professional",
            index=names.index(default_staff) if default_staff in names else 0,
        )

        # Se a data anterior não estiver disponível para o profissional atual,
        # posiciona o seletor na próxima data livre.
        date_key = "booking_date_picker"
        minimum_date = date.today() + timedelta(days=1)
        default_date = first_available_day(chosen)
        if default_date is None:
            st.warning("Não há datas disponíveis para este profissional no período demonstrativo.")
            chosen_date = None
            slots = []
        else:
            current_date = st.session_state.get(date_key)
            if not isinstance(current_date, date) or is_unavailable_day(current_date, chosen):
                st.session_state[date_key] = default_date

            st.caption("Atendimento de segunda a sábado. Domingos, 1º de janeiro, 25 de dezembro e dias sem horários livres não aceitam agendamento.")
            chosen_date = st.date_input(
                "Data desejada",
                min_value=minimum_date,
                format="DD/MM/YYYY",
                key=date_key,
                help="Selecione uma data futura. Domingos, datas de recesso e dias sem horários livres não aceitam solicitações.",
            )

            if is_unavailable_day(chosen_date, chosen):
                slots = []
                st.warning(
                    "Não há atendimento disponível nesta data. Escolha outro dia no calendário."
                )
            else:
                slots = available_slots_for(chosen_date, chosen)

        if chosen_date and slots:
            st.caption("Horários disponíveis — atendimento de segunda a sábado, das 09h às 19h.")
            with st.form("booking_form"):
                chosen_time = st.selectbox("Horário disponível", slots)
                c1, c2 = st.columns(2)
                with c1:
                    full_name = st.text_input("Nome completo", placeholder="Digite seu nome")
                    email = st.text_input("E-mail", placeholder="voce@exemplo.com")
                with c2:
                    phone = st.text_input("Telefone / WhatsApp", placeholder="(21) 99999-9999")
                    st.text_input(
                        "Data selecionada",
                        value=chosen_date.strftime("%d/%m/%Y"),
                        disabled=True,
                    )
                book = st.form_submit_button("Solicitar agendamento", use_container_width=True)
        else:
            chosen_time = None
            full_name = email = phone = ""
            book = False
            if chosen_date and not is_unavailable_day(chosen_date, chosen):
                st.info("Todos os horários desta data já foram solicitados. Escolha outro dia.")

        if book:
            email_ok = bool(re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email.strip()))
            phone_digits = re.sub(r"\D", "", phone)
            slots_now = available_slots_for(chosen_date, chosen) if chosen_date else []
            if not chosen_date or is_unavailable_day(chosen_date, chosen) or chosen_time not in slots_now:
                st.session_state.booking_feedback = {
                    "type": "error",
                    "message": "Solicitação não agendada. A data ou o horário não está mais disponível. Escolha outra opção.",
                }
            elif not full_name.strip() or not email_ok or len(phone_digits) < 10:
                st.session_state.booking_feedback = {
                    "type": "error",
                    "message": "Solicitação não agendada. Confira o nome, o e-mail e o telefone e tente novamente.",
                }
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
                st.session_state.booking_feedback = {
                    "type": "success",
                    "message": "Solicitação agendada com sucesso.",
                }
        feedback = st.session_state.get("booking_feedback")
        if feedback:
            css_class = "success" if feedback["type"] == "success" else "error"
            st.markdown(
                f'<div class="status-banner {css_class}">{escape(feedback["message"])}</div>',
                unsafe_allow_html=True,
            )



def render_triage():
    st.markdown(
        '<div class="eyebrow">Atendimento inicial</div>'
        '<h1>Vamos conhecer melhor sua necessidade.</h1>'
        '<p class="muted">Suas respostas serão analisadas para organizar um encaminhamento inicial. '
        'Não é diagnóstico nem indicação de procedimento.</p>',
        unsafe_allow_html=True,
    )

    # Os campos são mantidos fora de st.form para que a seleção "Sim" atualize
    # a tela imediatamente e revele o campo de descrição da alergia.
    with st.container(key="triage_questions"):
        c1, c2 = st.columns(2)
        with c1:
            queixa = st.selectbox("Qual é sua principal queixa?", COMPLAINTS, key="triage_queixa")
            gravidade = st.selectbox(
                "Como você descreveria o incômodo?",
                ["Leve", "Moderada", "Intensa"],
                key="triage_gravidade",
            )
            duracao = st.selectbox(
                "Há quanto tempo percebe essa queixa?",
                ["Até 3 meses", "De 3 a 6 meses", "Mais de 6 meses", "Não sei informar"],
                key="triage_duracao",
            )
        with c2:
            sensibilidade = st.selectbox(
                "Sua pele costuma apresentar sensibilidade?",
                ["Não", "Sim", "Não sei informar"],
                key="triage_sensibilidade",
            )
            alergia = st.selectbox(
                "Possui alergias conhecidas que queira informar?",
                ["Não", "Sim", "Não sei informar"],
                key="triage_alergia",
            )
            alergia_detalhe = ""
            if alergia == "Sim":
                alergia_detalhe = st.text_input(
                    "Qual alergia devemos registrar?",
                    placeholder="Ex.: fragrância, cosmético ou outra substância",
                    key="triage_alergia_detalhe",
                    help="Informe a alergia para que ela seja registrada nos fatos da triagem.",
                )
            else:
                # Evita reaproveitar uma descrição antiga se a pessoa trocar "Sim" por "Não".
                if st.session_state.get("triage_alergia_detalhe"):
                    st.session_state["triage_alergia_detalhe"] = ""
            avaliacao_anterior = st.selectbox(
                "Já realizou avaliação profissional para essa queixa?",
                ["Não", "Sim"],
                key="triage_avaliacao_anterior",
            )

        submitted = st.button(
            "Analisar respostas",
            key="triage_analisar",
            use_container_width=True,
            type="primary",
        )

    if submitted:
        if alergia == "Sim" and not alergia_detalhe.strip():
            st.session_state.result = None
            st.markdown(
                '<div class="allergy-warning" role="alert">'
                '<strong>Informe sua alergia</strong>'
                '<span>Você informou que possui alergia. Escreva qual alergia deseja informar antes de analisar a triagem.</span>'
                '</div>',
                unsafe_allow_html=True,
            )
        else:
            facts_input = {
                "queixa": queixa,
                "gravidade": gravidade,
                "duracao": duracao,
                "sensibilidade": sensibilidade,
                "alergia": alergia,
                "alergia_detalhe": alergia_detalhe.strip() if alergia == "Sim" else "",
                "avaliacao_anterior": avaliacao_anterior,
            }
            st.session_state.result = executar_inferencia(facts_input)
            st.session_state.result_input = facts_input
            st.session_state.booking_feedback = None

    if st.session_state.result:
        render_triage_result(st.session_state.result, st.session_state.get("result_input", {}))


def render_reception():
    if st.session_state.reception_view == "knowledge":
        render_knowledge()
        return
    st.markdown('<div class="eyebrow">Área interna demonstrativa</div><h1>Recepção DermaTech</h1><p class="muted">Acompanhe as solicitações de avaliação realizadas nesta sessão.</p>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    stats = [
        ("SOLICITAÇÕES NESTA SESSÃO", len(st.session_state.bookings), "Registros demonstrativos"),
        ("AGENDAMENTOS", len(st.session_state.bookings), "Horários solicitados"),
        ("REGRAS CADASTRADAS", len(RULES), "Base de conhecimento"),
    ]
    for col, (label, value, foot) in zip((c1,c2,c3), stats):
        with col:
            st.markdown(f'<div class="stat-card"><small>{label}</small><strong>{value}</strong><span>{foot}</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="access-panel"><div class="eyebrow">Demonstração acadêmica</div><h3>Base de conhecimento e motor de inferência</h3><p class="muted">Consulte fatos, regras de produção e os mecanismos utilizados para construir um encaminhamento explicável.</p></div>', unsafe_allow_html=True)
    if st.button("Ver base de conhecimento  ↗", key="open_knowledge"):
        st.session_state.reception_view = "knowledge"
        st.rerun()
    st.markdown("### Solicitações recentes")
    if st.session_state.bookings:
        for booking in reversed(st.session_state.bookings):
            st.markdown(
                f'''<div class="card"><div class="rule-meta">{booking['data']} · {booking['horario']}</div>
                <h3>{booking['nome']}</h3><p class="muted">{booking['email']} · {booking['telefone']}</p>
                <b>{booking['profissional']}</b><p class="muted">{booking['area']}</p></div>''',
                unsafe_allow_html=True,
            )
    else:
        st.markdown('<div class="card"><h3>Nenhuma solicitação por aqui ainda.</h3><p class="muted">Quando uma avaliação for solicitada nesta sessão, ela aparecerá nesta lista.</p></div>', unsafe_allow_html=True)


def render_knowledge():
    st.markdown('<div class="eyebrow">Demonstração acadêmica</div><h1>Base de conhecimento.</h1><p class="muted">Consulte os fatos, as regras e o funcionamento do motor de inferência que apoia a triagem inicial da DermaTech.</p>', unsafe_allow_html=True)
    st.markdown('<div class="knowledge-hero"><h2>Conhecimento organizado para orientar o atendimento.</h2><p>O protótipo utiliza encadeamento para frente: parte das respostas do cliente, deriva novos fatos quando as condições das regras são atendidas e constrói uma conclusão explicável. As regras são acadêmicas e não substituem avaliação profissional.</p></div>', unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    metrics = [(str(len(RULES)),"REGRAS DE PRODUÇÃO"),("01","MOTOR DE INFERÊNCIA"),("↗","FORWARD CHAINING")]
    for col,(value,label) in zip((c1,c2,c3),metrics):
        with col:
            st.markdown(f'<div class="stat-card"><strong>{value}</strong><small>{label}</small></div>',unsafe_allow_html=True)
    st.markdown("## Como o conhecimento é representado")
    d1,d2=st.columns(2)
    with d1:
        st.markdown('<div class="card"><span class="tag">FATOS</span><h3>Informações coletadas</h3><p class="muted">Queixa principal, gravidade, duração, sensibilidade, alergias e histórico de avaliação anterior. Novos fatos são derivados durante a inferência.</p></div>',unsafe_allow_html=True)
    with d2:
        st.markdown('<div class="card"><span class="tag">REGRAS</span><h3>Condições e conclusões</h3><p class="muted">Cada regra verifica condições sobre os fatos existentes e, quando satisfeita, acrescenta conclusões à base de fatos.</p></div>',unsafe_allow_html=True)

    groups = [
        ("QUEIXA E ENCAMINHAMENTO", RULES[:11]),
        ("CONTEXTO E PERFIL", RULES[11:20]),
        ("TIPO DE AVALIAÇÃO", RULES[20:25]),
        ("CONCLUSÃO E COMBINAÇÃO DE FATOS", RULES[25:]),
    ]
    st.markdown("## Regras de produção")
    st.caption("Cada cartão apresenta o identificador, a condição avaliada, a conclusão adicionada e o fator heurístico definido para a regra.")
    for group_name, group_rules in groups:
        st.markdown(f"### {group_name}")
        for start in range(0,len(group_rules),2):
            cols=st.columns(2)
            for col, rule in zip(cols,group_rules[start:start+2]):
                rid,description,condition,conclusion,cf=rule
                with col:
                    st.markdown(
                        f'''<div class="rule-card"><div><span class="rule-id">{rid}</span><b>{description}</b></div>
                        <p class="muted" style="margin:.7rem 0 .35rem"><b>Condição:</b> <code>{condition}</code></p>
                        <p class="muted" style="margin:.25rem 0 .55rem"><b>Conclusão:</b> {json.dumps(conclusion,ensure_ascii=False)}</p>
                        <span class="rule-meta">Fator heurístico: {cf:.0%}</span></div>''',
                        unsafe_allow_html=True,
                    )
    st.markdown("## Motor de inferência")
    st.markdown('<div class="card"><h3>Encadeamento para frente (Forward Chaining)</h3><p class="muted">O motor percorre a base de regras, verifica as condições, aplica as regras satisfeitas, adiciona fatos derivados e repete o processo até não haver novas conclusões. O histórico das regras acionadas é apresentado ao cliente após a triagem.</p></div>',unsafe_allow_html=True)
    st.markdown("## Testes de referência")
    tests=[
        ("Acne e oleosidade","Helena Martins"),
        ("Manchas e melasma","Caio Nogueira"),
        ("Outras queixas","Equipe DermaTech"),
    ]
    test_cols=st.columns(3)
    for col,(complaint,expected) in zip(test_cols,tests):
        result=executar_inferencia({"queixa":complaint,"gravidade":"Moderada","duracao":"Não sei informar","sensibilidade":"Não","alergia":"Não","avaliacao_anterior":"Não"})
        actual=result["fatos"].get("profissional","Não identificado")
        ok=actual==expected
        with col:
            st.markdown(f'<div class="card"><span class="tag">{"APROVADO" if ok else "REVISAR"}</span><h3>{complaint}</h3><p class="muted">Esperado: {expected}<br>Obtido: {actual}</p></div>',unsafe_allow_html=True)

    st.markdown("## Testes automatizados")
    st.markdown(
        '<div class="card"><span class="tag">PYTEST</span><h3>Validação do motor de inferência</h3>'
        '<p class="muted">O projeto inclui uma suíte com 12 testes automatizados para verificar os encaminhamentos, '
        'as regras combinadas R29–R32, o rastreio do Forward Chaining, entradas incompletas e ausência de conclusão.</p>'
        '<p><b>Como executar:</b> <code>python -m pytest</code></p></div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="knowledge-back-action"></div>', unsafe_allow_html=True)
    back_col, _ = st.columns([1, 5])
    with back_col:
        if st.button("← Voltar à recepção", key="back_reception", use_container_width=True):
            st.session_state.reception_view = "solicitacoes"
            st.rerun()


def render_about():
    # A página institucional usa títulos, textos e imagens em blocos separados
    # para manter hierarquia visual e leitura confortável em telas largas e móveis.
    st.markdown(
        '<div class="about-hero">'
        '<div class="eyebrow">SOBRE NÓS · DERMATECH</div>'
        '<h1 class="about-hero-title">Uma clínica feita para acolher.</h1>'
        '<p class="about-section-intro">A DermaTech nasceu da ideia de tornar o primeiro contato com uma clínica de estética mais simples, atencioso e organizado. Acreditamos que cada pessoa deve ter espaço para explicar suas dúvidas, falar sobre o que a trouxe até aqui e compreender com clareza quais são os próximos passos.</p>'
        '<p class="about-section-intro">Por isso, reunimos profissionais de diferentes áreas e uma experiência de atendimento que combina escuta, informação e tecnologia. Nosso objetivo é receber cada cliente com atenção e organizar as informações que serão aprofundadas durante a avaliação presencial.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown("## O jeito DermaTech de cuidar")
    st.markdown(
        '<p class="about-section-intro">Queremos que você saiba o que acontece em cada etapa do atendimento. Da primeira pergunta ao contato com a equipe, buscamos oferecer uma experiência clara, respeitosa e organizada.</p>',
        unsafe_allow_html=True,
    )
    values = [
        ("Escuta atenta", "Cada pessoa tem uma história e uma necessidade. Por isso, começamos ouvindo a queixa, as dúvidas e as expectativas apresentadas, sem tratar todos os casos como iguais."),
        ("Orientação clara", "Explicamos como funciona a triagem, quais informações são consideradas e por que determinado encaminhamento inicial foi apresentado."),
        ("Cuidado responsável", "A tecnologia ajuda a organizar o primeiro atendimento. A avaliação presencial, a análise profissional e qualquer decisão sobre cuidados continuam sob responsabilidade do profissional habilitado."),
    ]
    value_cols = st.columns(3, gap="medium")
    for col, (title, desc) in zip(value_cols, values):
        with col:
            st.markdown(
                f'<div class="about-values"><span class="tag">NOSSO COMPROMISSO</span><h3>{escape(title)}</h3><p class="muted">{escape(desc)}</p></div>',
                unsafe_allow_html=True,
            )

    st.markdown("## Nossa equipe")
    st.markdown(
        '<p class="staff-intro">Nossa equipe reúne profissionais com áreas de atuação diferentes e responsabilidades definidas no fluxo de atendimento. Essa organização ajuda a identificar uma área de referência a partir das informações fornecidas na triagem. O encaminhamento é inicial: durante a avaliação presencial, a equipe confirma qual profissional deverá acompanhar cada necessidade.</p>',
        unsafe_allow_html=True,
    )
    for start in range(0, len(STAFF), 3):
        cols = st.columns(3, gap="medium")
        for col, person in zip(cols, STAFF[start:start + 3]):
            with col:
                subtitle = f'<div class="staff-role">{escape(person["role"])}</div>'
                description = (
                    f'<p class="muted">{escape(person["bio"])}</p>'
                    f'<div class="responsibility-box"><b>Responsabilidade na clínica</b>'
                    f'<p class="muted">{escape(person["responsibility"])}</p></div>'
                )
                render_photo_card(person["photo"], person["name"], subtitle, description, person["focus"])

    st.markdown("## Um ambiente pensado para acolher")
    st.markdown(
        '<p class="about-section-intro">A experiência começa na chegada e continua na conversa inicial. Cada ambiente representa uma etapa importante do atendimento: receber com tranquilidade, orientar com clareza e oferecer um espaço reservado para que a pessoa possa compartilhar suas necessidades.</p>',
        unsafe_allow_html=True,
    )
    col1, col2 = st.columns(2, gap="large")
    with col1:
        render_photo_card(
            "recepcao_clinica.png", "Chegada e recepção", '<div class="staff-role">PRIMEIRO CONTATO</div>',
            '<p class="muted">Um espaço de boas-vindas com recepção organizada, assentos confortáveis e iluminação acolhedora. É o ponto de chegada, onde o cliente recebe as primeiras orientações e entende como seguirá o atendimento.</p>',
            "Acolhimento e orientação", wide=True,
        )
    with col2:
        render_photo_card(
            "espaco_conversa.png", "Espaço de conversa", '<div class="staff-role">ESCUTA E ORIENTAÇÃO</div>',
            '<p class="muted">Um ambiente reservado para uma conversa tranquila. Aqui, o cliente pode explicar suas dúvidas, compartilhar informações importantes e receber orientações sobre a avaliação presencial.</p>',
            "Conforto e privacidade", wide=True,
        )

    st.markdown("## Nossa proposta")
    st.markdown(
        '<p class="about-section-intro">A DermaTech utiliza um sistema especialista para apoiar a triagem inicial de uma clínica de estética. A aplicação coleta informações sobre a queixa apresentada, consulta uma base de conhecimento formada por fatos e regras e organiza um encaminhamento inicial para uma área ou profissional de referência.</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="about-section-intro">A proposta é facilitar a organização do primeiro contato e tornar o resultado compreensível. Em vez de apresentar apenas uma indicação, o sistema mostra quais informações foram consideradas e quais regras participaram do raciocínio.</p>',
        unsafe_allow_html=True,
    )
    steps = [
        ("01", "Compartilhar as informações", "O cliente responde perguntas sobre a queixa principal, a intensidade percebida, o tempo de ocorrência, a sensibilidade, as alergias e a existência de uma avaliação anterior."),
        ("02", "Organizar os fatos", "As respostas são registradas como fatos iniciais. Durante o processamento, novas informações podem ser derivadas quando as condições de uma regra são atendidas."),
        ("03", "Aplicar as regras de conhecimento", "O motor utiliza encadeamento para frente (Forward Chaining): percorre as regras, verifica suas condições, acrescenta as conclusões correspondentes à base de fatos e continua até não encontrar novas regras aplicáveis."),
        ("04", "Apresentar uma explicação", "O resultado informa o encaminhamento inicial e apresenta o histórico das regras acionadas. Assim, é possível entender quais fatos contribuíram para a conclusão."),
        ("05", "Continuar com a equipe", "Depois da triagem, o cliente pode solicitar uma avaliação. A equipe aprofunda as informações presencialmente e define os próximos passos de acordo com a análise profissional."),
    ]
    for number, title, desc in steps:
        st.markdown(
            f'<div class="proposal-step"><div class="number">{number}</div><div><b>{escape(title)}</b><p class="muted" style="margin:.3rem 0 0">{escape(desc)}</p></div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("### Tecnologia que orienta. Pessoas que cuidam.")
    st.markdown(
        '<div class="proposal-card">'
        '<p>Na DermaTech, a tecnologia tem uma função clara: apoiar a organização do atendimento inicial. A base de conhecimento reúne os fatos e as regras que representam o contexto da clínica. O motor de inferência analisa as respostas, identifica quais regras podem ser aplicadas e registra o caminho utilizado para chegar ao encaminhamento.</p>'
        '<p>Esse processo também precisa reconhecer seus próprios limites. Quando as respostas não permitem chegar a uma conclusão ou quando a queixa exige uma análise mais ampla, o sistema direciona a pessoa para uma avaliação geral, em vez de apresentar uma resposta sem fundamento.</p>'
        '<p>O sistema não realiza diagnóstico, não prescreve tratamentos e não substitui a avaliação presencial. Ele organiza informações e oferece uma explicação inicial para que o cliente e a equipe compreendam melhor como o atendimento pode continuar.</p>'
        '<p class="proposal-highlight">Nosso compromisso é unir informação organizada, transparência no encaminhamento e atenção individual em cada contato.</p>'
        '</div>',
        unsafe_allow_html=True,
    )


def render_site_footer():
    # Rodapé institucional consistente com a identidade visual da DermaTech.
    st.markdown(
        '''<div class="site-footer">
          <div class="site-footer-inner">
            <div>
              <div class="site-footer-brand">✳ DermaTech<small>CLÍNICA DE ESTÉTICA</small></div>
              <div class="site-footer-copy">Tecnologia a serviço do cuidado. Um primeiro atendimento organizado, com escuta, orientação e atenção às necessidades de cada pessoa.</div>
            </div>
            <div class="site-footer-copy"><b>Atendimento</b><br>Triagem inicial · Encaminhamento · Avaliação presencial</div>
          </div>
          <div class="site-footer-meta">© 2026 DermaTech. Todos os direitos reservados.</div>
        </div>''',
        unsafe_allow_html=True,
    )


if page == "Início":
    render_home()
elif page == "Nova triagem":
    render_triage()
elif page == "Recepção":
    render_reception()
elif page == "Sobre nós":
    render_about()


render_site_footer()
