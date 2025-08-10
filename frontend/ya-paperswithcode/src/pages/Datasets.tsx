import { useState, useEffect, useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { FilterSidebar } from '../components/datasets/FilterSidebar';
import { DatasetCard } from '../components/datasets/DatasetCard';
import { Button } from '../components/ui/button';
import { AgentSearch } from '../components/search/AgentSearch';
import { NormalSearch } from '../components/search/NormalSearch';
import { getDatasets, searchDatasets, searchDatasetsWithAgent } from '../lib/api';
import datasetFilters from '../data/dataset-filters.json';
import type { Dataset } from '../types';

export function Datasets() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [loading, setLoading] = useState(true);
  const [totalDatasets, setTotalDatasets] = useState(0);
  const [agentSearchLoading, setAgentSearchLoading] = useState(false);
  const [normalSearchLoading, setNormalSearchLoading] = useState(false);
  
  const datasetsPerPage = 48; // 12 columns x 4 rows
  
  // Get filters and page from URL
  const currentPage = parseInt(searchParams.get('page') || '1', 10);
  const searchQuery = searchParams.get('q') || '';
  const hideWithoutLink = searchParams.get('hideWithoutLink') === 'true';
  
  // Parse filters from URL
  const selectedFilters = {
    modalities: searchParams.get('modalities')?.split(',').filter(Boolean) || [],
    languages: searchParams.get('languages')?.split(',').filter(Boolean) || []
  };

  useEffect(() => {
    const fetchDatasets = async () => {
      setLoading(true);
      try {
        // Check if we have a search query
        if (searchQuery) {
          // Perform search
          const data = await searchDatasets(searchQuery, currentPage, datasetsPerPage);
          setDatasets(data.results);
          setTotalDatasets(data.results.length);
        } else {
          // Normal fetch with filters
          const filters = {
            modalities: selectedFilters.modalities,
            languages: selectedFilters.languages
          };
          
          const data = await getDatasets(currentPage, datasetsPerPage, filters);
          
          // Ensure we have valid data
          if (data && data.results && Array.isArray(data.results)) {
            setDatasets(data.results);
            setTotalDatasets(data.total || 0);
          } else {
            console.warn('Invalid data format received from API:', data);
            setDatasets([]);
            setTotalDatasets(0);
          }
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
  }, [currentPage, datasetsPerPage, searchParams, searchQuery]); // Re-fetch when URL params change

  const handleFilterChange = (filterType: 'modalities' | 'languages', value: string) => {
    const newParams = new URLSearchParams(searchParams);
    const currentFilters = selectedFilters[filterType];
    
    let updatedFilters: string[];
    if (currentFilters.includes(value)) {
      // Remove filter
      updatedFilters = currentFilters.filter(v => v !== value);
    } else {
      // Add filter
      updatedFilters = [...currentFilters, value];
    }
    
    // Update URL params
    if (updatedFilters.length > 0) {
      newParams.set(filterType, updatedFilters.join(','));
    } else {
      newParams.delete(filterType);
    }
    
    // Reset to page 1 when filters change
    newParams.delete('page');
    
    setSearchParams(newParams);
  };

  const handleToggleHideWithoutLink = (value: boolean) => {
    const newParams = new URLSearchParams(searchParams);
    
    if (value) {
      newParams.set('hideWithoutLink', 'true');
    } else {
      newParams.delete('hideWithoutLink');
    }
    
    // Reset to page 1 when filters change
    newParams.delete('page');
    
    setSearchParams(newParams);
  };

  const handleAgentSearch = async (query: string) => {
    setAgentSearchLoading(true);
    try {
      const data = await searchDatasetsWithAgent(query);
      setDatasets(data.results);
      setTotalDatasets(data.results.length);
    } catch (error) {
      console.error('Agent search failed:', error);
    } finally {
      setAgentSearchLoading(false);
    }
  };

  const handleNormalSearch = async (query: string) => {
    setNormalSearchLoading(true);
    try {
      const data = await searchDatasets(query, 1, datasetsPerPage);
      setDatasets(data.results);
      setTotalDatasets(data.results.length);
      
      // Update URL with search query
      const newParams = new URLSearchParams(searchParams);
      newParams.set('q', query);
      newParams.delete('page'); // Reset to page 1
      setSearchParams(newParams);
    } catch (error) {
      console.error('Normal search failed:', error);
    } finally {
      setNormalSearchLoading(false);
    }
  };

  const clearSearch = () => {
    const newParams = new URLSearchParams(searchParams);
    newParams.delete('q');
    newParams.delete('page');
    setSearchParams(newParams);
  };

  const activeFilterCount = 
    selectedFilters.modalities.length + 
    selectedFilters.languages.length +
    (hideWithoutLink ? 1 : 0);

  // Apply client-side filtering for datasets without links
  const filteredDatasets = useMemo(() => {
    if (!datasets || !Array.isArray(datasets)) return [];
    
    if (hideWithoutLink) {
      return datasets.filter(dataset => dataset.homepage && dataset.homepage.length > 0);
    }
    
    return datasets;
  }, [datasets, hideWithoutLink]);

  const totalPages = Math.ceil(totalDatasets / datasetsPerPage);
  
  const handlePageChange = (page: number) => {
    if (page >= 1 && page <= totalPages) {
      // Update URL with new page number
      const newParams = new URLSearchParams(searchParams);
      if (page === 1) {
        newParams.delete('page'); // Remove page param if it's page 1
      } else {
        newParams.set('page', page.toString());
      }
      setSearchParams(newParams);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  return (
    <div className="container py-8">
      <div className="space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold">Machine Learning Datasets</h1>
          <p className="text-muted-foreground mt-2">
            Browse datasets by modality, task, and language
          </p>
        </div>

        {/* Show search query info if searching */}
        {searchQuery && (
          <div className="flex items-center justify-between p-4 bg-muted rounded-lg">
            <p className="text-sm">
              Showing search results for: <strong>{searchQuery}</strong>
            </p>
            <Button variant="outline" size="sm" onClick={clearSearch}>
              Clear Search
            </Button>
          </div>
        )}
        
        <NormalSearch onSearch={handleNormalSearch} loading={normalSearchLoading} />
        <AgentSearch onSearch={handleAgentSearch} loading={agentSearchLoading} />

        {/* Main content */}
        <div className="flex gap-8">
          {/* Sidebar */}
          <aside className="w-64 shrink-0">
            <div className="sticky top-20">
              <FilterSidebar
                filters={datasetFilters}
                selectedFilters={selectedFilters}
                hideWithoutLink={hideWithoutLink}
                onFilterChange={handleFilterChange}
                onToggleHideWithoutLink={handleToggleHideWithoutLink}
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
                    Showing {filteredDatasets.length} of {totalDatasets.toLocaleString()} datasets
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
                          {(() => {
                            const pages: number[] = [];
                            const maxVisible = 7; // Maximum number of page buttons to show
                            
                            if (totalPages <= maxVisible) {
                              // Show all pages if total is small
                              for (let i = 1; i <= totalPages; i++) {
                                pages.push(i);
                              }
                            } else {
                              // Always show first page
                              pages.push(1);
                              
                              // Calculate range around current page
                              let start = Math.max(2, currentPage - 2);
                              let end = Math.min(totalPages - 1, currentPage + 2);
                              
                              // Adjust range if at the beginning or end
                              if (currentPage <= 3) {
                                end = 5;
                              } else if (currentPage >= totalPages - 2) {
                                start = totalPages - 4;
                              }
                              
                              // Add ellipsis if needed
                              if (start > 2) {
                                pages.push(-1); // -1 represents ellipsis
                              }
                              
                              // Add middle pages
                              for (let i = start; i <= end; i++) {
                                pages.push(i);
                              }
                              
                              // Add ellipsis if needed
                              if (end < totalPages - 1) {
                                pages.push(-2); // -2 represents second ellipsis
                              }
                              
                              // Always show last page
                              pages.push(totalPages);
                            }
                            
                            return pages.map((page, index) => {
                              if (page === -1 || page === -2) {
                                return (
                                  <span key={`ellipsis-${index}`} className="px-2 text-muted-foreground">
                                    ...
                                  </span>
                                );
                              }
                              
                              return (
                                <Button
                                  key={`page-${page}`}
                                  variant={currentPage === page ? "default" : "outline"}
                                  size="sm"
                                  onClick={() => handlePageChange(page)}
                                >
                                  {page}
                                </Button>
                              );
                            });
                          })()}
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
