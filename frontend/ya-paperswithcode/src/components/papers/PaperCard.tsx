import { Github, Star, TrendingUp, Calendar } from 'lucide-react';
import { Card, CardContent } from '../ui/card';
import { Badge } from '../ui/badge';
import type { Paper } from '../../types';
import { cn } from '../../lib/utils';

interface PaperCardProps {
  paper: Paper;
  className?: string;
}

export function PaperCard({ paper, className }: PaperCardProps) {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    });
  };

  const formatAuthors = (authors: string[]) => {
    if (authors.length <= 3) {
      return authors.join(', ');
    }
    return `${authors.slice(0, 3).join(', ')}, et al.`;
  };

  const handlePaperClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
    if (!paper.arxiv_id) {
      e.preventDefault();
      const currentOrigin = window.location.origin;
      window.open(`${currentOrigin}/404?title=${encodeURIComponent(paper.title)}`, '_blank');
    }
  };

  return (
    <Card className={cn('hover:shadow-lg transition-shadow', className)}>
      <CardContent className="p-6">
        <div className="space-y-4">
          {/* Title and trending badge */}
          <div className="flex items-start justify-between gap-4">
            <h3 className="text-lg font-semibold line-clamp-2">
              <a 
                href={paper.arxiv_id ? `https://arxiv.org/abs/${paper.arxiv_id}` : '#'}
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-primary transition-colors"
                onClick={handlePaperClick}
              >
                {paper.title}
              </a>
            </h3>
            {paper.trending && (
              <Badge variant="primary" className="flex items-center gap-1 shrink-0">
                <TrendingUp className="h-3 w-3" />
                Trending
              </Badge>
            )}
          </div>

          {/* Authors */}
          <p className="text-sm text-muted-foreground">
            {formatAuthors(paper.authors)}
          </p>

          {/* Abstract */}
          <p className="text-sm text-foreground/80 line-clamp-3">
            {paper.abstract}
          </p>

          {/* Tags */}
          <div className="flex flex-wrap gap-2">
            {paper.tags && paper.tags.map((tag) => (
              <Badge key={tag} variant="outline" className="text-xs">
                {tag}
              </Badge>
            ))}
          </div>

          {/* Footer with date and code links */}
          <div className="flex items-center justify-between pt-2">
            <div className="flex items-center gap-1 text-sm text-muted-foreground">
              <Calendar className="h-4 w-4" />
              {formatDate(paper.date)}
            </div>
            
            <div className="flex items-center gap-3">
              {paper.codeLinks && paper.codeLinks.map((link, index) => (
                <a
                  key={index}
                  href={link.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1 text-sm text-muted-foreground hover:text-primary transition-colors"
                >
                  <Github className="h-4 w-4" />
                  {link.stars && (
                    <>
                      <Star className="h-3 w-3 fill-current" />
                      <span>{link.stars.toLocaleString()}</span>
                    </>
                  )}
                </a>
              ))}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}