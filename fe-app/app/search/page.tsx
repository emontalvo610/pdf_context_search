'use client';

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { search, SearchResponse, Citation } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import Link from 'next/link';
import { ArrowLeft, Search as SearchIcon, Loader2, FileText } from 'lucide-react';

export default function SearchPage() {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState<SearchResponse | null>(null);

  const searchMutation = useMutation({
    mutationFn: search,
    onSuccess: (data) => {
      setResult(data);
    },
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      searchMutation.mutate(query);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-6">
          <Link href="/">
            <Button variant="ghost" size="sm" className="mb-2">
              <ArrowLeft className="h-4 w-4" />
              Back to Documents
            </Button>
          </Link>
          <h1 className="text-3xl font-bold mb-2">Search Documents</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Search across all analyzed documents
          </p>
        </div>

        <Card className="mb-6">
          <CardContent className="pt-6">
            <form onSubmit={handleSearch} className="flex gap-2">
              <Input
                type="text"
                placeholder="Enter your search query..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="flex-1"
                disabled={searchMutation.isPending}
              />
              <Button
                type="submit"
                disabled={!query.trim() || searchMutation.isPending}
              >
                {searchMutation.isPending ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <SearchIcon className="h-4 w-4" />
                )}
                Search
              </Button>
            </form>
          </CardContent>
        </Card>

        {searchMutation.isError && (
          <Card className="mb-6 border-red-200 bg-red-50 dark:bg-red-900/20">
            <CardContent className="pt-6">
              <p className="text-red-600 dark:text-red-400">
                Error: {(searchMutation.error as Error).message}
              </p>
            </CardContent>
          </Card>
        )}

        {result && (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Answer</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="prose dark:prose-invert max-w-none">
                  {result.response}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Citations</CardTitle>
                <CardDescription>
                  {result.citations.length} relevant sections found
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[600px]">
                  <div className="space-y-4">
                    {result.citations.map((citation: Citation, index: number) => (
                      <Card
                        key={`${citation.document_id}-${citation.section_id}-${index}`}
                        className="hover:shadow-md transition-shadow"
                      >
                        <CardHeader>
                          <div className="flex items-start justify-between gap-4">
                            <div className="flex-1">
                              <CardTitle className="text-base mb-1">
                                {citation.section_title}
                              </CardTitle>
                              <CardDescription>
                                {citation.document_name} · Relevance:{' '}
                                {(citation.score * 100).toFixed(1)}%
                              </CardDescription>
                            </div>
                            <Link
                              href={`/documents/${citation.document_id}?section=${citation.section_id}`}
                            >
                              <Button variant="outline" size="sm">
                                <FileText className="h-4 w-4" />
                                View
                              </Button>
                            </Link>
                          </div>
                        </CardHeader>
                        <CardContent>
                          <div className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                            {citation.text}
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          </div>
        )}

        {!result && !searchMutation.isPending && (
          <Card>
            <CardContent className="py-12">
              <div className="text-center text-gray-500">
                <SearchIcon className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Enter a search query to find relevant information</p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}

