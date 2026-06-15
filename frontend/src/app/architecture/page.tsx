export default function ArchitecturePage() {
  return (
    <main className="min-h-screen p-8 text-white max-w-5xl mx-auto pt-32">
      <div className="mb-16">
        <h1 className="text-5xl font-bold mb-4 glow-text">System Architecture</h1>
        <p className="text-gray-400 text-lg">The 5-phase deterministic pipeline of the AI Intelligence Archive.</p>
      </div>

      <div className="space-y-8">
        {[
          { phase: "Phase 8.5", name: "Mass Expansion Layer", desc: "Downloads 100,000+ seeds from Hugging Face and other APIs, converting them deterministically into JSON format." },
          { phase: "Phase 9", name: "Intelligence & Discovery Layer", desc: "Builds canonical knowledge graphs, extracts entities, generated chunks for semantic search, and compiles timelines." },
          { phase: "Phase 10", name: "Interactive Explorer", desc: "Fully static Next.js frontend serving visual insights from the raw generated Phase 9 site/ artifacts." }
        ].map((item, idx) => (
          <div key={idx} className="glass-panel p-8 rounded-3xl border-l-4 border-l-purple-500">
            <h2 className="text-2xl font-bold text-white mb-2">{item.phase}: {item.name}</h2>
            <p className="text-gray-400 leading-relaxed">{item.desc}</p>
          </div>
        ))}
      </div>
    </main>
  );
}
