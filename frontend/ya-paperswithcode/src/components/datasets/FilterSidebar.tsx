import { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import type { FilterOption } from '../../types';

interface FilterSidebarProps {
  filters: {
    modalities: FilterOption[];
    tasks: FilterOption[];
    languages: FilterOption[];
  };
  selectedFilters: {
    modalities: string[];
    tasks: string[];
    languages: string[];
  };
  onFilterChange: (filterType: 'modalities' | 'tasks' | 'languages', value: string) => void;
}

interface FilterSectionProps {
  title: string;
  options: FilterOption[];
  selectedValues: string[];
  onToggle: (value: string) => void;
  defaultExpanded?: boolean;
  showCount?: number;
}

function FilterSection({ 
  title, 
  options, 
  selectedValues, 
  onToggle, 
  defaultExpanded = true,
  showCount = 10 
}: FilterSectionProps) {
  const [expanded, setExpanded] = useState(defaultExpanded);
  const [showAll, setShowAll] = useState(false);

  const displayOptions = showAll ? options : options.slice(0, showCount);
  const hasMore = options.length > showCount;

  return (
    <div className="border-b pb-4">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex w-full items-center justify-between py-2 text-sm font-medium hover:text-primary"
      >
        {title}
        {expanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
      </button>
      
      {expanded && (
        <div className="mt-2 space-y-2">
          {displayOptions.map((option) => (
            <label
              key={option.param}
              className="flex items-center justify-between text-sm cursor-pointer hover:text-primary"
            >
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                  checked={selectedValues.includes(option.param)}
                  onChange={() => onToggle(option.param)}
                />
                <span>{option.name}</span>
              </div>
              <span className="text-muted-foreground">({option.count})</span>
            </label>
          ))}
          
          {hasMore && (
            <button
              onClick={() => setShowAll(!showAll)}
              className="text-sm text-primary hover:underline mt-2"
            >
              {showAll ? 'Show less' : `Show all ${options.length}`}
            </button>
          )}
        </div>
      )}
    </div>
  );
}

export function FilterSidebar({ filters, selectedFilters, onFilterChange }: FilterSidebarProps) {
  const hasActiveFilters = 
    selectedFilters.modalities.length > 0 ||
    selectedFilters.tasks.length > 0 ||
    selectedFilters.languages.length > 0;

  const clearAllFilters = () => {
    selectedFilters.modalities.forEach(m => onFilterChange('modalities', m));
    selectedFilters.tasks.forEach(t => onFilterChange('tasks', t));
    selectedFilters.languages.forEach(l => onFilterChange('languages', l));
  };

  return (
    <div className="w-full space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Filters</h3>
        {hasActiveFilters && (
          <button
            onClick={clearAllFilters}
            className="text-sm text-primary hover:underline"
          >
            Clear all
          </button>
        )}
      </div>
      
      <div className="space-y-4">
        <FilterSection
          title="Filter by Modality"
          options={filters.modalities}
          selectedValues={selectedFilters.modalities}
          onToggle={(value) => onFilterChange('modalities', value)}
        />
        
        <FilterSection
          title="Filter by Task"
          options={filters.tasks}
          selectedValues={selectedFilters.tasks}
          onToggle={(value) => onFilterChange('tasks', value)}
          showCount={15}
        />
        
        <FilterSection
          title="Filter by Language"
          options={filters.languages}
          selectedValues={selectedFilters.languages}
          onToggle={(value) => onFilterChange('languages', value)}
        />
      </div>
    </div>
  );
}