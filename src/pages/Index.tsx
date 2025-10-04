import { useState } from "react";
import Header from "@/components/Header";
import Sidebar from "@/components/Sidebar";
import DocumentPreview from "@/components/DocumentPreview";
import InsightsPanel from "@/components/InsightsPanel";
import ExtractionsTable from "@/components/ExtractionsTable";
import { useToast } from "@/hooks/use-toast";
import { processDocument, convertDocument, analyzeSentiment, recognizeEntities, extractInformation, SentimentResponse, NERResponse, LangExtractResponse, ConversionResponse } from "@/services/api";

const Index = () => {
  const [selectedAnalysis, setSelectedAnalysis] = useState<"sentiment" | "ner" | "langextract">("sentiment");
  const [document, setDocument] = useState<File | null>(null);
  const [htmlPreview, setHtmlPreview] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isConverting, setIsConverting] = useState(false);
  const [extractions, setExtractions] = useState<Array<{ text: string; class: string; score?: number }>>([]);
  const [analysisResults, setAnalysisResults] = useState<SentimentResponse | NERResponse | LangExtractResponse | null>(null);
  const [conversionData, setConversionData] = useState<ConversionResponse | null>(null);
  const { toast } = useToast();

  const handleFileUpload = async (file: File) => {
    setDocument(file);
    setHtmlPreview(null);
    setExtractions([]);
    setAnalysisResults(null);
    setIsConverting(true);

    try {
      // Automatically convert document and show preview
      const conversion = await convertDocument(file);
      setConversionData(conversion);
      setHtmlPreview(conversion.html);

      toast({
        title: "Document converted",
        description: `${file.name} is ready for analysis. Click "Process Document" to analyze.`,
      });
    } catch (error) {
      console.error("Conversion error:", error);
      toast({
        title: "Conversion failed",
        description: error instanceof Error ? error.message : "Failed to convert document.",
        variant: "destructive",
      });
      // Keep the document reference so user can try processing again
    } finally {
      setIsConverting(false);
    }
  };

  const handleClear = () => {
    setDocument(null);
    setHtmlPreview(null);
    setExtractions([]);
    setAnalysisResults(null);
    setConversionData(null);
  };

  const handleProcess = async () => {
    if (!document) return;

    setIsProcessing(true);

    try {
      let conversion = conversionData;
      let analysis: SentimentResponse | NERResponse | LangExtractResponse;

      // If document hasn't been converted yet, convert it first
      if (!conversion) {
        conversion = await convertDocument(document);
        setConversionData(conversion);
      }

      // Run the selected analysis on the converted text
      if (selectedAnalysis === "sentiment") {
        analysis = await analyzeSentiment(conversion.text, conversion.html);
      } else if (selectedAnalysis === "ner") {
        analysis = await recognizeEntities(conversion.text);
      } else {
        analysis = await extractInformation(
          conversion.text,
          'Extract financial entities, amounts, dates, and key metrics from the document',
          [
            {
              text: 'Apple Inc. reported revenue of $394.3 billion for fiscal year 2022.',
              extractions: [
                {
                  extraction_class: 'Company',
                  extraction_text: 'Apple Inc.',
                  attributes: { type: 'organization' },
                },
                {
                  extraction_class: 'Financial Metric',
                  extraction_text: 'revenue of $394.3 billion',
                  attributes: { amount: '$394.3 billion', metric: 'revenue' },
                },
                {
                  extraction_class: 'Time Period',
                  extraction_text: 'fiscal year 2022',
                  attributes: { year: '2022', type: 'fiscal year' },
                },
              ],
            },
          ]
        );
      }

      setAnalysisResults(analysis);

      // Set HTML preview based on analysis type
      if (selectedAnalysis === "sentiment") {
        const sentimentData = analysis as SentimentResponse;
        setHtmlPreview(sentimentData.highlighted_html || conversion.html);

        // Extract sentiment results for table
        setExtractions(
          sentimentData.sentiment_results.map((result) => ({
            text: result.sentence,
            class: result.class,
            score: Math.max(
              result.confidence_scores.positive,
              result.confidence_scores.negative,
              result.confidence_scores.neutral
            ),
          }))
        );
      } else if (selectedAnalysis === "ner") {
        const nerData = analysis as NERResponse;
        setHtmlPreview(nerData.highlighted_html);

        // Extract NER entities for table
        setExtractions(
          nerData.entities.map((entity) => ({
            text: entity.word,
            class: entity.entity_group,
            score: entity.score,
          }))
        );
      } else if (selectedAnalysis === "langextract") {
        const langExtractData = analysis as LangExtractResponse;
        setHtmlPreview(langExtractData.html_visualization);

        // Extract structured data for table
        setExtractions(
          langExtractData.extractions.map((extraction) => ({
            text: extraction.extraction_text,
            class: extraction.extraction_class,
          }))
        );
      }

      toast({
        title: "Processing complete",
        description: `Document analyzed successfully using ${selectedAnalysis}.`,
      });
    } catch (error) {
      console.error("Processing error:", error);
      toast({
        title: "Processing failed",
        description: error instanceof Error ? error.message : "There was an error processing your document.",
        variant: "destructive",
      });
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="h-screen flex flex-col bg-background">
      <Header />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar
          onAnalysisSelect={setSelectedAnalysis}
          selectedAnalysis={selectedAnalysis}
        />
        <div className="flex-1 flex flex-col">
          <div className="flex flex-1 overflow-hidden">
            <DocumentPreview
              document={document}
              htmlPreview={htmlPreview}
              onFileUpload={handleFileUpload}
              onClear={handleClear}
              onProcess={handleProcess}
              isProcessing={isProcessing || isConverting}
            />
            <InsightsPanel
              analysisResults={analysisResults}
              analysisType={selectedAnalysis}
            />
          </div>
          <ExtractionsTable extractions={extractions} />
        </div>
      </div>
    </div>
  );
};

export default Index;
