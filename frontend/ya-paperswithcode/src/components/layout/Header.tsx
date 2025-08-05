import { Link } from 'react-router-dom';
import { Search } from 'lucide-react';
import { useState } from 'react';
import { cn } from '../../lib/utils';

export function Header() {
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Implement search functionality
    console.log('Search:', searchQuery);
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
            <form onSubmit={handleSearch} className="flex items-center">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" />
                <input
                  type="search"
                  placeholder="Search papers, datasets, methods..."
                  className="h-9 w-[300px] rounded-md border border-input bg-background pl-10 pr-3 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
            </form>
            
            <Link
              to="/login"
              className="text-sm text-foreground/60 transition-colors hover:text-primary"
            >
              Sign In
            </Link>
          </div>
        </nav>
      </div>
    </header>
  );
}