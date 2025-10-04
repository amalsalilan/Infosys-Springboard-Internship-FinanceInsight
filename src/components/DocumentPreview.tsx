import { Button } from "@/components/ui/button";
import { Upload, X, FileText } from "lucide-react";
import { useRef } from "react";

interface DocumentPreviewProps {
  document: File | null;
  htmlPreview: string | null;
  onFileUpload: (file: File) => void;
  onClear: () => void;
  onProcess: () => void;
  isProcessing: boolean;
}

const DocumentPreview = ({ document, htmlPreview, onFileUpload, onClear, onProcess, isProcessing }: DocumentPreviewProps) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onFileUpload(file);
    }
  };

  return (
    <div className="flex-1 flex flex-col">
      <div className={`flex-1 bg-white relative border-r border-border ${htmlPreview ? 'overflow-hidden' : 'overflow-auto p-8'}`}>
        {htmlPreview ? (
          <iframe
            srcDoc={htmlPreview}
            className="w-full h-full bg-white block"
            title="Document Preview"
            sandbox="allow-same-origin"
            style={{ minHeight: '100%', display: 'block' }}
          />
        ) : (
          <div className="flex flex-col items-center justify-center h-full gap-4">
            {document ? (
              <>
                <div className="h-20 w-20 rounded-lg border-2 border-border flex items-center justify-center">
                  <FileText className="h-10 w-10 text-muted-foreground" />
                </div>
                <span className="text-foreground font-medium">{document.name}</span>
                <p className="text-muted-foreground text-sm">Click Process Document to analyze</p>
              </>
            ) : (
              <>
                <div className="h-20 w-20 rounded-lg border-2 border-dashed border-border flex items-center justify-center">
                  <FileText className="h-10 w-10 text-muted-foreground" />
                </div>
                <span className="text-muted-foreground text-sm">Upload a document to begin analysis</span>
              </>
            )}
          </div>
        )}
        <div className="absolute bottom-6 right-6 flex gap-2 z-10">
          <Button
            size="default"
            className="bg-foreground hover:bg-foreground/90 text-white shadow-lg"
            onClick={handleUploadClick}
          >
            <Upload className="h-4 w-4 mr-2" />
            Upload
          </Button>
          <Button
            size="default"
            variant="outline"
            className="hover:bg-secondary shadow-lg bg-white"
            onClick={onClear}
          >
            <X className="h-4 w-4 mr-2" />
            Clear
          </Button>
        </div>
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          onChange={handleFileChange}
          accept=".txt,.pdf,.doc,.docx"
        />
      </div>
      <div className="h-14 bg-white border-t border-r border-border flex items-center justify-center">
        <Button
          variant="ghost"
          className="text-sm text-muted-foreground hover:text-foreground hover:bg-secondary"
          onClick={onProcess}
          disabled={!document || isProcessing}
        >
          {isProcessing ? "Analyzing..." : "Process Document"}
        </Button>
      </div>
    </div>
  );
};

export default DocumentPreview;
