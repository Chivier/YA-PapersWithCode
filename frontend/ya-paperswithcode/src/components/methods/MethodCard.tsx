import { ChevronRight } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import type { MethodCategory } from '../../types';
import { cn } from '../../lib/utils';

interface MethodCardProps {
  category: MethodCategory;
  className?: string;
}

export function MethodCard({ category, className }: MethodCardProps) {
  return (
    <Card className={cn('hover:shadow-lg transition-shadow', className)}>
      <CardHeader>
        <CardTitle className="text-xl">{category.name}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground mb-4">
          {category.description}
        </p>
        
        <div className="space-y-2">
          {category.subcategories.slice(0, 5).map((subcategory) => (
            <a
              key={subcategory.slug}
              href={`/methods/${category.id}/${subcategory.slug}`}
              className="flex items-center justify-between p-2 rounded-md hover:bg-muted transition-colors group"
            >
              <span className="text-sm font-medium">{subcategory.name}</span>
              <ChevronRight className="h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors" />
            </a>
          ))}
          
          {category.subcategories.length > 5 && (
            <a
              href={`/methods/${category.id}`}
              className="block text-center text-sm text-primary hover:underline pt-2"
            >
              View all {category.subcategories.length} subcategories
            </a>
          )}
        </div>
      </CardContent>
    </Card>
  );
}