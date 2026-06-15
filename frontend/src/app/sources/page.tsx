import { getSourceRegistry } from "@/lib/api";

export default function SourcesPage() {
  const sourcesData = getSourceRegistry() || {};
  const sources = Object.entries(sourcesData).map(([id, val]: [string, any]) => ({ id, ...val }));

  return (
    <main className="min-h-screen p-8 text-white max-w-6xl mx-auto pt-32">
      <div className="mb-16 flex justify-between items-end border-b border-white/10 pb-8">
        <div>
          <h1 className="text-5xl font-bold mb-4 glow-text">Source Registry</h1>
          <p className="text-gray-400 text-lg">Public data sources ingested into the intelligence archive.</p>
        </div>
        <div className="text-right">
          <div className="text-3xl font-bold text-purple-400">{sources.length}</div>
          <div className="text-sm text-gray-500 uppercase tracking-wider">Approved Sources</div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {sources.map((source: any, idx: number) => (
          <div key={idx} className="glass-panel p-6 rounded-2xl hover:bg-white/5 transition-colors border-l-4 border-l-purple-500">
            <h3 className="text-xl font-semibold mb-2">{source.id}</h3>
            {source.description && (
              <p className="text-gray-400 text-sm mb-4 line-clamp-2">{source.description}</p>
            )}
            <div className="flex justify-between items-center text-sm">
              <span className="px-3 py-1 bg-white/10 rounded-full text-gray-300">
                {source.type}
              </span>
              <a 
                href={source.url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-purple-400 hover:text-purple-300 underline"
              >
                View Source
              </a>
            </div>
          </div>
        ))}
      </div>
      
      {sources.length === 0 && (
        <div className="text-center py-20 text-gray-500">
          No sources registered yet.
        </div>
      )}
    </main>
  );
}
