import { Link } from 'react-router-dom';
import { FileText, Image, ExternalLink } from 'lucide-react';
import { Card, CardContent } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { cn } from '../../lib/utils';

interface DatasetCardProps {
  dataset: {
    id: string;
    name: string;
    full_name?: string;
    description: string;
    homepage?: string;
    paper_title?: string;
    paper_url?: string;
    subtasks?: string[];
    modalities?: string[];
    languages?: string[];
    modality?: string;
    task?: string;
    downloads?: number;
    papers?: number;
    thumbnail?: string;
  };
  className?: string;
}

export function DatasetCard({ dataset, className }: DatasetCardProps) {
  const formatNumber = (num: number) => {
    if (num >= 1000000) {
      return `${(num / 1000000).toFixed(1)}M`;
    }
    if (num >= 1000) {
      return `${(num / 1000).toFixed(1)}K`;
    }
    return num.toString();
  };

  const getModalityIcon = (modality: string) => {
    if (!modality) return null;
    switch (modality.toLowerCase()) {
      case 'images':
      case 'image':
        return <Image className="h-4 w-4" />;
      case 'texts':
      case 'text':
        return <FileText className="h-4 w-4" />;
      default:
        return null;
    }
  };

  // Use the dataset ID directly for the URL, with safety check
  const datasetUrl = dataset.id ? `/datasets/${dataset.id}` : '#';

  // Don't render if no ID
  if (!dataset.id) {
    console.warn('Dataset without ID:', dataset);
    return null;
  }

  return (
    <Link to={datasetUrl} className="block">
      <Card className={cn('hover:shadow-lg transition-shadow cursor-pointer', className)}>
        <CardContent className="p-4">
        <div className="space-y-3">
          {/* Thumbnail or placeholder */}
          <div className="aspect-video bg-muted rounded-md overflow-hidden">
            {dataset.thumbnail ? (
              <img 
                src={dataset.thumbnail} 
                alt={dataset.name}
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center">
                <div className="text-muted-foreground">
                  {dataset.modality && getModalityIcon(dataset.modality) || <Image className="h-8 w-8" />}
                </div>
              </div>
            )}
          </div>

          {/* Dataset info */}
          <div className="space-y-2">
            <h3 className="font-semibold line-clamp-2" title={dataset.full_name || dataset.name}>
              {dataset.name}
            </h3>
            <p className="text-sm text-muted-foreground line-clamp-2">
              {dataset.description || 'No description available'}
            </p>
            
            {/* Tags */}
            <div className="flex flex-wrap gap-2">
              {/* Show modalities */}
              {dataset.modalities && Array.isArray(dataset.modalities) && dataset.modalities.length > 0 ? (
                dataset.modalities.slice(0, 2).map((mod, idx) => (
                  <Badge key={`mod-${idx}`} variant="outline" className="text-xs">
                    {mod}
                  </Badge>
                ))
              ) : dataset.modality ? (
                <Badge variant="outline" className="text-xs">
                  {dataset.modality}
                </Badge>
              ) : null}
              
              {/* Show subtasks */}
              {dataset.subtasks && Array.isArray(dataset.subtasks) && dataset.subtasks.length > 0 ? (
                dataset.subtasks.slice(0, 1).map((task, idx) => (
                  <Badge key={`task-${idx}`} variant="outline" className="text-xs">
                    {task}
                  </Badge>
                ))
              ) : dataset.task ? (
                <Badge variant="outline" className="text-xs">
                  {dataset.task}
                </Badge>
              ) : null}
            </div>

            {/* Stats and Visit Button */}
            <div className="flex items-center justify-between text-sm text-muted-foreground pt-2">
              {dataset.papers && dataset.papers > 0 ? (
                <div className="flex items-center gap-1">
                  <FileText className="h-3 w-3" />
                  <span>{formatNumber(dataset.papers)} papers</span>
                </div>
              ) : (
                <div />
              )}
              {dataset.homepage && (
                <Button
                  variant="outline"
                  size="sm"
                  className="h-7 px-2 text-xs"
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    window.open(dataset.homepage, '_blank', 'noopener,noreferrer');
                  }}
                >
                  <ExternalLink className="h-3 w-3 mr-1" />
                  Visit Dataset
                </Button>
              )}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
    </Link>
  );
}
