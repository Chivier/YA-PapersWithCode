import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  ArrowLeft, 
  ExternalLink, 
  Globe, 
  FileText, 
  Copy, 
  CheckCircle,
  Calendar,
  Languages,
  Database,
  BookOpen,
  Tag,
  Home,
  ChevronRight
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import type { Dataset } from '../types';

export function DatasetDetail() {
  const { id } = useParams<{ id: string }>();
  const [dataset, setDataset] = useState<Dataset | null>(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const fetchDataset = async () => {
      if (!id) return;
      
      // Use the full ID from the URL parameter - dataset IDs can contain hyphens
      const datasetId = id;
      
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

  const handleCopyId = () => {
    if (dataset?.id) {
      navigator.clipboard.writeText(dataset.id);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const formatDate = (dateString: string | undefined) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
  };

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
    <div className="min-h-screen bg-gray-50">
      {/* Breadcrumb */}
      <div className="bg-white border-b">
        <div className="container py-3">
          <nav className="flex items-center space-x-2 text-sm text-muted-foreground">
            <Link to="/" className="hover:text-foreground transition-colors">
              <Home className="h-4 w-4" />
            </Link>
            <ChevronRight className="h-4 w-4" />
            <Link to="/datasets" className="hover:text-foreground transition-colors">
              Datasets
            </Link>
            <ChevronRight className="h-4 w-4" />
            <span className="text-foreground font-medium">
              {dataset?.name || 'Loading...'}
            </span>
          </nav>
        </div>
      </div>

      <div className="container py-8">
        <div className="space-y-8">
          {/* Hero Section */}
          <div className="bg-white rounded-lg border p-8">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h1 className="text-4xl font-bold text-gray-900 mb-2">
                  {dataset.name}
                </h1>
                {dataset.full_name && dataset.full_name !== dataset.name && (
                  <p className="text-xl text-gray-600 mb-4">
                    {dataset.full_name}
                  </p>
                )}
                <div className="flex items-center gap-4 text-sm text-gray-500">
                  <div className="flex items-center gap-1">
                    <Database className="h-4 w-4" />
                    <span>Dataset</span>
                  </div>
                  {dataset.created_at && (
                    <div className="flex items-center gap-1">
                      <Calendar className="h-4 w-4" />
                      <span>Added {formatDate(dataset.created_at)}</span>
                    </div>
                  )}
                </div>
              </div>
              <div className="flex gap-2">
                <Link to="/datasets">
                  <Button variant="ghost">
                    <ArrowLeft className="mr-2 h-4 w-4" />
                    Back to Datasets
                  </Button>
                </Link>
              </div>
            </div>
          </div>

          {/* Main Content Grid */}
          <div className="grid gap-6 lg:grid-cols-3">
            {/* Left Column - Main Content */}
            <div className="lg:col-span-2 space-y-6">
              {/* Description Card */}
              <Card className="shadow-sm">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BookOpen className="h-5 w-5 text-primary" />
                    Description
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="prose prose-sm max-w-none">
                    <div 
                      className="text-base leading-relaxed text-gray-700"
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
                </CardContent>
              </Card>

              {/* Tasks and Subtasks */}
              {dataset.subtasks && dataset.subtasks.length > 0 && (
                <Card className="shadow-sm">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Tag className="h-5 w-5 text-primary" />
                      Tasks & Applications
                    </CardTitle>
                    <CardDescription>
                      This dataset is commonly used for the following tasks
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-2">
                      {dataset.subtasks.map((task, index) => (
                        <Badge 
                          key={index} 
                          variant="secondary"
                          className="px-3 py-1.5 text-sm font-medium"
                        >
                          {task}
                        </Badge>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* External Links */}
              <Card className="shadow-sm">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <ExternalLink className="h-5 w-5 text-primary" />
                    External Resources
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {dataset.homepage && (
                      <a 
                        href={dataset.homepage} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="flex items-center gap-3 p-3 rounded-lg border hover:bg-gray-50 transition-colors"
                      >
                        <Globe className="h-5 w-5 text-blue-600" />
                        <div className="flex-1">
                          <p className="font-medium">Official Dataset Homepage</p>
                          <p className="text-sm text-gray-500 truncate">{dataset.homepage}</p>
                        </div>
                        <ExternalLink className="h-4 w-4 text-gray-400" />
                      </a>
                    )}
                    
                    <a 
                      href={`https://paperswithcode.com/dataset/${dataset.id}`} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="flex items-center gap-3 p-3 rounded-lg border hover:bg-gray-50 transition-colors"
                    >
                      <Database className="h-5 w-5 text-purple-600" />
                      <div className="flex-1">
                        <p className="font-medium">View on Papers with Code</p>
                        <p className="text-sm text-gray-500">Access benchmarks and leaderboards</p>
                      </div>
                      <ExternalLink className="h-4 w-4 text-gray-400" />
                    </a>
                  </div>
                </CardContent>
              </Card>

              {/* Related Paper */}
              {(dataset.paper_title || dataset.paper_url) && (
                <Card className="shadow-sm">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <FileText className="h-5 w-5 text-primary" />
                      Introducing Paper
                    </CardTitle>
                    <CardDescription>
                      The paper that introduced this dataset
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="p-4 bg-gray-50 rounded-lg">
                      {dataset.paper_title && (
                        <h4 className="font-semibold text-gray-900 mb-3">
                          {dataset.paper_title}
                        </h4>
                      )}
                      {dataset.paper_url && (
                        <a 
                          href={dataset.paper_url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                        >
                          <Button variant="default" size="sm">
                            <FileText className="mr-2 h-4 w-4" />
                            Read Paper
                            <ExternalLink className="ml-2 h-3 w-3" />
                          </Button>
                        </a>
                      )}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>

            {/* Right Column - Metadata Sidebar */}
            <div className="space-y-6">
              {/* Quick Info Card */}
              <Card className="shadow-sm">
                <CardHeader>
                  <CardTitle>Dataset Information</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Dataset ID with Copy */}
                  <div>
                    <p className="text-sm font-medium text-gray-600 mb-2">Dataset ID</p>
                    <div className="flex items-center gap-2">
                      <code className="flex-1 text-xs bg-gray-100 px-3 py-2 rounded font-mono">
                        {dataset.id}
                      </code>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={handleCopyId}
                        className="h-8 w-8 p-0"
                      >
                        {copied ? (
                          <CheckCircle className="h-4 w-4 text-green-600" />
                        ) : (
                          <Copy className="h-4 w-4" />
                        )}
                      </Button>
                    </div>
                  </div>

                  {/* Modalities */}
                  {dataset.modalities && dataset.modalities.length > 0 && (
                    <div>
                      <p className="text-sm font-medium text-gray-600 mb-2 flex items-center gap-1">
                        <Database className="h-3 w-3" />
                        Modalities
                      </p>
                      <div className="flex flex-wrap gap-1.5">
                        {dataset.modalities.map((modality, index) => (
                          <Badge 
                            key={index} 
                            variant="outline"
                            className="text-xs"
                          >
                            {modality}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Languages */}
                  {dataset.languages && dataset.languages.length > 0 && (
                    <div>
                      <p className="text-sm font-medium text-gray-600 mb-2 flex items-center gap-1">
                        <Languages className="h-3 w-3" />
                        Languages
                      </p>
                      <div className="flex flex-wrap gap-1.5">
                        {dataset.languages.map((language, index) => (
                          <Badge 
                            key={index} 
                            variant="outline"
                            className="text-xs"
                          >
                            {language}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Homepage Link */}
                  {dataset.homepage && (
                    <div>
                      <p className="text-sm font-medium text-gray-600 mb-2">Homepage</p>
                      <a href={dataset.homepage} target="_blank" rel="noopener noreferrer">
                        <Button variant="outline" size="sm" className="w-full">
                          <Globe className="mr-2 h-3 w-3" />
                          Visit Homepage
                        </Button>
                      </a>
                    </div>
                  )}
                
                  {/* Date Added */}
                  {dataset.created_at && (
                    <div>
                      <p className="text-sm font-medium text-gray-600 mb-2 flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        Date Added
                      </p>
                      <p className="text-sm text-gray-800">
                        {formatDate(dataset.created_at)}
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Usage Statistics (if available) */}
              {(dataset.papers || dataset.downloads) && (
                <Card className="shadow-sm">
                  <CardHeader>
                    <CardTitle>Usage Statistics</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {dataset.papers && (
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Papers using dataset</span>
                        <span className="font-semibold text-lg">{dataset.papers.toLocaleString()}</span>
                      </div>
                    )}
                    {dataset.downloads && (
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Downloads</span>
                        <span className="font-semibold text-lg">{dataset.downloads.toLocaleString()}</span>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
