import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Play, ChevronLeft, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";

interface Extraction {
  text: string;
  class: string;
  score?: number;
}

interface ExtractionsTableProps {
  extractions: Extraction[];
  htmlVisualization?: string | null;
  analysisType?: "sentiment" | "ner" | "langextract";
  currentIndex?: number;
  onNavigate?: {
    onPlay: () => void;
    onPrevious: () => void;
    onNext: () => void;
  };
}

const ExtractionsTable = ({ extractions, htmlVisualization, analysisType, currentIndex = -1, onNavigate }: ExtractionsTableProps) => {
  const hasScores = extractions.some((e) => e.score !== undefined);
  const hasExtractions = extractions.length > 0;

  // For LangExtract, render the HTML visualization instead of the table
  if (analysisType === "langextract" && htmlVisualization) {
    return (
      <div className="h-full bg-white overflow-hidden flex flex-col">
        <div className="flex-1 overflow-auto p-6">
          <div
            className="bg-white rounded-lg border border-border p-4"
            dangerouslySetInnerHTML={{ __html: htmlVisualization }}
          />
        </div>
      </div>
    );
  }

  const getClassColor = (className: string) => {
    const colors: Record<string, string> = {
      // Sentiment classes
      positive: "bg-green-100 text-green-700",
      negative: "bg-red-100 text-red-700",
      neutral: "bg-gray-100 text-gray-700",
      // NER classes
      PER: "bg-pink-100 text-pink-700",
      ORG: "bg-blue-100 text-blue-700",
      LOC: "bg-green-100 text-green-700",
      MISC: "bg-yellow-100 text-yellow-700",
      // Default
      default: "bg-muted text-foreground",
    };

    return colors[className] || colors.default;
  };

  return (
    <div className="h-full bg-white overflow-hidden flex flex-col">
      {/* Navigation Controls - Only for LangExtract */}
      {onNavigate && analysisType === "langextract" && (
        <div className="border-b border-border p-4 bg-muted/30">
          <div className="flex items-center justify-center gap-2">
            <Button
              onClick={onNavigate.onPlay}
              disabled={!hasExtractions}
              variant="outline"
              size="sm"
              className="gap-2"
            >
              <Play className="h-4 w-4" />
              Play
            </Button>
            <Button
              onClick={onNavigate.onPrevious}
              disabled={!hasExtractions || currentIndex <= 0}
              variant="outline"
              size="sm"
            >
              <ChevronLeft className="h-4 w-4" />
              Previous
            </Button>
            <span className="text-sm text-muted-foreground px-3">
              {hasExtractions ? `${currentIndex + 1} / ${extractions.length}` : "0 / 0"}
            </span>
            <Button
              onClick={onNavigate.onNext}
              disabled={!hasExtractions || currentIndex >= extractions.length - 1}
              variant="outline"
              size="sm"
            >
              Next
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}

      <div className="flex-1 overflow-auto p-6">
        <div className="bg-white rounded-lg overflow-hidden border border-border">
          <Table>
          <TableHeader>
            <TableRow className="bg-muted/50 hover:bg-muted/70">
              <TableHead className="text-center font-medium text-foreground">Extractions</TableHead>
              <TableHead className="text-center font-medium text-foreground">Extraction Class</TableHead>
              {hasScores && (
                <TableHead className="text-center font-medium text-foreground">Confidence</TableHead>
              )}
            </TableRow>
          </TableHeader>
          <TableBody>
            {extractions.length === 0 ? (
              <TableRow>
                <TableCell colSpan={hasScores ? 3 : 2} className="text-center text-muted-foreground h-32">
                  <div className="flex flex-col items-center gap-2">
                    <div className="h-10 w-10 rounded-full bg-muted flex items-center justify-center">
                      <span className="text-xl">📄</span>
                    </div>
                    <p className="text-sm">No extractions yet - upload a document to begin</p>
                  </div>
                </TableCell>
              </TableRow>
            ) : (
              extractions.map((extraction, index) => (
                <TableRow
                  key={index}
                  data-table-row={index}
                  className={cn(
                    "hover:bg-muted/30 transition-colors",
                    currentIndex === index && "bg-primary/10 border-l-4 border-l-primary"
                  )}
                >
                  <TableCell className="text-center max-w-md truncate" title={extraction.text}>
                    {extraction.text}
                  </TableCell>
                  <TableCell className="text-center">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${getClassColor(extraction.class)}`}>
                      {extraction.class}
                    </span>
                  </TableCell>
                  {hasScores && (
                    <TableCell className="text-center">
                      {extraction.score !== undefined && (
                        <span className="text-sm font-medium">
                          {(extraction.score * 100).toFixed(1)}%
                        </span>
                      )}
                    </TableCell>
                  )}
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
        </div>
      </div>
    </div>
  );
};

export default ExtractionsTable;
