/* ForgeMind Intuition — workspace conectado al contrato público de la API. */
import { useEffect, useMemo, useState } from "react";
import { ArrowUpRight, Beaker, ChevronRight, CircleDot, FlaskConical, GitBranch, Info, Menu, Network, Play, Search, Sparkles, Terminal, X } from "lucide-react";
import { evaluateProject, getEngineHealth, type CandidateAdvice, type ProjectInput } from "../lib/forgemind-api";

const logoUrl = "/manus-storage/forgemind-compass-logo_7c2f3e26.png";
const projectInput: ProjectInput = {
  schema_version: "1.0",
  name: "intuition-playground",
  candidates: [
    { id: "H4", description: "Permutation invariance", program: [{ kind: "U", name: "rev" }, { kind: "U", name: "sort" }, { kind: "U", name: "neg" }, { kind: "U", name: "rev" }] },
    { id: "H7", description: "Signed reflection", program: [{ kind: "U", name: "neg" }, { kind: "U", name: "rev" }, { kind: "U", name: "abs" }] },
    { id: "H2", description: "Stable sorting", program: [{ kind: "U", name: "sort" }, { kind: "U", name: "sort" }, { kind: "U", name: "id" }] },
  ],
  probes: [[1, 2, 3], [3, 1, 2], [2, 2, 1]],
  targets: [],
  metadata: { source: "frontend-public-api" },
  knowledge: [],
};

type ViewHypothesis = CandidateAdvice & { id: string; title: string; code: string; status: "READY" | "SURVIVED" | "REVIEW"; color: "red" | "green" | "yellow" };

function asPercent(value: number) { return Math.max(0, Math.min(100, Math.round(value * 100))); }
function mapAdvice(advice: CandidateAdvice[], project: ProjectInput): ViewHypothesis[] {
  return advice.map((item) => {
    const candidate = project.candidates[item.candidate_index];
    const value = item.experimental_value;
    return {
      ...item,
      id: candidate?.id || `candidate-${item.candidate_index + 1}`,
      title: candidate?.description || `Candidate ${item.candidate_index + 1}`,
      code: (candidate?.program || []).map((node) => node.name).join(" → "),
      status: value > 0.9 ? "READY" : value > 0.3 ? "SURVIVED" : "REVIEW",
      color: value > 0.9 ? "red" : value > 0.3 ? "green" : "yellow",
    };
  });
}

function SignalBar({ value, tone }: { value: number; tone: string }) {
  const toneClass = tone === "red" ? "bg-vermilion" : tone === "yellow" ? "bg-pollen" : "bg-ink";
  return <div className="h-1.5 w-full overflow-hidden rounded-full bg-[#ded8ca]"><div className={`h-full rounded-full ${toneClass}`} style={{ width: `${value}%` }} /></div>;
}
function ScoreDial({ score }: { score: number }) {
  const rotation = -112 + score * 224;
  return <div className="relative h-28 w-28 shrink-0 rounded-full border-[7px] border-[#ded8ca] bg-[#f7f3e9]"><div className="absolute inset-[9px] rounded-full border border-dashed border-ink/20" /><div className="absolute left-1/2 top-1/2 h-[3px] w-10 origin-left bg-vermilion" style={{ transform: `rotate(${rotation}deg)` }} /><div className="absolute left-1/2 top-1/2 h-2.5 w-2.5 -translate-x-1/2 -translate-y-1/2 rounded-full bg-ink" /><div className="absolute inset-x-0 bottom-3 text-center font-mono text-[9px] uppercase tracking-[0.22em] text-ink/45">valor</div></div>;
}

