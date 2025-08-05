import { useState, useEffect } from 'react';
import { PaperCard } from '../components/papers/PaperCard';
import type { Paper } from '../types';
import samplePapers from '../data/sample-papers.json';

export function Home() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate loading papers
    setTimeout(() => {
      setPapers(samplePapers.papers as Paper[]);
      setLoading(false);
    }, 500);
  }, []);

  const trendingPapers = papers.filter(p => p.trending);
  const latestPapers = papers.filter(p => !p.trending);

  return (
    <div className="container py-8">
      <div className="space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold">Papers With Code</h1>
          <p className="text-muted-foreground mt-2">
            The latest in machine learning papers with code implementations
          </p>
        </div>

        {loading ? (
          <div className="flex justify-center py-12">
            <div className="text-muted-foreground">Loading papers...</div>
          </div>
        ) : (
          <>
            {/* Trending Papers Section */}
            {trendingPapers.length > 0 && (
              <section>
                <h2 className="text-2xl font-semibold mb-4 flex items-center gap-2">
                  <span className="text-primary">Trending</span> Papers
                </h2>
                <div className="grid gap-4 md:grid-cols-1 lg:grid-cols-2">
                  {trendingPapers.map((paper) => (
                    <PaperCard key={paper.id} paper={paper} />
                  ))}
                </div>
              </section>
            )}

            {/* Latest Papers Section */}
            <section>
              <h2 className="text-2xl font-semibold mb-4">Latest Papers</h2>
              <div className="grid gap-4 md:grid-cols-1 lg:grid-cols-2">
                {latestPapers.map((paper) => (
                  <PaperCard key={paper.id} paper={paper} />
                ))}
              </div>
            </section>

            {/* Load More Button */}
            <div className="flex justify-center pt-8">
              <button className="px-6 py-2 border border-primary text-primary rounded-md hover:bg-primary hover:text-primary-foreground transition-colors">
                Load More Papers
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}