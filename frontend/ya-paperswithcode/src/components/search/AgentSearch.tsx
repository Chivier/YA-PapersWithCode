import { useState } from 'react';
import { Search } from 'lucide-react';
import { Button } from '../ui/button';
import { useLocation } from 'react-router-dom';

interface AgentSearchProps {
  onSearch: (query: string) => void;
  loading: boolean;
}

export function AgentSearch({ onSearch, loading }: AgentSearchProps) {
  const [query, setQuery] = useState('');
  const location = useLocation();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch(query);
  };

  return (
    <div className="mt-8 p-6 bg-muted rounded-lg">
      <h2 className="text-lg font-semibold mb-2">AI-Powered Search</h2>
      <p className="text-sm text-muted-foreground mb-4">
        {location.pathname === '/datasets' 
          ? 'Use our AI agent to find relevant datasets with natural language.'
          : 'Use our AI agent to find relevant papers with natural language.'}
      </p>
      <form onSubmit={handleSearch} className="flex gap-2">
        <div className="relative flex-grow">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none z-10" />
          <input
            type="text"
            id="agent-search-input"
            name="agent-search-query"
            placeholder={location.pathname === '/datasets'
              ? "e.g., 'image classification datasets with more than 10k samples'"
              : "e.g., 'papers on diffusion models for image generation'"}
            className="h-10 w-full rounded-md border border-input bg-white pl-10 pr-4 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            style={{ textIndent: '0px' }}
          />
        </div>
        <Button type="submit" disabled={loading || !query.trim()}>
          {loading ? 'Searching...' : 'Search'}
        </Button>
      </form>
    </div>
  );
}
