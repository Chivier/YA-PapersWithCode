import { useState, useEffect } from 'react';
import { MethodCard } from '../components/methods/MethodCard';
import type { MethodCategory } from '../types';
import { getMethods } from '../lib/api';

export function Methods() {
  const [categories, setCategories] = useState<MethodCategory[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMethods = async () => {
      setLoading(true);
      try {
        const data = await getMethods();
        // The API returns a flat list of methods, but the UI expects categories.
        // For now, we'll create a single category with all methods.
        const allMethodsCategory: MethodCategory = {
          id: 'all-methods',
          name: 'All Methods',
          description: 'A comprehensive list of all available methods.',
          subcategories: data.results.map((method, index) => ({ name: method.name, slug: `${method.id}-${index}`, methods: [] })),
        };
        setCategories([allMethodsCategory]);
      } catch (error) {
        console.error('Failed to fetch methods:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchMethods();
  }, []);

  return (
    <div className="container py-8">
      <div className="space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold">The Methods Corpus</h1>
          <p className="text-muted-foreground mt-2">
            Explore machine learning methods and techniques organized by category
          </p>
        </div>

        {/* Methods grid */}
        {loading ? (
          <div className="flex justify-center py-12">
            <div className="text-muted-foreground">Loading methods...</div>
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2">
            {categories.map((category) => (
              <MethodCard key={category.id} category={category} />
            ))}
          </div>
        )}

        {/* Additional information */}
        <div className="mt-12 p-6 bg-muted rounded-lg">
          <h2 className="text-lg font-semibold mb-2">About the Methods Corpus</h2>
          <p className="text-sm text-muted-foreground">
            The Methods Corpus is a comprehensive collection of machine learning methods, techniques, and algorithms. 
            Each method is categorized by domain and includes links to papers that introduce or utilize the technique. 
            Browse through categories to discover foundational methods and cutting-edge approaches in machine learning.
          </p>
        </div>
      </div>
    </div>
  );
}