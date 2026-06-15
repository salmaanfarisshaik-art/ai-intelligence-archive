import { notFound } from "next/navigation";
import { getEntity, getAllDomains, getEntitiesByDomain } from "@/lib/api";

export async function generateStaticParams() {
  const domains = getAllDomains();
  const paths = [];

  for (const domain of domains) {
    const entities = getEntitiesByDomain(domain);
    for (const entity of entities.slice(0, 100)) {
      if (entity.unique_id) {
        paths.push({
          type: domain,
          id: entity.unique_id,
        });
      }
    }
  }

  return paths;
}

export default async function EntityPage(props: { params: Promise<{ type: string; id: string }> }) {
  const params = await props.params;
  const entity = getEntity(params.type, params.id);

  if (!entity) {
    notFound();
  }

  return (
    <main className="min-h-screen p-8 text-white max-w-5xl mx-auto pt-32">
      <div className="glass-panel p-8 rounded-3xl">
        <div className="flex items-center gap-4 mb-6">
          <span className="text-sm px-3 py-1 bg-purple-600/30 border border-purple-500/50 rounded-full uppercase tracking-wider">
            {params.type}
          </span>
          <span className="text-gray-400 text-sm">{entity.unique_id}</span>
        </div>
        
        <h1 className="text-4xl md:text-6xl font-bold mb-8">
          {entity.title || entity.name || entity.unique_id}
        </h1>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="md:col-span-2 space-y-8">
            {entity.description && (
              <section>
                <h2 className="text-2xl font-semibold mb-4 text-purple-300">Description</h2>
                <p className="text-gray-300 leading-relaxed whitespace-pre-wrap">
                  {entity.description}
                </p>
              </section>
            )}
            
            <section>
              <h2 className="text-2xl font-semibold mb-4 text-purple-300">Raw Data</h2>
              <pre className="bg-black/50 p-6 rounded-xl overflow-x-auto text-sm text-gray-300 font-mono">
                {JSON.stringify(entity, null, 2)}
              </pre>
            </section>
          </div>
          
          <div className="space-y-6">
            {entity.category && (
              <div className="glass-panel p-4 rounded-xl">
                <h3 className="text-sm text-gray-400 uppercase tracking-wider mb-2">Category</h3>
                <p className="font-semibold">{entity.category}</p>
              </div>
            )}
            
            {entity.tags && entity.tags.length > 0 && (
              <div className="glass-panel p-4 rounded-xl">
                <h3 className="text-sm text-gray-400 uppercase tracking-wider mb-3">Tags</h3>
                <div className="flex flex-wrap gap-2">
                  {entity.tags.map((tag: string, i: number) => (
                    <span key={i} className="px-2 py-1 bg-white/5 rounded text-sm text-gray-300">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}
            
            {entity.source_url && (
              <div className="glass-panel p-4 rounded-xl">
                <h3 className="text-sm text-gray-400 uppercase tracking-wider mb-2">Source URL</h3>
                <a href={entity.source_url} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300 underline break-all">
                  {entity.source_url}
                </a>
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
