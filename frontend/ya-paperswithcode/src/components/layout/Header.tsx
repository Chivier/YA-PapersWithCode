import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Search } from 'lucide-react';
import { useState } from 'react';
import { cn } from '../../lib/utils';

export function Header() {
  const [searchQuery, setSearchQuery] = useState('');
  const location = useLocation();
  const navigate = useNavigate();

  // Determine placeholder text based on current page
  const getPlaceholder = () => {
    if (location.pathname === '/') {
      return 'Search papers...';
    } else if (location.pathname === '/datasets') {
      return 'Search datasets...';
    } else if (location.pathname === '/methods') {
      return 'Search methods...';
    } else if (location.pathname === '/sota') {
      return 'Search benchmarks...';
    }
    return 'Search...';
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!searchQuery.trim()) return;
    
    // Navigate to the appropriate page with search query as URL parameter
    const searchParams = new URLSearchParams({ q: searchQuery.trim() });
    
    if (location.pathname === '/datasets') {
      // Stay on datasets page with search query
      navigate(`/datasets?${searchParams.toString()}`);
    } else if (location.pathname === '/methods') {
      // For methods page, navigate with search query
      navigate(`/methods?${searchParams.toString()}`);
    } else if (location.pathname === '/sota') {
      // For state-of-the-art page, navigate with search query
      navigate(`/sota?${searchParams.toString()}`);
    } else {
      // Default to home/papers page
      navigate(`/?${searchParams.toString()}`);
    }
    
    // Clear the search input after navigation
    setSearchQuery('');
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60">
      <div className="container flex h-16 items-center">
        <div className="mr-4 flex">
          <Link to="/" className="mr-6 flex items-center space-x-2">
            <span className="text-xl font-bold text-primary">Papers With Code</span>
          </Link>
        </div>
        
        <nav className="flex flex-1 items-center justify-between space-x-2 md:justify-start">
          <div className="flex items-center space-x-6 text-sm">
            <Link
              to="/"
              className={cn(
                "transition-colors hover:text-primary",
                "text-foreground/60"
              )}
            >
              Papers
            </Link>
            <Link
              to="/sota"
              className={cn(
                "transition-colors hover:text-primary",
                "text-foreground/60"
              )}
            >
              Browse State-of-the-Art
            </Link>
            <Link
              to="/datasets"
              className={cn(
                "transition-colors hover:text-primary",
                "text-foreground/60"
              )}
            >
              Datasets
            </Link>
            <Link
              to="/methods"
              className={cn(
                "transition-colors hover:text-primary",
                "text-foreground/60"
              )}
            >
              Methods
            </Link>
          </div>
          
          <div className="flex flex-1 items-center justify-end space-x-4">
            <form onSubmit={handleSearch} className="relative w-[300px]">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none z-10" />
              <input
                type="text"
                id="header-search-input"
                name="header-search-query"
                placeholder={getPlaceholder()}
                className="h-9 w-full rounded-md border border-input bg-white pl-10 pr-4 text-sm transition-colors placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </form>
          </div>
        </nav>
      </div>
    </header>
  );
}
