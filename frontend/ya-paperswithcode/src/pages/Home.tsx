import { useState, useEffect, useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';
import { PaperCard } from '../components/papers/PaperCard';
import { Button } from '../components/ui/button';
// import { AgentSearch } from '../components/search/AgentSearch';  // Temporarily disabled
import { NormalSearch } from '../components/search/NormalSearch';
import type { Paper } from '../types';
import { getPapers, searchPapers/*, searchPapersWithAgent*/ } from '../lib/api';  // AI search temporarily disabled

export function Home() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [papers, setPapers] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [sortOrder, setSortOrder] = useState('date');
  // const [agentSearchLoading, setAgentSearchLoading] = useState(false);  // Temporarily disabled
  const [normalSearchLoading, setNormalSearchLoading] = useState(false);
  const [isSearchMode, setIsSearchMode] = useState(false);

  const fetchPapers = async (pageNum: number) => {
    setLoading(true);
    try {
      const data = await getPapers(pageNum, 10);
      setPapers(data.results);
      setTotalPages(Math.ceil(data.total / 10));
    } catch (error) {
      console.error('Failed to fetch papers:', error);
    } finally {
      setLoading(false);
    }
  };

  // Handle search query from URL
  useEffect(() => {
    const query = searchParams.get('q');
    if (query) {
      // Automatically trigger normal search if query parameter exists
      handleNormalSearch(query);
    } else {
      // No search query, fetch regular papers
      setIsSearchMode(false);
      fetchPapers(page);
    }
  }, [searchParams]);

  // Fetch papers when page changes (only when not in search mode)
  useEffect(() => {
    if (!isSearchMode && !searchParams.get('q')) {
      fetchPapers(page);
    }
  }, [page, isSearchMode]);

  // Temporarily disabled AI-Powered Search handler
  /*
  const handleAgentSearch = async (query: string) => {
    setAgentSearchLoading(true);
    try {
      const data = await searchPapersWithAgent(query);
      setPapers(data.results);
      setTotalPages(1); // Reset pagination for search results
      setPage(1);
    } catch (error) {
      console.error('Agent search failed:', error);
    } finally {
      setAgentSearchLoading(false);
    }
  };
  */

  const handleNormalSearch = async (query: string) => {
    setNormalSearchLoading(true);
    setIsSearchMode(true);
    try {
      const data = await searchPapers(query, 1, 10);
      setPapers(data.results);
      setTotalPages(1); // Reset pagination for search results
      setPage(1);
      
      // Update URL with search query
      if (!searchParams.get('q') || searchParams.get('q') !== query) {
        setSearchParams({ q: query });
      }
    } catch (error) {
      console.error('Normal search failed:', error);
    } finally {
      setNormalSearchLoading(false);
    }
  };

  const clearSearch = () => {
    setSearchParams({});
    setIsSearchMode(false);
    setPage(1);
    fetchPapers(1);
  };

  const sortedPapers = useMemo(() => {
    return [...papers].sort((a, b) => {
      if (sortOrder === 'date') {
        return new Date(b.date).getTime() - new Date(a.date).getTime();
      } else {
        return a.title.localeCompare(b.title);
      }
    });
  }, [papers, sortOrder]);

  const trendingPapers = papers.filter(p => p.trending);

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

        {/* Show search query info if searching */}
        {searchParams.get('q') && (
          <div className="flex items-center justify-between p-4 bg-muted rounded-lg">
            <p className="text-sm">
              Showing search results for: <strong>{searchParams.get('q')}</strong>
            </p>
            <Button variant="outline" size="sm" onClick={clearSearch}>
              Clear Search
            </Button>
          </div>
        )}
        
        <NormalSearch onSearch={handleNormalSearch} loading={normalSearchLoading} />
        {/* Temporarily disabled AI-Powered Search */}
        {/* <AgentSearch onSearch={handleAgentSearch} loading={agentSearchLoading} /> */}

        {loading ? (
          <div className="flex justify-center py-12">
            <div className="text-muted-foreground">Loading papers...</div>
          </div>
        ) : (
          <>
            {/* Trending Papers Section */}
            {page === 1 && trendingPapers.length > 0 && (
              <section>
                <h2 className="text-2xl font-semibold mb-4 flex items-center gap-2">
                  <span className="text-primary">Trending</span> Papers
                </h2>
                <div className="grid gap-4 md:grid-cols-1 lg:grid-cols-2">
                  {trendingPapers.map((paper, index) => (
                    <PaperCard key={paper.id || `trending-${index}`} paper={paper} />
                  ))}
                </div>
              </section>
            )}

            {/* Latest Papers Section */}
            <section>
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-2xl font-semibold">Latest Papers</h2>
                <div className="flex gap-2">
                  <Button variant={sortOrder === 'date' ? 'primary' : 'outline'} onClick={() => setSortOrder('date')}>Sort by Date</Button>
                  <Button variant={sortOrder === 'title' ? 'primary' : 'outline'} onClick={() => setSortOrder('title')}>Sort by Title</Button>
                </div>
              </div>
              <div className="grid gap-4 md:grid-cols-1 lg:grid-cols-2">
                {sortedPapers.map((paper, index) => (
                  <PaperCard key={paper.id || `paper-${index}`} paper={paper} />
                ))}
              </div>
            </section>

            {/* Pagination */}
            <div className="flex justify-center items-center gap-4 pt-8">
              <Button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}>Previous</Button>
              <span>Page {page} of {totalPages}</span>
              <Button onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages}>Next</Button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
