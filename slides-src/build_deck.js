const pptxgen = require("pptxgenjs");
const A = "/tmp/slides";

const NAVY = "1B2A4A", TEAL = "1C7293", ORANGE = "E8833A",
      ICE = "CADCFC", WHITE = "FFFFFF", DARK = "222A35", MUTED = "6B7280";
const shadow = () => ({ type: "outer", color: "000000", blur: 7, offset: 3, angle: 135, opacity: 0.22 });

let p = new pptxgen();
p.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
p.author = "Bernardo Zamin; Joao Pedro Sostruznik Sotero da Cunha";
p.title = "Paralelizacao do Conjunto de Mandelbrot com MPI";

/* ---------- Slide 1: Titulo ---------- */
let s = p.addSlide();
s.background = { color: NAVY };
s.addImage({ path: `${A}/mandelbrot.png`, x: 8.4, y: 0, w: 4.93, h: 7.5,
             sizing: { type: "cover", w: 4.93, h: 7.5 } });
s.addShape(p.shapes.RECTANGLE, { x: 0.7, y: 1.95, w: 0.55, h: 0.14, fill: { color: TEAL } });
s.addText("Paralelização do Conjunto de Mandelbrot com MPI", {
  x: 0.7, y: 2.25, w: 7.2, h: 1.5, fontSize: 33, bold: true, color: WHITE,
  fontFace: "Georgia", align: "left", valign: "top", margin: 0 });
s.addText("Modelo Coordenador/Trabalhador (SPMD)", {
  x: 0.7, y: 3.85, w: 7.2, h: 0.5, fontSize: 19, color: TEAL, fontFace: "Calibri",
  bold: true, align: "left", margin: 0 });
s.addText([
  { text: "Bernardo Luiz Padilha Zamin", options: { breakLine: true } },
  { text: "João Pedro Sostruznik Sotero da Cunha" }
], { x: 0.7, y: 4.75, w: 7.2, h: 1.0, fontSize: 18, color: ICE, fontFace: "Calibri",
     align: "left", paraSpaceAfter: 4, margin: 0 });
s.addText("Programação Paralela  ·  Trabalho 2 (MPI)  ·  PUCRS  ·  2026", {
  x: 0.7, y: 6.55, w: 7.2, h: 0.4, fontSize: 13, color: "9FB2D6", fontFace: "Calibri",
  align: "left", margin: 0 });

/* ---------- Slide 2: Problema ---------- */
s = p.addSlide();
s.background = { color: WHITE };
s.addText("O Problema: Conjunto de Mandelbrot", {
  x: 0.6, y: 0.45, w: 12.1, h: 0.7, fontSize: 30, bold: true, color: NAVY,
  fontFace: "Georgia", align: "left", margin: 0 });
const bullet = (t) => ({ text: t, options: { bullet: { code: "2022" }, breakLine: true } });
s.addText([
  bullet("Para cada pixel da imagem (800×600), itera-se z = z² + c até |z| > 2 ou atingir MAX_ITER; o nº de iterações define a cor."),
  bullet("Custo por pixel é irregular: pontos no interior do conjunto fazem todas as iterações; os de fora escapam cedo."),
  bullet("Paralelização em C + MPI no modelo coordenador/trabalhador (SPMD)."),
  bullet("Saco de trabalho = linhas da imagem, distribuídas em blocos de 10 linhas."),
  bullet("Iniciativa dos trabalhadores: cada um pede tarefa ao coordenador até o saco esvaziar."),
  { text: "O coordenador remonta a imagem preservando a ordem original dos blocos.",
    options: { bullet: { code: "2022" } } }
], { x: 0.6, y: 1.55, w: 7.4, h: 5.3, fontSize: 17, color: DARK, fontFace: "Calibri",
     align: "left", paraSpaceAfter: 11, lineSpacingMultiple: 1.0 });
s.addImage({ path: `${A}/mandelbrot.png`, x: 8.45, y: 1.7, w: 4.35, h: 3.26, shadow: shadow() });
s.addText("Imagem gerada pelo programa (região do código).", {
  x: 8.45, y: 5.05, w: 4.35, h: 0.4, fontSize: 12, italic: true, color: MUTED,
  fontFace: "Calibri", align: "center", margin: 0 });

/* ---------- Slides de graficos ---------- */
function graphSlide(title, tag, tagColor, img, takeaway) {
  let g = p.addSlide();
  g.background = { color: WHITE };
  g.addText(title, { x: 0.6, y: 0.42, w: 10.0, h: 0.7, fontSize: 27, bold: true,
    color: NAVY, fontFace: "Georgia", align: "left", valign: "middle", margin: 0 });
  g.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 10.95, y: 0.5, w: 1.9, h: 0.52,
    fill: { color: tagColor }, rectRadius: 0.1 });
  g.addText(tag, { x: 10.95, y: 0.5, w: 1.9, h: 0.52, fontSize: 13, bold: true,
    color: WHITE, fontFace: "Calibri", align: "center", valign: "middle", margin: 0 });
  // chart 6.6x4.2 ratio -> h=4.75, w=7.46, centrado
  g.addImage({ path: `${A}/${img}`, x: 2.93, y: 1.25, w: 7.46, h: 4.75 });
  g.addText(takeaway, { x: 1.3, y: 6.25, w: 10.7, h: 0.9, fontSize: 16, color: NAVY,
    fontFace: "Calibri", align: "center", valign: "top", margin: 0 });
  return g;
}

graphSlide("Escala forte — Speed-up", "Escala forte", TEAL, "chart_strong_sp.png",
  "Crescimento quase linear até ~5 trabalhadores; atinge 10,7× com 15 e 20,2× com 31.");
graphSlide("Escala forte — Eficiência", "Escala forte", TEAL, "chart_strong_eff.png",
  "Cai de 0,97 (2 trab.) para 0,72 (15) e 0,65 (31): gargalo do coordenador + overhead de comunicação.");
graphSlide("Escala fraca — Speed-up", "Escala fraca", ORANGE, "chart_weak_sp.png",
  "Com a carga crescendo junto (10000×N iterações), o speed-up alcança 20,4× com 31 trabalhadores.");
graphSlide("Escala fraca — Eficiência", "Escala fraca", ORANGE, "chart_weak_eff.png",
  "Boa escalabilidade fraca: a eficiência cai suavemente de 1,0 para 0,66.");

p.writeFile({ fileName: `${A}/apresentacao.pptx` }).then(f => console.log("OK:", f));
