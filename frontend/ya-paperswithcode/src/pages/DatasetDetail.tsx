import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, ExternalLink, Globe, FileText, Hash } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import type { Dataset } from '../types';

export function DatasetDetail() {
  const { id } = useParams<{ id: string }>();
  const [dataset, setDataset] = useState<Dataset | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDataset = async () => {
      if (!id) return;
      
      // Extract the actual dataset ID from the URL parameter (format: id-name)
      const datasetId = id.split('-')[0];
      
      setLoading(true);
      try {
        // Fetch specific dataset by ID
        const response = await fetch(`http://0.0.0.0:8000/api/v1/datasets/${datasetId}`);
        
        if (response.ok) {
          const data = await response.json();
          setDataset(data);
        } else if (response.status === 404) {
          setDataset(null);
        } else {
          console.error('Failed to fetch dataset:', response.statusText);
          setDataset(null);
        }
      } catch (error) {
        console.error('Failed to fetch dataset:', error);
        setDataset(null);
      } finally {
        setLoading(false);
      }
    };

    fetchDataset();
  }, [id]);

  if (loading) {
    return (
      <div className="container py-8">
        <div className="flex justify-center py-12">
          <div className="text-muted-foreground">Loading dataset...</div>
        </div>
      </div>
    );
  }

  if (!dataset) {
    return (
      <div className="container py-8">
        <div className="text-center py-12">
          <h2 className="text-2xl font-semibold mb-4">Dataset not found</h2>
          <Link to="/datasets">
            <Button>
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Datasets
            </Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="container py-8">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <Link to="/datasets">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back
            </Button>
          </Link>
        </div>

        {/* Main Content */}
        <div className="grid gap-6 lg:grid-cols-3">
          {/* Left Column - Main Info */}
          <div className="lg:col-span-2 space-y-6">
            {/* Title and Description */}
            <Card>
              <CardHeader>
                <CardTitle className="text-3xl">
                  {dataset.name}
                </CardTitle>
                {dataset.full_name && dataset.full_name !== dataset.name && (
                  <p className="text-lg text-muted-foreground mt-2">
                    {dataset.full_name}
                  </p>
                )}
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="prose prose-sm max-w-none">
                  <div 
                    className="text-base leading-relaxed"
                    dangerouslySetInnerHTML={{ 
                      __html: (dataset.description || 'No description available.')
                        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                        .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:underline">$1</a>')
                        .replace(/\n\n/g, '</p><p class="mt-4">')
                        .replace(/^/, '<p>')
                        .replace(/$/, '</p>')
                    }}
                  />
                </div>
                
                {/* External Links */}
                <div className="flex flex-wrap gap-2 pt-4 border-t">
                  {dataset.homepage && (
                    <a href={dataset.homepage} target="_blank" rel="noopener noreferrer">
                      <Button variant="default" size="sm">
                        <Globe className="mr-2 h-4 w-4" />
                        Visit Dataset Homepage
                      </Button>
                    </a>
                  )}
                  <a href={`https://paperswithcode.com/dataset/${dataset.id}`} target="_blank" rel="noopener noreferrer">
                    <Button variant="outline" size="sm">
                      <ExternalLink className="mr-2 h-4 w-4" />
                      View on PapersWithCode
                    </Button>
                  </a>
                </div>
              </CardContent>
            </Card>

            {/* Paper Information */}
            {(dataset.paper_title || dataset.paper_url) && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="h-5 w-5" />
                    Related Paper
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {dataset.paper_title && (
                    <p className="font-medium mb-2">{dataset.paper_title}</p>
                  )}
                  {dataset.paper_url && (
                    <a href={dataset.paper_url} target="_blank" rel="noopener noreferrer">
                      <Button variant="outline" size="sm">
                        View Paper
                        <ExternalLink className="ml-2 h-3 w-3" />
                      </Button>
                    </a>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Subtasks */}
            {dataset.subtasks && dataset.subtasks.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Hash className="h-5 w-5" />
                    Tasks
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {dataset.subtasks.map((task, index) => (
                      <Badge key={index} variant="secondary">
                        {task}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Right Column - Metadata */}
          <div className="space-y-6">
            {/* Quick Info */}
            <Card>
              <CardHeader>
                <CardTitle>Dataset Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Homepage */}
                {dataset.homepage && (
                  <div>
                    <p className="text-sm font-medium mb-1">Homepage</p>
                    <a href={dataset.homepage} target="_blank" rel="noopener noreferrer" className="block">
                      <Button variant="outline" size="sm" className="w-full">
                        <Globe className="mr-2 h-3 w-3" />
                        Visit Homepage
                      </Button>
                    </a>
                  </div>
                )}

                {/* Modalities */}
                {dataset.modalities && dataset.modalities.length > 0 && (
                  <div>
                    <p className="text-sm font-medium mb-2">Modalities</p>
                    <div className="flex flex-wrap gap-1">
                      {dataset.modalities.map((modality, index) => (
                        <Badge key={index} variant="outline">
                          {modality}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {/* Languages */}
                {dataset.languages && dataset.languages.length > 0 && (
                  <div>
                    <p className="text-sm font-medium mb-2">Languages</p>
                    <div className="flex flex-wrap gap-1">
                      {dataset.languages.map((language, index) => (
                        <Badge key={index} variant="outline">
                          {language}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {/* ID */}
                <div>
                  <p className="text-sm font-medium mb-1">Dataset ID</p>
                  <code className="text-xs bg-muted px-2 py-1 rounded">
                    {dataset.id}
                  </code>
                </div>
              </CardContent>
            </Card>

            {/* Statistics (if available) */}
            {(dataset.papers || dataset.downloads) && (
              <Card>
                <CardHeader>
                  <CardTitle>Usage Statistics</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  {dataset.papers && (
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Papers using this dataset</span>
                      <span className="font-medium">{dataset.papers.toLocaleString()}</span>
                    </div>
                  )}
                  {dataset.downloads && (
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Downloads</span>
                      <span className="font-medium">{dataset.downloads.toLocaleString()}</span>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}