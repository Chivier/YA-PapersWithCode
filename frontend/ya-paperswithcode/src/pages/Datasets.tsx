import { useState, useEffect, useMemo } from 'react';
import { FilterSidebar } from '../components/datasets/FilterSidebar';
import { DatasetCard } from '../components/datasets/DatasetCard';
import datasetFilters from '../data/dataset-filters.json';
import sampleDatasets from '../data/sample-datasets.json';
import type { Dataset } from '../types';

export function Datasets() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedFilters, setSelectedFilters] = useState({
    modalities: [] as string[],
    tasks: [] as string[],
    languages: [] as string[]
  });

  useEffect(() => {
    // Simulate loading datasets
    setTimeout(() => {
      setDatasets(sampleDatasets.datasets as Dataset[]);
      setLoading(false);
    }, 500);
  }, []);

  const handleFilterChange = (filterType: 'modalities' | 'tasks' | 'languages', value: string) => {
    setSelectedFilters(prev => ({
      ...prev,
      [filterType]: prev[filterType].includes(value)
        ? prev[filterType].filter(v => v !== value)
        : [...prev[filterType], value]
    }));
  };

  // Filter datasets based on selected filters
  const filteredDatasets = useMemo(() => {
    return datasets.filter(dataset => {
      const modalityMatch = selectedFilters.modalities.length === 0 || 
        selectedFilters.modalities.some(m => 
          dataset.modality.toLowerCase() === m.toLowerCase()
        );
      
      const taskMatch = selectedFilters.tasks.length === 0 || 
        selectedFilters.tasks.some(t => 
          dataset.task.toLowerCase().replace(/\s+/g, '-') === t.toLowerCase()
        );
      
      // Note: Our sample datasets don't have language field, so we skip language filtering
      
      return modalityMatch && taskMatch;
    });
  }, [datasets, selectedFilters]);

  const activeFilterCount = 
    selectedFilters.modalities.length + 
    selectedFilters.tasks.length + 
    selectedFilters.languages.length;

  return (
    <div className="container py-8">
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold">Machine Learning Datasets</h1>
          <p className="text-muted-foreground mt-2">
            Browse datasets by modality, task, and language
          </p>
        </div>

        {/* Main content */}
        <div className="flex gap-8">
          {/* Sidebar */}
          <aside className="w-64 shrink-0">
            <div className="sticky top-20">
              <FilterSidebar
                filters={datasetFilters}
                selectedFilters={selectedFilters}
                onFilterChange={handleFilterChange}
              />
            </div>
          </aside>

          {/* Dataset grid */}
          <main className="flex-1">
            {loading ? (
              <div className="flex justify-center py-12">
                <div className="text-muted-foreground">Loading datasets...</div>
              </div>
            ) : (
              <>
                {/* Results header */}
                <div className="mb-4 flex items-center justify-between">
                  <p className="text-sm text-muted-foreground">
                    Showing {filteredDatasets.length} of {datasets.length} datasets
                    {activeFilterCount > 0 && ` (${activeFilterCount} filters active)`}
                  </p>
                </div>

                {/* Dataset grid */}
                {filteredDatasets.length > 0 ? (
                  <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                    {filteredDatasets.map(dataset => (
                      <DatasetCard key={dataset.id} dataset={dataset} />
                    ))}
                  </div>
                ) : (
                  <div className="py-12 text-center">
                    <p className="text-muted-foreground">
                      No datasets found matching your filters.
                    </p>
                  </div>
                )}
              </>
            )}
          </main>
        </div>
      </div>
    </div>
  );
}