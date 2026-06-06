"use client";
import { useState } from "react";
import { Search, Scale, ExternalLink, Loader2 } from "lucide-react";

interface Source {
  title: string;
  url: string;
  score: number;
}

interface Answer {
  answer: string;
  sources: Source[];
}

export default function Home() {
  const [question, setQuestion] = useState("");
  const [result, setResult]     = useState<Answer | null>(null);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState("");

  async function ask() {
    if (!question.trim()) return;
    setLoading(true);
    setResult(null);
    setError("");

    try {
  
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();
      setResult(data);
    } catch {
      setError("Could not connect to the API. Make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-gray-950 text-white">

      {/* Header */}
      <div className="border-b border-gray-800 px-6 py-4 flex items-center gap-3">
        <Scale className="text-amber-400" size={24} />
        <span className="text-xl font-semibold">NyayaBot</span>
        <span className="text-gray-500 text-sm ml-2">Indian Legal Research Assistant</span>
      </div>

      <div className="max-w-3xl mx-auto px-6 py-12">

        {/* Hero */}
        <div className="text-center mb-10">
          <h1 className="text-4xl font-bold mb-3">
            Ask any <span className="text-amber-400">legal question</span>
          </h1>
          <p className="text-gray-400">
            Answers grounded in real Indian court judgments
          </p>
        </div>

        {/* Search box */}
        <div className="flex gap-3 mb-8">
          <input
            type="text"
            value={question}
            onChange={e => setQuestion(e.target.value)}
            onKeyDown={e => e.key === "Enter" && ask()}
            placeholder="e.g. Can an employer terminate without notice?"
            className="flex-1 bg-gray-900 border border-gray-700 rounded-xl px-5 py-4 text-white placeholder-gray-500 focus:outline-none focus:border-amber-400 transition"
          />
          <button
            onClick={ask}
            disabled={loading}
            className="bg-amber-400 hover:bg-amber-300 text-gray-950 font-semibold px-6 py-4 rounded-xl transition disabled:opacity-50 flex items-center gap-2"
          >
            {loading
              ? <Loader2 size={18} className="animate-spin" />
              : <Search size={18} />}
            Ask
          </button>
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-950 border border-red-800 text-red-300 rounded-xl px-5 py-4 mb-6">
            {error}
          </div>
        )}

        {/* Loading state */}
        {loading && (
          <div className="text-center text-gray-400 py-12">
            <Loader2 size={32} className="animate-spin mx-auto mb-3 text-amber-400" />
            Searching judgments and generating answer...
          </div>
        )}

        {/* Result */}
        {result && !loading && (
          <div className="space-y-6">

            {/* Answer card */}
            <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6">
              <div className="flex items-center gap-2 text-amber-400 font-semibold mb-3">
                <Scale size={16} />
                Legal Answer
              </div>
              <p className="text-gray-100 leading-relaxed">{result.answer}</p>
            </div>

            {/* Sources */}
            <div>
              <h2 className="text-gray-400 text-sm font-medium mb-3 uppercase tracking-wider">
                Sources — {result.sources.length} cases retrieved
              </h2>
              <div className="space-y-3">
                {result.sources.map((s, i) => (
                  <a
                    key={i}
                    href={s.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-start justify-between gap-4 bg-gray-900 border border-gray-800 hover:border-amber-400 rounded-xl px-5 py-4 transition group"
                  >
                    <div>
                      <p className="text-white font-medium group-hover:text-amber-400 transition text-sm">
                        {s.title}
                      </p>
                      <p className="text-gray-500 text-xs mt-1">{s.url}</p>
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      <span className="text-xs text-gray-500">
                        score: {s.score}
                      </span>
                      <ExternalLink size={14} className="text-gray-600 group-hover:text-amber-400 transition" />
                    </div>
                  </a>
                ))}
              </div>
            </div>

          </div>
        )}

        {/* Empty state */}
        {!result && !loading && !error && (
          <div className="text-center text-gray-600 py-16">
            <Scale size={48} className="mx-auto mb-4 opacity-30" />
            <p>Ask a question to search through Indian court judgments</p>
          </div>
        )}

      </div>
    </main>
  );
}