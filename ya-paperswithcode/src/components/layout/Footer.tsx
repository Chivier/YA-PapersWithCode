import { Link } from 'react-router-dom';

export function Footer() {
  return (
    <footer className="mt-auto border-t bg-muted">
      <div className="container py-8">
        <div className="grid grid-cols-1 gap-8 md:grid-cols-4">
          <div className="space-y-3">
            <h3 className="text-lg font-semibold">Papers With Code</h3>
            <p className="text-sm text-muted-foreground">
              A free resource for researchers and practitioners to find and follow the latest ML papers and code.
            </p>
          </div>
          
          <div className="space-y-3">
            <h4 className="text-sm font-semibold">Browse</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <Link to="/" className="text-muted-foreground hover:text-primary">
                  Latest Papers
                </Link>
              </li>
              <li>
                <Link to="/sota" className="text-muted-foreground hover:text-primary">
                  State-of-the-Art
                </Link>
              </li>
              <li>
                <Link to="/datasets" className="text-muted-foreground hover:text-primary">
                  Datasets
                </Link>
              </li>
              <li>
                <Link to="/methods" className="text-muted-foreground hover:text-primary">
                  Methods
                </Link>
              </li>
            </ul>
          </div>
          
          <div className="space-y-3">
            <h4 className="text-sm font-semibold">Resources</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <Link to="/about" className="text-muted-foreground hover:text-primary">
                  About
                </Link>
              </li>
              <li>
                <a 
                  href="https://github.com/paperswithcode/paperswithcode-data" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-muted-foreground hover:text-primary"
                >
                  Data Download
                </a>
              </li>
              <li>
                <Link to="/api" className="text-muted-foreground hover:text-primary">
                  API
                </Link>
              </li>
            </ul>
          </div>
          
          <div className="space-y-3">
            <h4 className="text-sm font-semibold">Legal</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <Link to="/terms" className="text-muted-foreground hover:text-primary">
                  Terms of Service
                </Link>
              </li>
              <li>
                <Link to="/privacy" className="text-muted-foreground hover:text-primary">
                  Privacy Policy
                </Link>
              </li>
              <li>
                <a 
                  href="https://creativecommons.org/licenses/by-sa/4.0/" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-muted-foreground hover:text-primary"
                >
                  CC-BY-SA License
                </a>
              </li>
            </ul>
          </div>
        </div>
        
        <div className="mt-8 border-t pt-8 text-center text-sm text-muted-foreground">
          <p>© 2025 Papers With Code. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}