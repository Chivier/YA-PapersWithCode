import { AlertCircle, Search } from 'lucide-react';
import { Button } from '../ui/button';


interface NotFoundProps {
  paperTitle?: string;
  message?: string;
}

export function NotFound({ paperTitle, message = "The page you're looking for doesn't exist." }: NotFoundProps) {
  
  const handleGoogleSearch = () => {
    if (paperTitle) {
      const searchQuery = encodeURIComponent(paperTitle);
      window.open(`https://www.google.com/search?q=${searchQuery}`, '_blank');
    }
  };

  return (
    <div className="min-h-[60vh] flex items-center justify-center px-4">
      <div className="text-center max-w-lg">
        <div className="flex justify-center mb-6">
          <div className="rounded-full bg-destructive/10 p-6">
            <AlertCircle className="h-12 w-12 text-destructive" />
          </div>
        </div>
        
        <h1 className="text-4xl font-bold mb-2">404</h1>
        <h2 className="text-xl font-semibold mb-4">Page Not Found</h2>
        <p className="text-muted-foreground mb-2">
          {message}
        </p>
        
        {paperTitle && (
          <>
            <p className="text-sm text-muted-foreground mb-8">
              Looking for: <span className="font-medium text-foreground">"{paperTitle}"</span>
            </p>
            
            <Button
              onClick={handleGoogleSearch}
              size="lg"
              className="flex items-center justify-center gap-2 mx-auto"
            >
              <Search className="h-4 w-4" />
              Search on Google
            </Button>
            
            <div className="mt-8 p-4 bg-muted/30 rounded-lg max-w-sm mx-auto">
              <p className="text-xs text-muted-foreground">
                <strong>Tip:</strong> The paper link might be outdated or incorrect. 
                Clicking the button above will search for this paper on Google in a new tab.
              </p>
            </div>
          </>
        )}
        
        {!paperTitle && (
          <p className="text-sm text-muted-foreground mt-4">
            You can close this tab to go back.
          </p>
        )}
      </div>
    </div>
  );
}