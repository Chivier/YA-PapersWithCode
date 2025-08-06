import { useState, useEffect, useMemo } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { FilterSidebar } from '../components/datasets/FilterSidebar';
import { DatasetCard } from '../components/datasets/DatasetCard';
import { Button } from '../components/ui/button';
import { getDatasets } from '../lib/api';
import datasetFilters from '../data/dataset-filters.json';
import type { Dataset } from '../types';

export function Datasets() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalDatasets, setTotalDatasets] = useState(0);
  const [selectedFilters, setSelectedFilters] = useState({
    modalities: [] as string[],
    tasks: [] as string[],
    languages: [] as string[]
  });
  
  const datasetsPerPage = 48; // 12 columns x 4 rows

  useEffect(() => {
    const fetchDatasets = async () => {
      setLoading(true);
      try {
        const data = await getDatasets(currentPage, datasetsPerPage);
        // Ensure we have valid data
        if (data && data.results && Array.isArray(data.results)) {
          setDatasets(data.results);
          setTotalDatasets(data.total || 0);
        } else {
          console.warn('Invalid data format received from API:', data);
          setDatasets([]);
          setTotalDatasets(0);
        }
      } catch (error) {
        console.error('Failed to fetch datasets:', error);
        setDatasets([]);
        setTotalDatasets(0);
      } finally {
        setLoading(false);
      }
    };
    fetchDatasets();
  }, [currentPage]);

  const handleFilterChange = (filterType: 'modalities' | 'tasks' | 'languages', value: string) => {
    setSelectedFilters(prev => ({
      ...prev,
      [filterType]: prev[filterType].includes(value)
        ? prev[filterType].filter(v => v !== value)
        : [...prev[filterType], value]
    }));
  };

  const filteredDatasets = useMemo(() => {
    if (!datasets || !Array.isArray(datasets)) return [];
    
    return datasets.filter(dataset => {
      // Check modalities - match the filter param against the database values
      const modalityMatch = selectedFilters.modalities.length === 0 || 
        (dataset.modalities && Array.isArray(dataset.modalities) && dataset.modalities.some(dm => 
          selectedFilters.modalities.some(filterModality => {
            // Match "Texts" in DB with "texts" filter param
            // Match "Images" in DB with "images" filter param
            return dm.toLowerCase() === filterModality.toLowerCase() ||
                   dm.toLowerCase() === filterModality.charAt(0).toUpperCase() + filterModality.slice(1).toLowerCase();
          })
        ));
      
      // Check tasks (using subtasks field from backend)
      const taskMatch = selectedFilters.tasks.length === 0 || 
        (dataset.subtasks && Array.isArray(dataset.subtasks) && dataset.subtasks.some(dt => 
          selectedFilters.tasks.some(filterTask => {
            // Convert task name to param format for comparison
            const taskParam = dt.toLowerCase().replace(/\s+/g, '-');
            return taskParam === filterTask.toLowerCase();
          })
        ));
      
      // Check languages - match filter param against database values
      const languageMatch = selectedFilters.languages.length === 0 || 
        (dataset.languages && Array.isArray(dataset.languages) && dataset.languages.some(dl => 
          selectedFilters.languages.some(filterLang => {
            // Match "English" in DB with "english" filter param
            return dl.toLowerCase() === filterLang.toLowerCase();
          })
        ));
      
      return modalityMatch && taskMatch && languageMatch;
    });
  }, [datasets, selectedFilters]);

  const activeFilterCount = 
    selectedFilters.modalities.length + 
    selectedFilters.tasks.length + 
    selectedFilters.languages.length;

  const totalPages = Math.ceil(totalDatasets / datasetsPerPage);
  
  const handlePageChange = (page: number) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

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
                    Showing {datasets.length} of {totalDatasets.toLocaleString()} datasets
                    {activeFilterCount > 0 && ` (${activeFilterCount} filters active)`}
                    {totalPages > 1 && ` • Page ${currentPage} of ${totalPages}`}
                  </p>
                </div>

                {/* Dataset grid */}
                {filteredDatasets.length > 0 ? (
                  <>
                    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                      {filteredDatasets.map((dataset, index) => (
                        <DatasetCard key={`${dataset.id}-${index}`} dataset={dataset} />
                      ))}
                    </div>
                    
                    {/* Pagination */}
                    {totalPages > 1 && (
                      <div className="mt-8 flex items-center justify-center gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handlePageChange(currentPage - 1)}
                          disabled={currentPage === 1}
                        >
                          <ChevronLeft className="h-4 w-4" />
                          Previous
                        </Button>
                        
                        {/* Page numbers */}
                        <div className="flex items-center gap-1">
                          {/* First page */}
                          {currentPage > 3 && (
                            <>
                              <Button
                                variant={currentPage === 1 ? "default" : "outline"}
                                size="sm"
                                onClick={() => handlePageChange(1)}
                              >
                                1
                              </Button>
                              {currentPage > 4 && <span className="px-2 text-muted-foreground">...</span>}
                            </>
                          )}
                          
                          {/* Pages around current */}
                          {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                            const page = Math.max(1, Math.min(currentPage - 2 + i, totalPages - 4)) + Math.min(i, Math.max(0, 4 - (totalPages - currentPage)));
                            if (page > 0 && page <= totalPages && 
                                (page >= currentPage - 2 && page <= currentPage + 2)) {
                              return (
                                <Button
                                  key={page}
                                  variant={currentPage === page ? "default" : "outline"}
                                  size="sm"
                                  onClick={() => handlePageChange(page)}
                                >
                                  {page}
                                </Button>
                              );
                            }
                            return null;
                          }).filter(Boolean)}
                          
                          {/* Last page */}
                          {currentPage < totalPages - 2 && (
                            <>
                              {currentPage < totalPages - 3 && <span className="px-2 text-muted-foreground">...</span>}
                              <Button
                                variant={currentPage === totalPages ? "default" : "outline"}
                                size="sm"
                                onClick={() => handlePageChange(totalPages)}
                              >
                                {totalPages}
                              </Button>
                            </>
                          )}
                        </div>
                        
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handlePageChange(currentPage + 1)}
                          disabled={currentPage === totalPages}
                        >
                          Next
                          <ChevronRight className="h-4 w-4" />
                        </Button>
                      </div>
                    )}
                  </>
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