// API Service Layer for FinSight Frontend

const API_BASE_URLS = {
  converter: 'http://localhost:8000',
  sentiment: 'http://localhost:8001',
  ner: 'http://localhost:8002',
  langextract: 'http://localhost:8003',
};

// Type Definitions
export interface ConversionResponse {
  success: boolean;
  filename: string;
  format: string;
  markdown: string;
  text: string;
  html: string;
  saved_files?: {
    text: string;
    markdown: string;
    html: string;
  };
}

export interface SentimentResult {
  sentence: string;
  class: string;
  position: {
    start: number;
    end: number;
  };
  confidence_scores: {
    positive: number;
    negative: number;
    neutral: number;
  };
}

export interface SentimentResponse {
  sentiment_results: SentimentResult[];
  highlighted_html?: string;
}

export interface NEREntity {
  entity_group: string;
  score: number;
  word: string;
  start: number;
  end: number;
}

export interface NERResponse {
  success: boolean;
  entities: NEREntity[];
  highlighted_html: string;
  saved_file?: string;
}

export interface Extraction {
  extraction_class: string;
  extraction_text: string;
  attributes: Record<string, string>;
  start_char?: number;
  end_char?: number;
}

export interface LangExtractResponse {
  success: boolean;
  extractions: Extraction[];
  html_visualization: string;
  saved_files?: {
    jsonl: string;
    html: string;
  };
}

// API Functions

/**
 * Convert a document to markdown/text/html
 */
export async function convertDocument(file: File): Promise<ConversionResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URLS.converter}/convert`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to convert document');
  }

  return response.json();
}

/**
 * Analyze sentiment of text and optionally highlight HTML
 */
export async function analyzeSentiment(
  text: string,
  html?: string
): Promise<SentimentResponse> {
  const response = await fetch(`${API_BASE_URLS.sentiment}/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text, html }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to analyze sentiment');
  }

  return response.json();
}

/**
 * Recognize named entities in text
 */
export async function recognizeEntities(text: string): Promise<NERResponse> {
  const response = await fetch(`${API_BASE_URLS.ner}/recognize`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to recognize entities');
  }

  return response.json();
}

/**
 * Extract structured information using LangExtract
 */
export async function extractInformation(
  text: string,
  promptDescription: string,
  examples: Array<{
    text: string;
    extractions: Array<{
      extraction_class: string;
      extraction_text: string;
      attributes: Record<string, string>;
    }>;
  }>,
  modelId: string = 'gemini-2.0-flash-exp'
): Promise<LangExtractResponse> {
  const response = await fetch(`${API_BASE_URLS.langextract}/extract`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      text,
      prompt_description: promptDescription,
      examples,
      model_id: modelId,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to extract information');
  }

  return response.json();
}

/**
 * Complete workflow: Convert document and run analysis based on type
 */
export async function processDocument(
  file: File,
  analysisType: 'sentiment' | 'ner' | 'langextract'
): Promise<{
  conversion: ConversionResponse;
  analysis: SentimentResponse | NERResponse | LangExtractResponse;
}> {
  // Step 1: Convert document
  const conversion = await convertDocument(file);

  // Step 2: Run appropriate analysis
  let analysis: SentimentResponse | NERResponse | LangExtractResponse;

  switch (analysisType) {
    case 'sentiment':
      analysis = await analyzeSentiment(conversion.text, conversion.html);
      break;

    case 'ner':
      analysis = await recognizeEntities(conversion.text);
      break;

    case 'langextract':
      // Default financial document extraction
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
      break;

    default:
      throw new Error(`Unknown analysis type: ${analysisType}`);
  }

  return { conversion, analysis };
}

/**
 * Health check for all services
 */
export async function checkServicesHealth(): Promise<Record<string, { status: string; model_loaded?: boolean }>> {
  const services = ['converter', 'sentiment', 'ner', 'langextract'] as const;
  const healthChecks: Record<string, { status: string; model_loaded?: boolean }> = {};

  await Promise.all(
    services.map(async (service) => {
      try {
        const response = await fetch(`${API_BASE_URLS[service]}/health`);
        healthChecks[service] = await response.json();
      } catch (error) {
        healthChecks[service] = { status: 'unavailable' };
      }
    })
  );

  return healthChecks;
}
