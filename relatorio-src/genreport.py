# -*- coding: utf-8 -*-
import html
from pygments import highlight
from pygments.lexers import CLexer
from pygments.formatters import HtmlFormatter
from weasyprint import HTML

SRC = "/Users/bernardozamin/Documents/Ultimo semestre/ProgParalela/t2-ProgramacaoParalela"
OUT = "/tmp/relatorio"

def code_block(path, title):
    with open(path, encoding="utf-8") as f:
        src = f.read()
    fmt = HtmlFormatter(nowrap=False, style="friendly")
    body = highlight(src, CLexer(), fmt)
    return f'<h3 class="code-title">{html.escape(title)}</h3>{body}'

pyg_css = HtmlFormatter(style="friendly").get_style_defs('.highlight')

# ---------------- tabelas ----------------
strong = [
    (1,"10,861261","1,00","1,000"),(2,"5,596511","1,94","0,970"),
    (3,"4,179426","2,60","0,866"),(4,"3,255884","3,34","0,834"),
    (5,"2,545801","4,27","0,853"),(6,"2,072567","5,24","0,873"),
    (7,"1,863472","5,83","0,833"),(8,"1,657298","6,55","0,819"),
    (9,"1,483067","7,32","0,814"),(10,"1,384045","7,85","0,785"),
    (11,"1,312784","8,27","0,752"),(12,"1,194458","9,09","0,758"),
    (13,"1,067153","10,18","0,783"),(14,"1,033584","10,51","0,751"),
    (15,"1,011426","10,74","0,716"),(31,"0,537922","20,19","0,651"),
]
weak = [
    (1,"10,785180","1,00","1,000"),(2,"11,220187","1,93","0,963"),
    (3,"12,804295","2,51","0,837"),(4,"13,448854","3,18","0,796"),
    (5,"13,074383","4,09","0,818"),(6,"12,586510","5,09","0,849"),
    (7,"13,399998","5,59","0,798"),(8,"13,823886","6,18","0,773"),
    (9,"13,787825","6,97","0,775"),(10,"14,119740","7,57","0,757"),
    (11,"14,559463","8,08","0,734"),(12,"14,021968","9,15","0,762"),
    (13,"14,563222","9,53","0,733"),(14,"14,665052","10,19","0,728"),
    (15,"15,440807","10,37","0,691"),(31,"16,232599","20,39","0,658"),
]

def table(rows, cap):
    head = "<tr><th>Trab.</th><th>Tempo (s)</th><th>Speed-up</th><th>Efic.</th></tr>"
    body = "".join(
        f"<tr><td>{w}</td><td>{t}</td><td>{s}</td><td>{e}</td></tr>"
        for (w,t,s,e) in rows)
    return f'<table class="data"><caption>{cap}</caption>{head}{body}</table>'

