import { TrendingUp, BarChart, Tag, Languages } from "lucide-react";
import { SentimentResponse, NERResponse, LangExtractResponse } from "@/services/api";
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from "recharts";

interface InsightsPanelProps {
  analysisResults: SentimentResponse | NERResponse | LangExtractResponse | null;
  analysisType: "sentiment" | "ner" | "langextract";
}

const InsightsPanel = ({ analysisResults, analysisType }: InsightsPanelProps) => {
  // Sentiment Analysis Chart Data
  const getSentimentChartData = (results: SentimentResponse) => {
    const counts = { positive: 0, negative: 0, neutral: 0 };

    results.sentiment_results.forEach((result) => {
      counts[result.class as keyof typeof counts]++;
    });

    return [
      { name: "Positive", value: counts.positive, color: "#10b981" },
      { name: "Negative", value: counts.negative, color: "#ef4444" },
      { name: "Neutral", value: counts.neutral, color: "#6b7280" },
    ];
  };

  // NER Entity Distribution
  const getNERChartData = (results: NERResponse) => {
    const entityCounts: Record<string, number> = {};

    results.entities.forEach((entity) => {
      entityCounts[entity.entity_group] = (entityCounts[entity.entity_group] || 0) + 1;
    });

    const colors = ["#3b82f6", "#8b5cf6", "#ec4899", "#f59e0b", "#10b981", "#06b6d4"];

    return Object.entries(entityCounts).map(([name, value], index) => ({
      name,
      value,
      color: colors[index % colors.length],
    }));
  };

  // LangExtract Statistics
  const getLangExtractStats = (results: LangExtractResponse) => {
    const classCounts: Record<string, number> = {};

    results.extractions.forEach((extraction) => {
      classCounts[extraction.extraction_class] = (classCounts[extraction.extraction_class] || 0) + 1;
    });

    return classCounts;
  };

  const renderChart = () => {
    if (!analysisResults) {
      return (
        <div className="border-2 border-border p-6 rounded-lg flex flex-col items-center justify-center gap-3 h-64 bg-muted/30">
          <BarChart className="h-10 w-10 text-muted-foreground" />
          <span className="text-foreground font-medium text-sm">
            {analysisType === "sentiment" && "Sentiment Analysis Chart"}
            {analysisType === "ner" && "Entity Distribution Chart"}
            {analysisType === "langextract" && "Extraction Distribution Chart"}
          </span>
          <p className="text-muted-foreground text-xs text-center">
            Upload a document to see {analysisType} distribution
          </p>
        </div>
      );
    }

    if (analysisType === "sentiment") {
      const data = getSentimentChartData(analysisResults as SentimentResponse);
      return (
        <div className="border-2 border-border p-4 rounded-lg h-64 bg-white">
          <h3 className="text-sm font-medium mb-2">Sentiment Distribution</h3>
          <ResponsiveContainer width="100%" height="85%">
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={60}
                fill="#8884d8"
                dataKey="value"
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      );
    }

    if (analysisType === "ner") {
      const data = getNERChartData(analysisResults as NERResponse);
      return (
        <div className="border-2 border-border p-4 rounded-lg h-64 bg-white">
          <h3 className="text-sm font-medium mb-2">Entity Distribution</h3>
          <ResponsiveContainer width="100%" height="85%">
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={60}
                fill="#8884d8"
                dataKey="value"
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      );
    }

    if (analysisType === "langextract") {
      const stats = getLangExtractStats(analysisResults as LangExtractResponse);
      return (
        <div className="border-2 border-border p-4 rounded-lg h-64 bg-white overflow-y-auto">
          <h3 className="text-sm font-medium mb-3">Extraction Classes</h3>
          <div className="space-y-2">
            {Object.entries(stats).map(([className, count]) => (
              <div key={className} className="flex justify-between items-center p-2 bg-muted/30 rounded">
                <span className="text-sm font-medium">{className}</span>
                <span className="text-xs bg-primary text-primary-foreground px-2 py-1 rounded">{count}</span>
              </div>
            ))}
          </div>
        </div>
      );
    }

    return null;
  };

  const renderInsights = () => {
    if (!analysisResults) {
      return (
        <p className="text-sm text-muted-foreground leading-relaxed">
          Analysis results will appear here after processing your document. You'll see key metrics, trends, and extracted information.
        </p>
      );
    }

    if (analysisType === "sentiment") {
      const results = analysisResults as SentimentResponse;
      const total = results.sentiment_results.length;
      const positive = results.sentiment_results.filter((r) => r.class === "positive").length;
      const negative = results.sentiment_results.filter((r) => r.class === "negative").length;
      const neutral = results.sentiment_results.filter((r) => r.class === "neutral").length;

      return (
        <div className="space-y-3">
          <div className="grid grid-cols-3 gap-2 text-center">
            <div className="p-2 bg-green-100 rounded">
              <div className="text-lg font-bold text-green-700">{positive}</div>
              <div className="text-xs text-green-600">Positive</div>
            </div>
            <div className="p-2 bg-red-100 rounded">
              <div className="text-lg font-bold text-red-700">{negative}</div>
              <div className="text-xs text-red-600">Negative</div>
            </div>
            <div className="p-2 bg-gray-100 rounded">
              <div className="text-lg font-bold text-gray-700">{neutral}</div>
              <div className="text-xs text-gray-600">Neutral</div>
            </div>
          </div>
          <p className="text-sm text-muted-foreground">
            Analyzed {total} sentence{total !== 1 ? "s" : ""} from the document.
          </p>
        </div>
      );
    }

    if (analysisType === "ner") {
      const results = analysisResults as NERResponse;
      const total = results.entities.length;
      const avgScore = (
        results.entities.reduce((sum, e) => sum + e.score, 0) / total
      ).toFixed(2);

      return (
        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-2">
            <div className="p-3 bg-blue-50 rounded">
              <div className="text-2xl font-bold text-blue-700">{total}</div>
              <div className="text-xs text-blue-600">Entities Found</div>
            </div>
            <div className="p-3 bg-purple-50 rounded">
              <div className="text-2xl font-bold text-purple-700">{avgScore}</div>
              <div className="text-xs text-purple-600">Avg Confidence</div>
            </div>
          </div>
          <p className="text-sm text-muted-foreground">
            Identified entities include organizations, people, locations, and more.
          </p>
        </div>
      );
    }

    if (analysisType === "langextract") {
      const results = analysisResults as LangExtractResponse;
      const total = results.extractions.length;
      const classes = new Set(results.extractions.map((e) => e.extraction_class)).size;

      return (
        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-2">
            <div className="p-3 bg-indigo-50 rounded">
              <div className="text-2xl font-bold text-indigo-700">{total}</div>
              <div className="text-xs text-indigo-600">Total Extractions</div>
            </div>
            <div className="p-3 bg-pink-50 rounded">
              <div className="text-2xl font-bold text-pink-700">{classes}</div>
              <div className="text-xs text-pink-600">Unique Classes</div>
            </div>
          </div>
          <p className="text-sm text-muted-foreground">
            Extracted structured information using AI language models.
          </p>
        </div>
      );
    }

    return null;
  };

  const getIcon = () => {
    if (analysisType === "sentiment") return <BarChart className="h-4 w-4" />;
    if (analysisType === "ner") return <Tag className="h-4 w-4" />;
    if (analysisType === "langextract") return <Languages className="h-4 w-4" />;
    return <TrendingUp className="h-4 w-4" />;
  };

  return (
    <aside className="w-96 bg-white p-6 flex flex-col gap-6">
      {renderChart()}
      <div className="flex-1 border border-border rounded-lg p-6 flex flex-col gap-4 bg-muted/20">
        <div className="flex items-center gap-2 text-foreground">
          {getIcon()}
          <h3 className="font-medium text-sm">Insights</h3>
        </div>
        {renderInsights()}
      </div>
    </aside>
  );
};

export default InsightsPanel;
