/* Design: Cuaderno de Laboratorio — neo-editorial científico, fondo marfil, azul tinta, vermellón de falsación. */
import { useMemo, useState } from "react";
import {
  ArrowUpRight,
  Beaker,
  ChevronRight,
  CircleDot,
  FlaskConical,
  GitBranch,
  Info,
  Menu,
  Network,
  Play,
  Plus,
  Search,
  Sparkles,
  Terminal,
  X,
} from "lucide-react";

const logoUrl = "/manus-storage/forgemind-compass-logo_7c2f3e26.png";
const paperUrl = "/manus-storage/forgemind-lab-paper_0e352c89.jpg";
const fieldUrl = "/manus-storage/forgemind-hypothesis-field_55ca604d.jpg";

type Hypothesis = {
  id: string;
  title: string;
  code: string;
  score: number;
  status: "READY" | "SURVIVED" | "REVIEW";
  color: string;
  metrics: { label: string; value: number; tone: string }[];
  note: string;
};

const hypotheses: Hypothesis[] = [
  {
    id: "H4",
    title: "Permutation invariance",
    code: "rev → sort → neg → rev",
    score: 0.87,
    status: "READY",
    color: "red",
    metrics: [
      { label: "Novedad", value: 72, tone: "ink" },
      { label: "Compresión", value: 91, tone: "yellow" },
      { label: "Falsación", value: 76, tone: "red" },
    ],
    note: "Contiene una conmutación reutilizable y todavía no ha sido aislada por un contraejemplo.",
  },
  {
    id: "H7",
    title: "Signed reflection",
    code: "neg → rev → abs",
    score: 0.81,
    status: "SURVIVED",
    color: "green",
    metrics: [
      { label: "Novedad", value: 56, tone: "ink" },
      { label: "Compresión", value: 84, tone: "yellow" },
      { label: "Falsación", value: 69, tone: "red" },
    ],
    note: "Sobrevive en 36 casos acotados; la equivalencia global continúa desconocida.",
  },
  {
    id: "H2",
    title: "Stable sorting",
    code: "sort → sort → id",
    score: 0.64,
    status: "REVIEW",
    color: "yellow",
    metrics: [
      { label: "Novedad", value: 39, tone: "ink" },
      { label: "Compresión", value: 62, tone: "yellow" },
      { label: "Falsación", value: 51, tone: "red" },
    ],
    note: "Se parece a una regla ya registrada, pero añade complejidad sin evidencia diferencial.",
  },
];

function SignalBar({ value, tone }: { value: number; tone: string }) {
  const toneClass = tone === "red" ? "bg-vermilion" : tone === "yellow" ? "bg-pollen" : "bg-ink";
  return (
    <div className="h-1.5 w-full overflow-hidden rounded-full bg-[#ded8ca]">
      <div className={`h-full rounded-full ${toneClass} transition-all duration-500`} style={{ width: `${value}%` }} />
    </div>
  );
}

function ScoreDial({ score }: { score: number }) {
  const rotation = -112 + score * 224;
  return (
    <div className="relative h-28 w-28 shrink-0 rounded-full border-[7px] border-[#ded8ca] bg-[#f7f3e9] shadow-[inset_0_0_0_1px_rgba(32,49,65,.08)]">
      <div className="absolute inset-[9px] rounded-full border border-dashed border-ink/20" />
      <div className="absolute left-1/2 top-1/2 h-[3px] w-10 origin-left bg-vermilion transition-transform duration-300" style={{ transform: `rotate(${rotation}deg)` }}>
        <span className="absolute -right-1.5 -top-1.5 h-3 w-3 rounded-full bg-vermilion ring-4 ring-vermilion/10" />
      </div>
      <div className="absolute left-1/2 top-1/2 h-2.5 w-2.5 -translate-x-1/2 -translate-y-1/2 rounded-full bg-ink" />
      <div className="absolute inset-x-0 bottom-3 text-center font-mono text-[9px] uppercase tracking-[0.22em] text-ink/45">intuición</div>
    </div>
  );
}

