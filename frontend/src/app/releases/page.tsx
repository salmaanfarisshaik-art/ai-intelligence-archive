import { getBuildManifest } from "@/lib/api";

export default function ReleasesPage() {
  const manifest = getBuildManifest();

  return (
    <main className="min-h-screen p-8 text-white max-w-5xl mx-auto pt-32">
      <div className="mb-16">
        <h1 className="text-5xl font-bold mb-4 glow-text">Build Releases</h1>
        <p className="text-gray-400 text-lg">Details of the deterministic build process.</p>
      </div>

      {manifest ? (
        <div className="glass-panel p-8 rounded-3xl">
          <h2 className="text-2xl font-bold mb-6 text-purple-300 border-b border-white/10 pb-4">
            Current Release Manifest
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
            <div>
              <h3 className="text-sm uppercase tracking-widest text-gray-400 mb-2">Build Pipeline Version</h3>
              <p className="text-xl font-mono text-gray-200 bg-white/5 p-3 rounded-xl inline-block">
                {manifest.pipeline_version}
              </p>
            </div>
            
            <div>
              <h3 className="text-sm uppercase tracking-widest text-gray-400 mb-2">Total Entities Processed</h3>
              <p className="text-xl font-bold text-gray-200 bg-white/5 p-3 rounded-xl inline-block">
                {Number(manifest.total_entities_processed).toLocaleString()}
              </p>
            </div>
          </div>
          
          <div className="space-y-6">
            <div>
              <h3 className="text-sm uppercase tracking-widest text-gray-400 mb-2">Build Timeline</h3>
              <div className="bg-white/5 p-4 rounded-xl font-mono text-sm space-y-2 text-gray-300">
                <div className="flex justify-between">
                  <span>Started At:</span>
                  <span>{manifest.build_started_at}</span>
                </div>
                <div className="flex justify-between">
                  <span>Completed At:</span>
                  <span>{manifest.build_completed_at}</span>
                </div>
              </div>
            </div>
            
            <div>
              <h3 className="text-sm uppercase tracking-widest text-gray-400 mb-2">Deterministic Hashes</h3>
              <div className="bg-black/30 p-4 rounded-xl font-mono text-xs space-y-3 break-all text-gray-400">
                <div>
                  <span className="text-purple-400 block mb-1">Source Manifest Hash</span>
                  {manifest.source_manifest_hash}
                </div>
                <div>
                  <span className="text-purple-400 block mb-1">Artifact Manifest Hash</span>
                  {manifest.artifact_manifest_hash}
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center py-20 text-gray-500 italic">
          Build manifest not found. This environment may not have completed a pipeline run.
        </div>
      )}
    </main>
  );
}
