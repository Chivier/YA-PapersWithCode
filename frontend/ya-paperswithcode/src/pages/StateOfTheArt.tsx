import { TrendingUp, Trophy, BarChart3 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';

const benchmarkCategories = [
  {
    id: 'cv',
    name: 'Computer Vision',
    icon: BarChart3,
    benchmarks: ['ImageNet', 'COCO Object Detection', 'ADE20K', 'PASCAL VOC'],
    color: 'text-blue-600'
  },
  {
    id: 'nlp',
    name: 'Natural Language Processing',
    icon: TrendingUp,
    benchmarks: ['GLUE', 'SQuAD 2.0', 'WMT Translation', 'SuperGLUE'],
    color: 'text-green-600'
  },
  {
    id: 'speech',
    name: 'Speech',
    icon: Trophy,
    benchmarks: ['LibriSpeech', 'Common Voice', 'TIMIT', 'WSJ'],
    color: 'text-purple-600'
  }
];

export function StateOfTheArt() {
  return (
    <div className="container py-8">
      <div className="space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold">Browse State-of-the-Art</h1>
          <p className="text-muted-foreground mt-2">
            Explore the best performing models on various benchmarks
          </p>
        </div>

        {/* Categories Grid */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {benchmarkCategories.map((category) => {
            const Icon = category.icon;
            return (
              <Card key={category.id} className="hover:shadow-lg transition-shadow cursor-pointer">
                <CardHeader>
                  <CardTitle className="flex items-center gap-3">
                    <Icon className={`h-6 w-6 ${category.color}`} />
                    {category.name}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {category.benchmarks.map((benchmark) => (
                      <div
                        key={benchmark}
                        className="p-2 rounded hover:bg-muted transition-colors"
                      >
                        <p className="text-sm font-medium">{benchmark}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Info Section */}
        <div className="mt-12 grid gap-6 md:grid-cols-3">
          <div className="text-center">
            <div className="text-3xl font-bold text-primary">500+</div>
            <p className="text-sm text-muted-foreground mt-1">Benchmarks Tracked</p>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-primary">10,000+</div>
            <p className="text-sm text-muted-foreground mt-1">Model Results</p>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-primary">Daily</div>
            <p className="text-sm text-muted-foreground mt-1">Updates</p>
          </div>
        </div>
      </div>
    </div>
  );
}