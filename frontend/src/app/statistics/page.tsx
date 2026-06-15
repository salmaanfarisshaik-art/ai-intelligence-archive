import { getDashboardMetrics } from "@/lib/api";

export default function StatisticsPage() {
  const data = getDashboardMetrics();
  const rawStats = data?.raw_stats || {};
  const metrics = data?.metrics || [];

  return (
    <main className="min-h-screen p-8 text-white max-w-5xl mx-auto pt-32">
      <div className="mb-16">
        <h1 className="text-5xl font-bold mb-4 glow-text">Archive Statistics</h1>
        <p className="text-gray-400 text-lg">Detailed breakdown of the AI ecosystem tracked in this archive.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16">
        {metrics.map((m: any, idx: number) => (
          <div key={idx} className="glass-panel p-6 rounded-2xl">
            <h3 className="text-sm uppercase tracking-wider text-gray-400 mb-2">{m.metric}</h3>
            <div className="text-4xl font-bold text-purple-300">
              {typeof m.current === "number" ? m.current.toLocaleString() : m.current}
            </div>
            {m.target && m.target !== "-" && (
              <div className="mt-4 flex items-center justify-between text-xs text-gray-500">
                <span>Progress to Target</span>
                <span>{Math.round((m.current / m.target) * 100)}%</span>
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="glass-panel p-8 rounded-3xl">
        <h2 className="text-2xl font-semibold mb-6 text-purple-300">Raw Categories</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
          {Object.entries(rawStats)
            .filter(([key]) => key !== "generated_at")
            .map(([key, value]) => (
            <div key={key} className="bg-white/5 p-4 rounded-xl border border-white/10 hover:border-white/20 transition-colors">
              <div className="text-xs text-gray-400 uppercase tracking-wider mb-1">{key.replace(/_/g, " ")}</div>
              <div className="text-2xl font-semibold">{Number(value).toLocaleString()}</div>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
