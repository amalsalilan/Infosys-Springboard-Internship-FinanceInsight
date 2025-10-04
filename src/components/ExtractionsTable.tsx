import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

interface Extraction {
  text: string;
  class: string;
  score?: number;
}

interface ExtractionsTableProps {
  extractions: Extraction[];
}

const ExtractionsTable = ({ extractions }: ExtractionsTableProps) => {
  const hasScores = extractions.some((e) => e.score !== undefined);

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
    <div className="bg-white border-t border-border p-6">
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
                <TableRow key={index} className="hover:bg-muted/30 transition-colors">
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
  );
};

export default ExtractionsTable;
