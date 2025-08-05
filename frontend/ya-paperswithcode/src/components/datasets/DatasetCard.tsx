import { Download, FileText, Image } from 'lucide-react';
import { Card, CardContent } from '../ui/card';
import { Badge } from '../ui/badge';
import { cn } from '../../lib/utils';

interface DatasetCardProps {
  dataset: {
    id: string;
    name: string;
    description: string;
    modality: string;
    task: string;
    downloads: number;
    papers: number;
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

  return (
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
                  {getModalityIcon(dataset.modality) || <Image className="h-8 w-8" />}
                </div>
              </div>
            )}
          </div>

          {/* Dataset info */}
          <div className="space-y-2">
            <h3 className="font-semibold line-clamp-1">{dataset.name}</h3>
            <p className="text-sm text-muted-foreground line-clamp-2">
              {dataset.description}
            </p>
            
            {/* Tags */}
            <div className="flex flex-wrap gap-2">
              <Badge variant="outline" className="text-xs">
                {dataset.modality}
              </Badge>
              <Badge variant="outline" className="text-xs">
                {dataset.task}
              </Badge>
            </div>

            {/* Stats */}
            <div className="flex items-center justify-between text-sm text-muted-foreground pt-2">
              <div className="flex items-center gap-1">
                <FileText className="h-3 w-3" />
                <span>{formatNumber(dataset.papers)} papers</span>
              </div>
              <div className="flex items-center gap-1">
                <Download className="h-3 w-3" />
                <span>{formatNumber(dataset.downloads)}</span>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}