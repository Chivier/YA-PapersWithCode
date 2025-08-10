import { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import type { FilterOption } from '../../types';

interface FilterSidebarProps {
  filters: {
    modalities: FilterOption[];
    languages: FilterOption[];
  };
  selectedFilters: {
    modalities: string[];
    languages: string[];
  };
  hideWithoutLink?: boolean;
  onFilterChange: (filterType: 'modalities' | 'languages', value: string) => void;
  onToggleHideWithoutLink?: (value: boolean) => void;
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
              className="flex items-center gap-2 text-sm cursor-pointer hover:text-primary"
            >
              <input
                type="checkbox"
                className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                checked={selectedValues.includes(option.param)}
                onChange={() => onToggle(option.param)}
              />
              <span>{option.name}</span>
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

export function FilterSidebar({ 
  filters, 
  selectedFilters, 
  hideWithoutLink = false, 
  onFilterChange,
  onToggleHideWithoutLink 
}: FilterSidebarProps) {
  const hasActiveFilters = 
    selectedFilters.modalities.length > 0 ||
    selectedFilters.languages.length > 0 ||
    hideWithoutLink;

  const clearAllFilters = () => {
    selectedFilters.modalities.forEach(m => onFilterChange('modalities', m));
    selectedFilters.languages.forEach(l => onFilterChange('languages', l));
    if (hideWithoutLink && onToggleHideWithoutLink) {
      onToggleHideWithoutLink(false);
    }
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
          title="Filter by Language"
          options={filters.languages}
          selectedValues={selectedFilters.languages}
          onToggle={(value) => onFilterChange('languages', value)}
        />
        
        {/* Additional Options */}
        <div className="border-b pb-4">
          <h4 className="text-sm font-medium mb-3">Additional Options</h4>
          <label className="flex items-center gap-2 text-sm cursor-pointer hover:text-primary">
            <input
              type="checkbox"
              className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
              checked={hideWithoutLink}
              onChange={(e) => onToggleHideWithoutLink?.(e.target.checked)}
            />
            <span className="flex items-center gap-1">
              Hide datasets without official link
            </span>
          </label>
        </div>
      </div>
    </div>
  );
}