analysis = """
<h2>1. Introdução</h2>
<p>O problema escolhido é o cálculo do <b>conjunto de Mandelbrot</b>,
reaproveitado do primeiro trabalho (OpenMP). Para cada pixel (x,y) de uma
imagem de 800&times;600, mapeia-se um ponto <i>c</i> do plano complexo e
itera-se <i>z = z² + c</i> até |z| &gt; 2 ou atingir MAX_ITER; o número de
iterações define a cor. O custo por pixel é <b>altamente irregular</b> —
pontos dentro do conjunto executam todas as MAX_ITER iterações, enquanto
pontos externos escapam cedo — o que torna o <b>balanceamento de carga</b> o
ponto central do problema.</p>

<h2>2. Modelo coordenador/trabalhador</h2>
<p>A versão paralela foi implementada em C + MPI no padrão SPMD seguindo o
modelo mestre/escravo. O <b>saco de trabalho</b> é a imagem, dividida em
blocos de <code>rows_per_task = 10</code> linhas (unidades de trabalho). O
processo de rank 0 é o <b>coordenador</b>; os ranks 1..n−1 são
<b>trabalhadores</b>. A <b>iniciativa é dos trabalhadores</b>: cada um envia
<code>TAG_REQUEST</code> pedindo trabalho; o coordenador responde com um bloco
(<code>TAG_TASK</code>) enquanto houver linhas, ou com <code>TAG_STOP</code>
quando o saco esvazia. O trabalhador calcula o bloco e devolve o resultado
(<code>TAG_RESULT</code>: metadados + vetor de pixels). O coordenador grava
cada bloco em <code>image[start_row*WIDTH]</code>, <b>preservando a ordem
original</b> dos vetores independentemente da ordem de chegada (recepção por
ordem de chegada via <code>MPI_Probe</code> / <code>MPI_ANY_SOURCE</code>). O
programa encerra quando todos os trabalhadores recebem <code>STOP</code>.
Verificamos que a imagem gerada é <b>idêntica</b> (mesmo checksum) para
qualquer número de trabalhadores e igual à da versão sequencial, confirmando a
corretude e a preservação da ordem.</p>

<h2>3. Metodologia</h2>
<p>A versão sequencial (referência) executa em um único processo. As medições
paralelas foram feitas em <b>2 nós exclusivos da máquina atlantica</b> (LAD),
variando de 1 a 15 trabalhadores (até 16 processos, 1 nó) e 31 trabalhadores
(32 processos, 2 nós). Caso de teste: imagem 800&times;600. Na <b>escala
forte</b>, MAX_ITER = 10000 é fixo. Na <b>escala fraca</b>, a carga cresce
proporcionalmente ao número de trabalhadores (MAX_ITER &prop; N), mantendo a
carga por trabalhador constante. O tempo de referência é o de 1 trabalhador,
no qual o coordenador não computa — equivalente à execução serial.
Speed-up = T<sub>seq</sub> / T<sub>p</sub> e Eficiência = Speed-up / p.</p>

<h2>4. Resultados e análise</h2>
<p><b>Escala forte.</b> O speed-up cresce de forma quase linear até ~5
trabalhadores e segue subindo, atingindo 10,7&times; com 15 trabalhadores e
20,2&times; com 31. A eficiência cai de 0,97 (2 trab.) para 0,72 (15) e 0,65
(31). A perda decorre de: (i) o coordenador ser um processo serial que não
computa e centraliza a recepção, tornando-se gargalo conforme mais
trabalhadores disputam atendimento; (ii) crescimento do overhead de
comunicação; (iii) efeito de cauda — com 60 blocos, ao aumentar os
trabalhadores cresce a ociosidade no fim do processamento.</p>
<p><b>Balanceamento de carga.</b> A distribuição é <b>dinâmica e orientada por
demanda</b>: trabalhadores ociosos pedem o próximo bloco, o que absorve
naturalmente a forte irregularidade de custo entre as linhas do Mandelbrot.
Blocos de 10 linhas equilibram overhead de mensagens e granularidade. O
resultado determinístico confirma que a ordem é mantida apesar do
não-determinismo de chegada.</p>
<p><b>Escala fraca.</b> Idealmente o tempo permaneceria constante ao escalar
carga e trabalhadores juntos. O tempo medido sobe pouco (10,8 s &rarr; 16,2 s
de 1 a 31 trab.) e a eficiência fraca cai de 1,0 para 0,66 — boa
escalabilidade fraca, com a mesma degradação suave atribuída ao gargalo do
coordenador e à comunicação.</p>

<h2>5. Conclusão</h2>
<p>O modelo coordenador/trabalhador com iniciativa dos trabalhadores forneceu
bom speed-up e balanceamento de carga para um problema fortemente irregular,
escalando até 32 processos em 2 nós. As limitações de eficiência vêm da
serialização no coordenador e do overhead de comunicação, esperados nesse
padrão; blocos adaptativos ou múltiplos coordenadores poderiam mitigá-las.</p>
"""

