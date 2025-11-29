'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useParams, useRouter } from 'next/navigation';
import { getDocument, Section, deleteDocument } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import Link from 'next/link';
import { ArrowLeft, FileText, Loader2, ChevronRight, ChevronDown, Trash2 } from 'lucide-react';

interface TreeNode {
  section: Section;
  children: TreeNode[];
}

interface SectionTreeItemProps {
  node: TreeNode;
  selectedSection: Section | null;
  onSelectSection: (section: Section) => void;
  level?: number;
}

function SectionTreeItem({ node, selectedSection, onSelectSection, level = 0 }: SectionTreeItemProps) {
  const [isExpanded, setIsExpanded] = useState(true);
  const hasChildren = node.children.length > 0;
  const isSelected = selectedSection?.id === node.section.id;

  return (
    <div>
      <Button
        variant={isSelected ? 'default' : 'ghost'}
        className="w-full justify-start text-left h-auto py-2"
        style={{ paddingLeft: `${level * 1 + 0.5}rem` }}
        onClick={() => onSelectSection(node.section)}
      >
        <div className="flex items-start gap-1 w-full">
          {hasChildren && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                setIsExpanded(!isExpanded);
              }}
              className="flex-shrink-0 mt-0.5 hover:bg-gray-200 dark:hover:bg-gray-700 rounded p-0.5"
            >
              {isExpanded ? (
                <ChevronDown className="h-3 w-3" />
              ) : (
                <ChevronRight className="h-3 w-3" />
              )}
            </button>
          )}
          {!hasChildren && <div className="w-4" />}
          <FileText className="h-4 w-4 mt-0.5 flex-shrink-0" />
          <div className="flex-1 min-w-0">
            <p className="font-medium text-sm truncate">{node.section.title}</p>
            <p className="text-xs text-gray-500">Page {node.section.page_number}</p>
          </div>
        </div>
      </Button>
      {hasChildren && isExpanded && (
        <div>
          {node.children.map((child) => (
            <SectionTreeItem
              key={child.section.id}
              node={child}
              selectedSection={selectedSection}
              onSelectSection={onSelectSection}
              level={level + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default function DocumentPage() {
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const documentId = params.id as string;
  const [selectedSection, setSelectedSection] = useState<Section | null>(null);

  const { data, isLoading, error } = useQuery({
    queryKey: ['document', documentId],
    queryFn: () => getDocument(documentId),
  });

  const deleteMutation = useMutation({
    mutationFn: deleteDocument,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      router.push('/');
    },
  });

  const handleDelete = () => {
    if (confirm('Are you sure you want to delete this document?')) {
      deleteMutation.mutate(documentId);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="max-w-md">
          <CardContent className="p-6">
            <p className="text-red-500">Error loading document</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Build tree structure
  const buildTree = (sections: Section[]): TreeNode[] => {
    const sectionMap = new Map<string, TreeNode>();
    const rootNodes: TreeNode[] = [];

    // Create nodes
    sections.forEach((section) => {
      sectionMap.set(section.id, { section, children: [] });
    });

    // Build relationships
    sections.forEach((section) => {
      const node = sectionMap.get(section.id)!;
      if (section.parent_id && sectionMap.has(section.parent_id)) {
        const parent = sectionMap.get(section.parent_id)!;
        parent.children.push(node);
      } else {
        rootNodes.push(node);
      }
    });

    return rootNodes;
  };

  const tree = buildTree(data.sections);
  const currentSection = selectedSection || data.sections[0];

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <Link href="/">
              <Button variant="ghost" size="sm" className="mb-2">
                <ArrowLeft className="h-4 w-4" />
                Back to Documents
              </Button>
            </Link>
            <h1 className="text-3xl font-bold">{data.metadata.filename}</h1>
            <p className="text-gray-600 dark:text-gray-400">
              {data.metadata.total_sections} sections
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Badge
              className={
                data.metadata.status === 'completed'
                  ? 'bg-green-500'
                  : data.metadata.status === 'in_progress'
                  ? 'bg-blue-500'
                  : data.metadata.status === 'failed'
                  ? 'bg-red-500'
                  : 'bg-yellow-500'
              }
            >
              {data.metadata.status.replace('_', ' ').toUpperCase()}
            </Badge>
            <Button
              variant="outline"
              size="sm"
              onClick={handleDelete}
              disabled={deleteMutation.isPending}
              className="text-red-600 hover:text-red-700 hover:bg-red-50"
            >
              {deleteMutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Trash2 className="h-4 w-4" />
              )}
              Delete
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle className="text-lg">Sections</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <ScrollArea className="h-[calc(100vh-300px)]">
                <div className="space-y-0.5 p-2">
                  {tree.map((node) => (
                    <SectionTreeItem
                      key={node.section.id}
                      node={node}
                      selectedSection={currentSection}
                      onSelectSection={setSelectedSection}
                    />
                  ))}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>

          <Card className="lg:col-span-3">
            <CardHeader>
              <CardTitle>{currentSection?.title || 'No Section Selected'}</CardTitle>
              {currentSection && (
                <p className="text-sm text-gray-500">
                  Page {currentSection.page_number}
                </p>
              )}
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[calc(100vh-300px)]">
                <div className="prose dark:prose-invert max-w-none">
                  {currentSection ? (
                    <div className="whitespace-pre-wrap">
                      {currentSection.content}
                    </div>
                  ) : (
                    <p className="text-gray-500">
                      Select a section to view its content
                    </p>
                  )}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