export default function Home() {
  const [selectedId, setSelectedId] = useState("H4");
  const [mobileNav, setMobileNav] = useState(false);
  const [runState, setRunState] = useState<"idle" | "running" | "done">("idle");
  const [results, setResults] = useState<CandidateAdvice[]>([]);
  const [apiError, setApiError] = useState<string | null>(null);
  const [engineOnline, setEngineOnline] = useState(false);
  const hypotheses = useMemo(() => mapAdvice(results, projectInput), [results]);
  const selected = useMemo(() => hypotheses.find((item) => item.id === selectedId) || hypotheses[0], [hypotheses, selectedId]);

  const runExperiment = async () => {
    setRunState("running");
    setApiError(null);
    try {
      const response = await evaluateProject(projectInput);
      setResults(response.results);
      setRunState("done");
      if (response.results[0]) setSelectedId(projectInput.candidates[response.results[0].candidate_index]?.id || "H4");
    } catch (error) {
      setApiError(error instanceof Error ? error.message : "No se pudo evaluar el proyecto");
      setRunState("idle");
    }
  };

  useEffect(() => {
    getEngineHealth().then(() => setEngineOnline(true)).catch(() => setEngineOnline(false));
    void runExperiment();
  }, []);

  if (runState === "running" && !selected) return <div className="min-h-screen bg-paper p-10 font-mono text-sm text-ink/60">Conectando con ForgeMind API…</div>;
  if (apiError && !selected) return <div className="min-h-screen bg-paper p-10 font-mono text-sm text-vermilion">API no disponible: {apiError}<button onClick={runExperiment} className="ml-4 border border-vermilion px-3 py-2">Reintentar</button></div>;
  if (!selected) return <div className="min-h-screen bg-paper p-10"><div className="border border-dashed border-ink/20 p-8"><div className="font-mono text-[10px] uppercase tracking-[0.2em] text-vermilion">Población vacía</div><h1 className="mt-3 font-serif text-3xl">La API no devolvió hipótesis.</h1><p className="mt-3 text-sm text-ink/60">Revisa el contrato ProjectInput y vuelve a ejecutar la evaluación.</p></div></div>;

  return <div className="min-h-screen bg-paper text-ink"><div className="pointer-events-none fixed inset-0 bg-[url('/manus-storage/forgemind-lab-paper_0e352c89.jpg')] bg-cover bg-center opacity-[0.14] mix-blend-multiply" />
    <aside className={`fixed inset-y-0 left-0 z-40 w-[260px] border-r border-ink/10 bg-[#f2eee3]/95 px-5 py-6 backdrop-blur-xl transition-transform duration-200 lg:translate-x-0 ${mobileNav ? "translate-x-0" : "-translate-x-full"}`}><div className="flex items-center justify-between"><div className="flex items-center gap-3"><img src={logoUrl} alt="ForgeMind compass" className="h-10 w-10 object-contain" /><div><div className="font-serif text-xl leading-none">ForgeMind</div><div className="mt-1 font-mono text-[9px] uppercase tracking-[0.22em] text-ink/45">intuition engine</div></div></div><button className="lg:hidden" onClick={() => setMobileNav(false)} aria-label="Cerrar navegación"><X size={17} /></button></div><div className="mt-12 font-mono text-[10px] uppercase tracking-[0.24em] text-ink/40">Workspace</div><nav className="mt-4 space-y-1">{[{ icon: Network, label: "Hipótesis", active: true }, { icon: FlaskConical, label: "Experimentos" }, { icon: GitBranch, label: "Reglas y equivalencias" }, { icon: Terminal, label: "Agente de código" }].map(({ icon: Icon, label, active }) => <button key={label} className={`group flex w-full items-center gap-3 border-l-2 px-3 py-3 text-left text-sm ${active ? "border-vermilion bg-[#e8dfd1] font-medium" : "border-transparent text-ink/55"}`}><Icon size={16} /><span>{label}</span>{active && <ChevronRight size={14} className="ml-auto text-vermilion" />}</button>)}</nav><div className="mt-10 border-t border-ink/10 pt-5"><div className="flex items-center justify-between font-mono text-[10px] uppercase tracking-[0.18em] text-ink/40"><span>API pública</span><span className={engineOnline ? "text-green" : "text-vermilion"}>{engineOnline ? "online" : "offline"}</span></div><div className="mt-3 text-sm text-ink/70">POST /v1/evaluate</div><div className="mt-2 text-sm text-ink/70">GET /health</div></div></aside>
    <main className="relative lg:pl-[260px]"><header className="flex h-[76px] items-center justify-between border-b border-ink/10 px-5 sm:px-8 lg:px-12"><div className="flex items-center gap-3"><button className="p-2 lg:hidden" onClick={() => setMobileNav(true)} aria-label="Abrir navegación"><Menu size={20} /></button><img src={logoUrl} alt="" className="h-8 w-8 object-contain" /><span className="font-serif text-xl">ForgeMind</span><span className="hidden font-mono text-[10px] uppercase tracking-[0.2em] text-ink/45 sm:block">public api client</span></div><div className="flex items-center gap-3"><span className={`hidden items-center gap-2 text-xs sm:flex ${engineOnline ? "text-green" : "text-vermilion"}`}><span className="h-2 w-2 rounded-full bg-current" /> {engineOnline ? "Engine online" : "Engine offline"}</span><Search size={17} className="text-ink/45" /><div className="flex h-8 w-8 items-center justify-center rounded-full border border-ink/15 bg-[#e6dece] font-serif text-sm">M</div></div></header>
      <div className="px-5 py-8 sm:px-8 lg:px-12 lg:py-12"><section className="relative overflow-hidden border border-ink/15 bg-[#e9e0d1] px-6 py-9 shadow-[0_20px_50px_rgba(32,49,65,.12)] sm:px-9 sm:py-11"><div className="absolute inset-0 bg-[url('/manus-storage/forgemind-hypothesis-field_55ca604d.jpg')] bg-cover bg-center opacity-35 mix-blend-multiply" /><div className="relative max-w-2xl"><div className="mb-5 flex items-center gap-3 font-mono text-[10px] uppercase tracking-[0.25em] text-vermilion"><span className="h-px w-7 bg-vermilion" /> API pública / contrato 1.0</div><h1 className="max-w-xl font-serif text-4xl leading-[0.98] sm:text-6xl">No busques la respuesta.<br /><em className="text-vermilion">Elige el experimento.</em></h1><p className="mt-6 max-w-lg text-sm leading-7 text-ink/65 sm:text-base">La copia versionada de frontend/ envía ProjectInput a la API pública y muestra el ranking explicable devuelto por el motor.</p><div className="mt-8 flex flex-wrap items-center gap-3"><button onClick={runExperiment} className="inline-flex items-center gap-2 bg-vermilion px-4 py-3 text-xs font-semibold uppercase tracking-[0.16em] text-white active:scale-[.97]"><Play size={14} fill="currentColor" /> {runState === "running" ? "Evaluando…" : runState === "done" ? "Evaluación lista" : "Evaluar proyecto"}<ArrowUpRight size={14} /></button><button className="inline-flex items-center gap-2 border border-ink/20 px-4 py-3 text-xs font-semibold uppercase tracking-[0.16em] text-ink/75"><Info size={14} /> Contrato 1.0</button></div>{apiError && <p className="mt-4 font-mono text-[11px] text-vermilion">{apiError}</p>}</div></section>
        <section className="mt-10 grid gap-10 xl:grid-cols-[minmax(0,1.35fr)_minmax(340px,.65fr)]"><div><div className="flex items-end justify-between border-b border-ink/15 pb-4"><div><div className="font-mono text-[10px] uppercase tracking-[0.24em] text-vermilion">01 / Respuesta API</div><h2 className="mt-2 font-serif text-3xl">Hipótesis rankeadas</h2></div><span className="font-mono text-[10px] text-ink/40">{results.length} candidatas</span></div><div className="mt-5 space-y-3">{hypotheses.map((item, index) => <button key={item.id} onClick={() => setSelectedId(item.id)} className={`group relative w-full overflow-hidden border text-left ${item.id === selected.id ? "border-vermilion/45 bg-[#f7f3e9]" : "border-ink/10 bg-[#f1ece1]/60"}`}><div className={`absolute inset-y-0 left-0 w-1 ${item.color === "red" ? "bg-vermilion" : item.color === "green" ? "bg-green" : "bg-pollen"}`} /><div className="flex items-center gap-4 px-4 py-4 sm:px-5"><div className="w-10 shrink-0 font-mono text-[11px] text-ink/35">0{index + 1}<br /><span className="text-vermilion">{item.id}</span></div><div className="min-w-0 flex-1"><div className="flex flex-wrap items-center gap-2"><span className="font-serif text-lg">{item.title}</span><span className="rounded-sm bg-ink/5 px-1.5 py-0.5 font-mono text-[9px] uppercase tracking-[0.16em]">{item.status}</span></div><div className="mt-1 font-mono text-xs text-ink/50">{item.code}</div></div><div className="hidden w-40 gap-2 sm:block"><div className="mb-1.5 flex items-center gap-2"><span className="w-16 font-mono text-[8px] uppercase text-ink/40">Novedad</span><SignalBar value={asPercent(item.intuition.novelty)} tone="ink" /></div><div className="mb-1.5 flex items-center gap-2"><span className="w-16 font-mono text-[8px] uppercase text-ink/40">Falsación</span><SignalBar value={asPercent(item.intuition.falsification_value)} tone="red" /></div></div><div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full border border-ink/15 text-lg font-serif">{item.experimental_value.toFixed(2)}</div><ChevronRight size={16} /></div></button>)}</div></div>
          <aside className="border-t border-ink/15 pt-5 xl:border-l xl:border-t-0 xl:pl-8 xl:pt-0"><div className="font-mono text-[10px] uppercase tracking-[0.24em] text-vermilion">02 / Cuaderno de razones</div><div className="mt-2 flex items-start justify-between gap-4"><div><h2 className="font-serif text-3xl">{selected.id} / {selected.title}</h2><div className="mt-2 inline-flex items-center gap-2 rounded-sm bg-ink px-2 py-1 font-mono text-[11px] text-paper"><CircleDot size={12} className="text-pollen" /> {selected.code}</div></div><ScoreDial score={Math.max(0, Math.min(1, selected.experimental_value))} /></div><p className="mt-6 text-sm leading-6 text-ink/65">{selected.recommendation}</p><div className="mt-7 border-t border-ink/10 pt-5"><div className="font-mono text-[10px] uppercase tracking-[0.2em] text-ink/40">Razones devueltas por la API</div><div className="mt-4 space-y-3">{selected.intuition.reasons.map((reason) => <div key={reason} className="border-l-2 border-pollen bg-pollen/10 px-3 py-2 text-xs leading-5 text-ink/70">{reason}</div>)}</div></div><button onClick={runExperiment} className="mt-6 flex w-full items-center justify-between bg-ink px-4 py-3 text-xs font-semibold uppercase tracking-[0.14em] text-paper"><span className="flex items-center gap-2"><Beaker size={15} className="text-pollen" /> Repetir evaluación</span><span className="font-mono text-[10px] text-paper/50">/v1/evaluate</span></button></aside></section>
        <section className="mt-12 border-t border-ink/15 pt-5"><div className="flex items-center justify-between"><div><div className="font-mono text-[10px] uppercase tracking-[0.24em] text-vermilion">03 / Metadatos</div><h2 className="mt-2 font-serif text-2xl">Geometría de la respuesta</h2></div><Sparkles size={18} className="text-pollen" /></div><div className="mt-5 grid gap-0 border-y border-ink/10 sm:grid-cols-3"><div className="border-b border-ink/10 py-5 sm:border-b-0 sm:border-r sm:pr-5"><div className="font-mono text-[10px] uppercase tracking-[0.16em] text-ink/45">Proyecto</div><div className="mt-4 font-serif text-2xl">{projectInput.name}</div><div className="mt-2 text-xs text-ink/50">schema_version · {projectInput.schema_version}</div></div><div className="border-b border-ink/10 py-5 sm:border-b-0 sm:border-r sm:px-5"><div className="font-mono text-[10px] uppercase tracking-[0.16em] text-ink/45">Engine</div><div className="mt-4 font-serif text-2xl">{results.length ? "forgemind-python" : "—"}</div><div className="mt-2 text-xs text-ink/50">respuesta tipada / JSON</div></div><div className="py-5 sm:pl-5"><div className="font-mono text-[10px] uppercase tracking-[0.16em] text-ink/45">Interpretación</div><div className="mt-4 font-serif text-2xl text-green">experimental</div><div className="mt-2 text-xs text-ink/50">Confidence ≠ truth probability</div></div></div></section>
      </div><footer className="flex flex-wrap items-center justify-between gap-3 border-t border-ink/10 px-5 py-5 text-[10px] uppercase tracking-[0.18em] text-ink/35 sm:px-8 lg:px-12"><span>ForgeMind / public API client</span><span>ProjectInput 1.0</span><span>Evidence before certainty</span></footer></main></div>;
}