export default function Home() {
  const [selectedId, setSelectedId] = useState("H4");
  const [mobileNav, setMobileNav] = useState(false);
  const [runState, setRunState] = useState<"idle" | "running" | "done">("idle");
  const selected = useMemo(() => hypotheses.find((item) => item.id === selectedId) ?? hypotheses[0], [selectedId]);

  const runExperiment = () => {
    setRunState("running");
    window.setTimeout(() => setRunState("done"), 850);
  };

  return (
    <div className="min-h-screen bg-paper text-ink">
      <div className="pointer-events-none fixed inset-0 bg-[url('/manus-storage/forgemind-lab-paper_0e352c89.jpg')] bg-cover bg-center opacity-[0.14] mix-blend-multiply" />
      <aside className={`fixed inset-y-0 left-0 z-40 w-[260px] border-r border-ink/10 bg-[#f2eee3]/95 px-5 py-6 backdrop-blur-xl transition-transform duration-200 lg:translate-x-0 ${mobileNav ? "translate-x-0" : "-translate-x-full"}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <img src={logoUrl} alt="ForgeMind compass" className="h-10 w-10 object-contain" />
            <div>
              <div className="font-serif text-xl leading-none">ForgeMind</div>
              <div className="mt-1 font-mono text-[9px] uppercase tracking-[0.22em] text-ink/45">intuition engine</div>
            </div>
          </div>
          <button className="rounded-md p-1 text-ink/50 hover:bg-ink/5 lg:hidden" onClick={() => setMobileNav(false)} aria-label="Cerrar navegación"><X size={17} /></button>
        </div>
        <div className="mt-12 font-mono text-[10px] uppercase tracking-[0.24em] text-ink/40">Workspace</div>
        <nav className="mt-4 space-y-1">
          {[{ icon: Network, label: "Hipótesis", active: true }, { icon: FlaskConical, label: "Experimentos" }, { icon: GitBranch, label: "Reglas y equivalencias" }, { icon: Terminal, label: "Agente de código" }].map(({ icon: Icon, label, active }) => (
            <button key={label} className={`group flex w-full items-center gap-3 border-l-2 px-3 py-3 text-left text-sm transition-colors ${active ? "border-vermilion bg-[#e8dfd1] font-medium text-ink" : "border-transparent text-ink/55 hover:border-ink/20 hover:bg-ink/5"}`}>
              <Icon size={16} strokeWidth={1.7} className={active ? "text-vermilion" : "text-ink/40"} />
              <span>{label}</span>
              {active && <ChevronRight size={14} className="ml-auto text-vermilion" />}
            </button>
          ))}
        </nav>
        <div className="mt-10 border-t border-ink/10 pt-5">
          <div className="flex items-center justify-between font-mono text-[10px] uppercase tracking-[0.18em] text-ink/40"><span>Memoria</span><span className="text-green">0.16</span></div>
          <div className="mt-3 flex items-center gap-2 text-sm text-ink/70"><span className="h-2 w-2 rounded-full bg-green shadow-[0_0_0_4px_rgba(79,117,96,.12)]" /> 148 casos observados</div>
          <div className="mt-2 flex items-center gap-2 text-sm text-ink/70"><span className="h-2 w-2 rounded-full bg-pollen shadow-[0_0_0_4px_rgba(223,177,72,.14)]" /> 23 reglas activas</div>
        </div>
        <div className="absolute bottom-6 left-5 right-5 border-t border-ink/10 pt-4 text-[11px] leading-relaxed text-ink/45">La intuición decide qué falsar primero. Nunca decide qué es verdad.</div>
      </aside>

      <main className="relative lg:pl-[260px]">
        <header className="flex h-[76px] items-center justify-between border-b border-ink/10 px-5 sm:px-8 lg:px-12">
          <div className="flex items-center gap-3"><button className="rounded-md p-2 hover:bg-ink/5 lg:hidden" onClick={() => setMobileNav(true)} aria-label="Abrir navegación"><Menu size={20} /></button><div className="flex items-center gap-2.5"><img src={logoUrl} alt="" className="h-8 w-8 object-contain" /><span className="font-serif text-xl tracking-[-0.03em]">ForgeMind</span><span className="hidden h-5 w-px bg-ink/15 sm:block" /><span className="hidden font-mono text-[10px] uppercase tracking-[0.2em] text-ink/45 sm:block">intuition engine</span></div></div>
          <div className="flex items-center gap-2 sm:gap-5"><div className="hidden items-center gap-2 text-xs text-ink/45 sm:flex"><span className="h-2 w-2 rounded-full bg-green" /> Engine online</div><button className="rounded-md p-2 text-ink/45 hover:bg-ink/5" aria-label="Buscar"><Search size={17} /></button><div className="flex h-8 w-8 items-center justify-center rounded-full border border-ink/15 bg-[#e6dece] font-serif text-sm">M</div></div>
        </header>

        <div className="px-5 py-8 sm:px-8 lg:px-12 lg:py-12">
          <section className="relative overflow-hidden border border-ink/15 bg-[#e9e0d1] px-6 py-9 text-ink shadow-[0_20px_50px_rgba(32,49,65,.12)] sm:px-9 sm:py-11">
            <div className="absolute inset-0 bg-[url('/manus-storage/forgemind-hypothesis-field_55ca604d.jpg')] bg-cover bg-center opacity-35 mix-blend-multiply" /><div className="absolute right-8 top-7 hidden border-l border-vermilion/45 pl-3 font-mono text-[9px] uppercase leading-5 tracking-[0.18em] text-ink/45 md:block">plate 016.3<br />bounded field<br /><span className="text-vermilion">counterexample ready</span></div>
            <div className="relative max-w-2xl"><div className="mb-5 flex items-center gap-3 font-mono text-[10px] uppercase tracking-[0.25em] text-vermilion"><span className="h-px w-7 bg-vermilion" /> Iteración 0.16.3 / calibración</div><h1 className="max-w-xl font-serif text-4xl leading-[0.98] tracking-[-0.035em] sm:text-6xl">No busques la respuesta.<br /><em className="text-vermilion">Elige el experimento.</em></h1><p className="mt-6 max-w-lg text-sm leading-7 text-ink/65 sm:text-base">ForgeMind conserva evidencia, compara estructuras y señala qué hipótesis puede enseñarnos más al ser falsada.</p><div className="mt-8 flex flex-wrap items-center gap-3"><button onClick={runExperiment} className="group inline-flex items-center gap-2 bg-vermilion px-4 py-3 text-xs font-semibold uppercase tracking-[0.16em] text-white transition-transform duration-150 hover:bg-[#f0644d] active:scale-[.97]"><Play size={14} fill="currentColor" /> {runState === "running" ? "Ejecutando…" : runState === "done" ? "Experimento listo" : "Falsar H4 primero"}<ArrowUpRight size={14} className="transition-transform group-hover:-translate-y-0.5 group-hover:translate-x-0.5" /></button><button className="inline-flex items-center gap-2 border border-ink/20 px-4 py-3 text-xs font-semibold uppercase tracking-[0.16em] text-ink/75 hover:border-ink/45 hover:text-ink"><Info size={14} /> Ver método</button></div></div>
            <div className="absolute bottom-7 right-8 hidden items-end gap-4 md:flex"><div className="text-right"><div className="font-mono text-[9px] uppercase tracking-[0.2em] text-ink/45">Casos bounded</div><div className="mt-1 font-serif text-3xl text-ink">36</div></div><div className="h-10 w-px bg-ink/20" /><div className="text-right"><div className="font-mono text-[9px] uppercase tracking-[0.2em] text-ink/45">Contraejemplos</div><div className="mt-1 font-serif text-3xl text-vermilion">0</div></div></div>
          </section>

          <section className="mt-10 grid gap-10 xl:grid-cols-[minmax(0,1.35fr)_minmax(340px,.65fr)]">
            <div>
              <div className="flex items-end justify-between border-b border-ink/15 pb-4"><div><div className="font-mono text-[10px] uppercase tracking-[0.24em] text-vermilion">01 / Población activa</div><h2 className="mt-2 font-serif text-3xl tracking-[-0.025em]">Hipótesis supervivientes</h2></div><button className="hidden items-center gap-2 text-xs font-semibold text-ink/55 hover:text-ink sm:flex"><Plus size={15} /> Añadir candidata</button></div>
              <div className="mt-5 space-y-3">{hypotheses.map((item, index) => { const isSelected = item.id === selected.id; return <button key={item.id} onClick={() => setSelectedId(item.id)} className={`group relative w-full overflow-hidden border text-left transition-all duration-200 ${isSelected ? "border-vermilion/45 bg-[#f7f3e9] shadow-[0_12px_30px_rgba(32,49,65,.08)]" : "border-ink/10 bg-[#f1ece1]/60 hover:border-ink/25 hover:bg-[#f7f3e9]"}`}><div className={`absolute inset-y-0 left-0 w-1 ${item.color === "red" ? "bg-vermilion" : item.color === "green" ? "bg-green" : "bg-pollen"}`} /><div className="flex items-center gap-4 px-4 py-4 sm:px-5"><div className="w-10 shrink-0 font-mono text-[11px] text-ink/35">0{index + 1}<br /><span className="text-vermilion">{item.id}</span></div><div className="min-w-0 flex-1"><div className="flex flex-wrap items-center gap-2"><span className="font-serif text-lg">{item.title}</span><span className={`rounded-sm px-1.5 py-0.5 font-mono text-[9px] uppercase tracking-[0.16em] ${item.status === "READY" ? "bg-vermilion/10 text-vermilion" : item.status === "SURVIVED" ? "bg-green/10 text-green" : "bg-pollen/20 text-[#8b6715]"}`}>{item.status}</span></div><div className="mt-1 font-mono text-xs text-ink/50">{item.code}</div></div><div className="hidden w-40 gap-2 sm:block">{item.metrics.map((metric) => <div key={metric.label} className="mb-1.5 flex items-center gap-2"><span className="w-16 font-mono text-[8px] uppercase tracking-wider text-ink/40">{metric.label}</span><SignalBar value={metric.value} tone={metric.tone} /></div>)}</div><div className={`flex h-14 w-14 shrink-0 items-center justify-center rounded-full border text-lg font-serif ${isSelected ? "border-vermilion bg-vermilion/5 text-vermilion" : "border-ink/15 text-ink/65"}`}>{item.score.toFixed(2)}</div><ChevronRight size={16} className={`shrink-0 transition-transform ${isSelected ? "translate-x-1 text-vermilion" : "text-ink/25 group-hover:translate-x-1"}`} /></div></button> })}</div>
              <button className="mt-4 flex w-full items-center justify-center gap-2 border border-dashed border-ink/20 py-3 text-xs font-medium text-ink/45 hover:border-ink/40 hover:text-ink/70 sm:hidden"><Plus size={15} /> Añadir candidata</button>
            </div>

            <aside className="relative border-t border-ink/15 pt-5 xl:border-l xl:border-t-0 xl:pl-8 xl:pt-0"><div className="font-mono text-[10px] uppercase tracking-[0.24em] text-vermilion">02 / Cuaderno de razones</div><div className="mt-2 flex items-start justify-between gap-4"><div><h2 className="font-serif text-3xl tracking-[-0.025em]">{selected.id} / {selected.title}</h2><div className="mt-2 inline-flex items-center gap-2 rounded-sm bg-ink px-2 py-1 font-mono text-[11px] text-paper"><CircleDot size={12} className="text-pollen" /> {selected.code}</div></div><ScoreDial score={selected.score} /></div><p className="mt-6 text-sm leading-6 text-ink/65">{selected.note}</p><div className="mt-7 border-t border-ink/10 pt-5"><div className="flex items-center justify-between"><div className="font-mono text-[10px] uppercase tracking-[0.2em] text-ink/40">Contribuciones</div><div className="font-mono text-[10px] text-ink/35">score / 0.87</div></div><div className="mt-4 space-y-4">{[{ label: "similarity_to_survivors", value: "+0.24", width: 78, tone: "ink" }, { label: "compression_potential", value: "+0.21", width: 91, tone: "yellow" }, { label: "falsification_value", value: "+0.16", width: 66, tone: "red" }, { label: "complexity_penalty", value: "−0.04", width: 18, tone: "red" }].map((row) => <div key={row.label}><div className="mb-1.5 flex items-center justify-between gap-3 font-mono text-[10px]"><span className="text-ink/55">{row.label}</span><span className={row.value.startsWith("−") ? "text-vermilion" : "text-ink"}>{row.value}</span></div><SignalBar value={row.width} tone={row.tone} /></div>)}</div></div><div className="mt-7 border-l-2 border-pollen bg-pollen/10 px-4 py-3 text-xs leading-5 text-ink/70"><div className="mb-1 font-mono text-[9px] uppercase tracking-[0.2em] text-[#8b6715]">Lectura del motor</div>H4 contiene un patrón de conmutación reutilizable. Su valor no está en ser correcta, sino en separar familias rivales con bajo coste.</div><button onClick={runExperiment} className="mt-5 flex w-full items-center justify-between bg-ink px-4 py-3 text-xs font-semibold uppercase tracking-[0.14em] text-paper transition-transform duration-150 hover:bg-ink/90 active:scale-[.98]"><span className="flex items-center gap-2"><Beaker size={15} className="text-pollen" /> Ejecutar experimento</span><span className="font-mono text-[10px] text-paper/50">coste · 18 probes</span></button></aside>
          </section>

          <section className="mt-12 border-t border-ink/15 pt-5"><div className="flex flex-wrap items-center justify-between gap-4"><div><div className="font-mono text-[10px] uppercase tracking-[0.24em] text-vermilion">03 / Estado de conocimiento</div><h2 className="mt-2 font-serif text-2xl">Geometría de la búsqueda</h2></div><button className="inline-flex items-center gap-2 text-xs font-semibold text-ink/50 hover:text-ink">Abrir mapa completo <ArrowUpRight size={14} /></button></div><div className="mt-5 grid gap-0 border-y border-ink/10 sm:grid-cols-3"><div className="border-b border-ink/10 py-5 sm:border-b-0 sm:border-r sm:pr-5"><div className="flex items-center justify-between"><span className="font-mono text-[10px] uppercase tracking-[0.16em] text-ink/45">Candidatas</span><Network size={15} className="text-ink/35" /></div><div className="mt-5 flex items-end gap-3"><div className="font-serif text-3xl">39</div><div className="mb-1 font-mono text-[9px] text-ink/45">observadas</div></div><div className="mt-2 flex items-center gap-2 text-xs text-ink/50"><span className="h-px w-5 bg-vermilion" /> 12 normalizadas / origen: search</div></div><div className="border-b border-ink/10 py-5 sm:border-b-0 sm:border-r sm:px-5"><div className="flex items-center justify-between"><span className="font-mono text-[10px] uppercase tracking-[0.16em] text-ink/45">Clases semánticas</span><Sparkles size={15} className="text-pollen" /></div><div className="mt-5 flex items-end gap-3"><div className="font-serif text-3xl">8</div><div className="mb-1 font-mono text-[9px] text-ink/45">supervivientes</div></div><div className="mt-2 flex items-center gap-2 text-xs text-ink/50"><span className="h-px w-5 bg-pollen" /> 42.16% reducción / método: bounded</div></div><div className="py-5 sm:pl-5"><div className="flex items-center justify-between"><span className="font-mono text-[10px] uppercase tracking-[0.16em] text-ink/45">Comportamiento</span><CircleDot size={15} className="text-green" /></div><div className="mt-5 flex items-end gap-3"><div className="font-serif text-3xl text-green">preserved</div></div><div className="mt-2 flex items-center gap-2 text-xs text-ink/50"><span className="h-px w-5 bg-green" /> evidencia bounded / 36 casos · 0 contraejemplos</div></div></div></section>
        </div>
        <footer className="flex flex-wrap items-center justify-between gap-3 border-t border-ink/10 px-5 py-5 text-[10px] uppercase tracking-[0.18em] text-ink/35 sm:px-8 lg:px-12"><span>ForgeMind / intuition engine</span><span>Experimental support for coding agents</span><span>Confidence ≠ truth probability</span></footer>
      </main>
    </div>
  );
}
