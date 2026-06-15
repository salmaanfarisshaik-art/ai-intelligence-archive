import { getArtifactManifest } from "@/lib/api";

export default function ArtifactsPage() {
  const manifest = getArtifactManifest();
  const artifacts = manifest?.artifacts || [];

  return (
    <main className="min-h-screen p-8 text-white max-w-6xl mx-auto pt-32">
      <div className="mb-16">
        <h1 className="text-5xl font-bold mb-4 glow-text">Generated Artifacts</h1>
        <p className="text-gray-400 text-lg">Static JSON files generated deterministically by Phase 9 pipeline.</p>
        <p className="text-sm text-gray-500 mt-2 font-mono">Last Generated: {manifest?.generated_at || "Unknown"}</p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-white/20 text-gray-400 text-sm tracking-wider uppercase">
              <th className="p-4 font-semibold">Artifact Path</th>
              <th className="p-4 font-semibold">Size (Bytes)</th>
              <th className="p-4 font-semibold">Schema Version</th>
              <th className="p-4 font-semibold">SHA-256 Checksum</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {artifacts.map((artifact: any, idx: number) => (
              <tr key={idx} className="hover:bg-white/5 transition-colors group">
                <td className="p-4 font-mono text-purple-300">
                  <a href={`/ai-intelligence-archive/site/${artifact.artifact_path}`} target="_blank" className="hover:underline">
                    {artifact.artifact_path}
                  </a>
                </td>
                <td className="p-4 text-gray-300">{(artifact.size_bytes / 1024).toFixed(1)} KB</td>
                <td className="p-4 text-gray-400 text-sm">{artifact.schema_version}</td>
                <td className="p-4 font-mono text-xs text-gray-500 truncate max-w-[200px] group-hover:text-gray-300 transition-colors" title={artifact.sha256}>
                  {artifact.sha256}
                </td>
              </tr>
            ))}
            {artifacts.length === 0 && (
              <tr>
                <td colSpan={4} className="p-8 text-center text-gray-500 italic">No artifacts found. Pipeline may not have completed.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </main>
  );
}