doc = f"""<!DOCTYPE html><html lang="pt-br"><head><meta charset="utf-8">
<style>
@page {{ size: A4; margin: 1.4cm 1.3cm; }}
* {{ box-sizing: border-box; }}
body {{ font-family: "Times New Roman", Georgia, serif; color:#111;
        font-size: 9.3pt; line-height: 1.28; }}
header.title {{ text-align:center; border-bottom:2px solid #222;
        padding-bottom:6px; margin-bottom:8px; }}
header.title h1 {{ font-size: 14pt; margin:0 0 3px 0; }}
header.title .authors {{ font-size: 9.5pt; }}
header.title .meta {{ font-size: 8.3pt; color:#444; }}
.columns {{ column-count: 2; column-gap: 1.0em; text-align: justify; }}
h2 {{ font-size: 10pt; margin: 7px 0 2px 0; break-after: avoid; }}
p {{ margin: 0 0 5px 0; }}
code {{ font-family: "DejaVu Sans Mono", monospace; font-size: 8pt;
        background:#f2f2f2; padding:0 2px; }}
section.page {{ break-before: page; }}
h2.annex {{ font-size: 12pt; text-align:center; border-bottom:1px solid #999;
        margin-bottom:8px; }}
.grid2 {{ display:grid; grid-template-columns: 1fr 1fr; gap: 6px 14px; }}
table.data {{ border-collapse: collapse; width:100%; font-size:7.6pt; }}
table.data caption {{ font-weight:bold; font-size:8.2pt; margin-bottom:3px; }}
table.data th, table.data td {{ border:1px solid #999; padding:1px 4px;
        text-align:center; }}
table.data th {{ background:#e8e8e8; }}
.figs {{ display:grid; grid-template-columns: 1fr 1fr; gap: 4px; margin-top:10px; }}
.figs img {{ width:100%; }}
.figcap {{ font-size:7.6pt; text-align:center; color:#333; margin-top:-2px; }}
h3.code-title {{ font-family:monospace; font-size:9pt; background:#222;
        color:#fff; padding:3px 6px; margin:10px 0 2px 0; break-before: auto; }}
.highlight {{ font-size:6.6pt; line-height:1.12; }}
.highlight pre {{ white-space: pre-wrap; word-break: break-word; margin:0; }}
{pyg_css}
</style></head><body>

<header class="title">
  <h1>Paralelização do Conjunto de Mandelbrot com MPI<br>
      no Modelo Coordenador/Trabalhador</h1>
  <div class="authors">Bernardo Luiz Padilha Zamin &nbsp;&middot;&nbsp; João Pedro Sostruznik Sotero da Cunha</div>
  <div class="meta">Programação Paralela — Trabalho 2 (MPI) &middot; PUCRS &middot; 2026</div>
</header>

<div class="columns">{analysis}</div>

<section class="page">
  <h2 class="annex">Anexo I — Tabelas e Gráficos</h2>
  <div class="grid2">
    {table(strong, "Tabela 1 — Escala forte (800×600, MAX_ITER=10000)")}
    {table(weak, "Tabela 2 — Escala fraca (carga ∝ N)")}
  </div>
  <div class="figs">
    <div><img src="fig_strong_speedup.png"><div class="figcap">Fig. 1 — Speed-up (escala forte)</div></div>
    <div><img src="fig_strong_eff.png"><div class="figcap">Fig. 2 — Eficiência (escala forte)</div></div>
    <div><img src="fig_weak_speedup.png"><div class="figcap">Fig. 3 — Speed-up (escala fraca)</div></div>
    <div><img src="fig_weak_time.png"><div class="figcap">Fig. 4 — Tempo de execução (escala fraca)</div></div>
  </div>
</section>

<section class="page">
  <h2 class="annex">Anexo II — Código-fonte</h2>
  {code_block(SRC + "/mandelbrot-seq.c", "mandelbrot-seq.c — versão sequencial (referência)")}
  {code_block(SRC + "/mandelbrot-v2.c", "mandelbrot-v2.c — versão paralela MPI (iniciativa dos trabalhadores)")}
</section>

</body></html>"""

HTML(string=doc, base_url=OUT).write_pdf(f"{OUT}/relatorio.pdf")

# diagnostico: numero de paginas
pages = HTML(string=doc, base_url=OUT).render().pages
print("PDF gerado. Paginas:", len(pages))
