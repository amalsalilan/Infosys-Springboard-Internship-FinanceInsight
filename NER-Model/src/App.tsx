import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Button } from './components/ui/button';
import { Label } from './components/ui/label';
import { Input } from './components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';
import { Textarea } from './components/ui/textarea';
import { Checkbox } from './components/ui/checkbox';
import { Upload, FileText, Loader2, Zap } from 'lucide-react';

type ModelType = 'bert' | 'langchain' | 'spacy' | null;

// --- 1. TYPE DEFINITIONS ---

// Type definition for BERT output (Sentiment Analysis)
type BertAnalysisResult = {
    sentence: string;
    sentiment: 'Positive' | 'Negative' | 'Neutral';
    confidence: number;
};

type BertApiResponse = {
    filename: string;
    total_sentences_processed: number;
    filter_applied: string;
    analysis_results: BertAnalysisResult[];
};

// Type definition for LangExtract output (LLM Extraction)
type ExtractionResult = {
    extraction_class: string;
    extraction_text: string;
    attributes: Record<string, string>;
};

type ExtractionApiResponse = {
    filename: string;
    total_characters_processed: number;
    extraction_results: ExtractionResult[];
};

// Type definition for SpaCy output (Custom NER)
type SpacyExtractionResult = {
    extraction_text: string;
    extraction_class: string;
    start_char: number;
    end_char: number;
};

type SpacyApiResponse = {
    filename: string;
    total_entities_found: number;
    extraction_results: SpacyExtractionResult[];
};


export default function App() {
    // --- 2. STATE INITIALIZATION (Corrected) ---
    const [selectedModel, setSelectedModel] = useState<ModelType>('bert');
    const [uploadedFile, setUploadedFile] = useState<File | null>(null);
    const [isDragging, setIsDragging] = useState(false);

    // BERT config
    const [bertSentiment, setBertSentiment] = useState('all');

    // LangExtract config (Shared slot for LLM-based extraction config)
    const [langExtractApiKey, setLangExtractApiKey] = useState('');
    const [langExtractPrompt, setLangExtractPrompt] = useState('Extract people\'s name, company names, and financial metrics.');
    
    // Processing and Output States
    const [isProcessing, setIsProcessing] = useState(false);
    const [bertOutput, setBertOutput] = useState<BertApiResponse | null>(null);
    const [extractionOutput, setExtractionOutput] = useState<ExtractionApiResponse | null>(null);
    const [spacyOutput, setSpacyOutput] = useState<SpacyApiResponse | null>(null);
    const [error, setError] = useState<string | null>(null);
    
    // --- 3. HANDLER FUNCTIONS ---

    const handleModelSelect = (model: ModelType) => {
        setSelectedModel(model);
        setBertOutput(null);
        setExtractionOutput(null);
        setSpacyOutput(null);
        setError(null);
    };

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        const files = e.dataTransfer.files;
        if (files && files[0]) {
            const file = files[0];
            const validTypes = ['.pdf', '.docx', '.txt'];
            const fileExt = '.' + file.name.split('.').pop()?.toLowerCase();
            if (validTypes.includes(fileExt)) {
                setUploadedFile(file);
                setError(null);
                setBertOutput(null);
                setExtractionOutput(null);
                setSpacyOutput(null);
            } else {
                setError('Invalid file type. Please upload a PDF, DOCX, or TXT file.');
            }
        }
    };

    const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files;
        if (files && files[0]) {
            setUploadedFile(files[0]);
            setError(null);
            setBertOutput(null);
            setExtractionOutput(null);
            setSpacyOutput(null);
        }
    };

    const handleRunModel = async () => {
        if (!uploadedFile) {
            setError('Please upload a document first.');
            return;
        }

        setIsProcessing(true);
        setBertOutput(null);
        setExtractionOutput(null);
        setSpacyOutput(null);
        setError(null);

        const formData = new FormData();
        formData.append('file', uploadedFile);

        let endpoint = '';
        let configKey: 'bertOutput' | 'extractionOutput' | 'spacyOutput' = 'bertOutput';

        // --- Model Execution Logic ---
        if (selectedModel === 'bert') {
            formData.append('sentiment_filter', bertSentiment);
            endpoint = 'http://127.0.0.1:8000/predict_file';
            configKey = 'bertOutput';

        } else if (selectedModel === 'langchain') {
            if (!langExtractApiKey || !langExtractPrompt) {
                 setError('API Key and Extraction Prompt are required for LLM extraction.');
                 setIsProcessing(false);
                 return;
            }
            formData.append('prompt_description', langExtractPrompt);
            formData.append('api_key', langExtractApiKey);
            endpoint = 'http://127.0.0.1:8000/extract_file'; 
            configKey = 'extractionOutput';
        
        } else if (selectedModel === 'spacy') {
            endpoint = 'http://127.0.0.1:8000/predict_spacy'; 
            configKey = 'spacyOutput';

        } else {
            setError(`Processing for ${selectedModel} is not yet implemented.`);
            setIsProcessing(false);
            return;
        }

        // --- Execute API Call ---
        try {
            const response = await fetch(endpoint, { method: 'POST', body: formData });
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'An error occurred during processing.');
            }
            
            // Assign data based on the model that ran
            if (configKey === 'bertOutput') {
                setBertOutput(data as BertApiResponse);
            } else if (configKey === 'extractionOutput') {
                setExtractionOutput(data as ExtractionApiResponse);
            } else if (configKey === 'spacyOutput') {
                setSpacyOutput(data as SpacyApiResponse);
            }

        } catch (err: any) {
            setError(err.message || 'Failed to connect to the backend server. Is it running?');
        } finally {
            setIsProcessing(false);
        }
    };
    
    // --- 4. RENDER HELPERS ---

    const getSentimentClass = (sentiment: string) => {
        if (sentiment === 'Positive') return 'border-green-500 bg-green-500/10 text-green-700 dark:text-green-300';
        if (sentiment === 'Negative') return 'border-red-500 bg-red-500/10 text-red-700 dark:text-red-300';
        return 'border-blue-500 bg-blue-500/10 text-blue-700 dark:text-blue-300';
    };

    const getExtractionClass = (extractionClass: string) => {
        switch(extractionClass.toLowerCase()) {
            case 'person_name': 
            case 'character': return 'border-purple-500 bg-purple-500/10 text-purple-700 dark:text-purple-300';
            case 'company_name': 
            case 'organization': return 'border-orange-500 bg-orange-500/10 text-orange-700 dark:text-orange-300';
            case 'ai_model': 
            case 'product': return 'border-cyan-500 bg-cyan-500/10 text-cyan-700 dark:text-cyan-300';
            default: return 'border-gray-500 bg-gray-500/10 text-gray-700 dark:text-gray-300';
        }
    };
    
    const getSpacyClass = (entityClass: string) => {
        switch(entityClass.toUpperCase()) {
            case 'PERSON': return 'border-blue-500 bg-blue-500/10 text-blue-700 dark:text-blue-300';
            case 'COMPANY': return 'border-orange-500 bg-orange-500/10 text-orange-700 dark:text-orange-300';
            case 'DATE': return 'border-green-500 bg-green-500/10 text-green-700 dark:text-green-300';
            case 'MONEY': return 'border-yellow-500 bg-yellow-500/10 text-yellow-700 dark:text-yellow-300';
            case 'LOCATION': return 'border-red-500 bg-red-500/10 text-red-700 dark:text-red-300';
            default: return 'border-gray-500 bg-gray-500/10 text-gray-700 dark:text-gray-300';
        }
    };

    const renderOutput = () => {
        if (bertOutput) {
            // Render BERT Output (Sentiment Analysis)
            const output = bertOutput;
             return (
                <div className="mt-6 w-full max-w-2xl">
                    <Card>
                        <CardHeader>
                            <CardTitle>BERT Analysis Report for <span className="text-primary">{output.filename}</span></CardTitle>
                            <CardDescription>
                                {output.analysis_results.length} results found (Filter: {output.filter_applied})
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4 max-h-[400px] overflow-y-auto">
                            {output.analysis_results.length > 0 ? (
                                output.analysis_results.map((result, index) => (
                                    <div key={index} className={`p-3 rounded-lg border-l-4 ${getSentimentClass(result.sentiment)}`}>
                                        <p className="font-medium text-sm">"{result.sentence}"</p>
                                        <p className="text-xs text-muted-foreground mt-2">
                                            Sentiment: <span className={`font-bold`}>{result.sentiment}</span> ({result.confidence}%)
                                        </p>
                                    </div>
                                ))
                            ) : (
                                <p className="text-muted-foreground text-center p-4">No sentences matched the filter '{output.filter_applied}'.</p>
                            )}
                        </CardContent>
                    </Card>
                </div>
            );
        }
        
        if (extractionOutput) {
            // Render LangExtract/LLM Extraction Output
            const output = extractionOutput;
            return (
                <div className="mt-6 w-full max-w-2xl">
                    <Card>
                        <CardHeader>
                            <CardTitle>LangExtract Analysis for <span className="text-primary">{output.filename}</span></CardTitle>
                            <CardDescription>
                                {output.extraction_results.length} entities extracted.
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4 max-h-[400px] overflow-y-auto">
                            {output.extraction_results.length > 0 ? (
                                output.extraction_results.map((result, index) => (
                                    <div key={index} className={`p-3 rounded-lg border-l-4 ${getExtractionClass(result.extraction_class)}`}>
                                        <div className="flex justify-between items-start">
                                            <p className="font-semibold text-sm">{result.extraction_text}</p>
                                            <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${getExtractionClass(result.extraction_class)}`}>
                                                {result.extraction_class.replace('_', ' ')}
                                            </span>
                                        </div>
                                        {Object.keys(result.attributes).length > 0 && (
                                            <div className="text-xs text-muted-foreground mt-2 space-y-1">
                                                {Object.entries(result.attributes).map(([key, value]) => (
                                                    <p key={key}><span className="font-medium capitalize">{key}:</span> {value}</p>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                ))
                            ) : (
                                <p className="text-muted-foreground text-center p-4">No entities were extracted.</p>
                            )}
                        </CardContent>
                    </Card>
                </div>
            );
        }

        if (spacyOutput) {
            // Render SpaCy Custom NER Output
            const output = spacyOutput;
            return (
                <div className="mt-6 w-full max-w-2xl">
                    <Card>
                        <CardHeader>
                            <CardTitle>SpaCy Custom NER Report for <span className="text-primary">{output.filename}</span></CardTitle>
                            <CardDescription>
                                {output.total_entities_found} entities found by the custom financial model.
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4 max-h-[400px] overflow-y-auto">
                            {output.extraction_results.length > 0 ? (
                                output.extraction_results.map((result, index) => (
                                    <div key={index} className={`p-3 rounded-lg border-l-4 ${getSpacyClass(result.extraction_class)}`}>
                                        <div className="flex justify-between items-start">
                                            <p className="font-semibold text-sm">{result.extraction_text}</p>
                                            <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${getSpacyClass(result.extraction_class)}`}>
                                                {result.extraction_class.replace('_', ' ')}
                                            </span>
                                        </div>
                                    </div>
                                ))
                            ) : (
                                <p className="text-muted-foreground text-center p-4">No entities were extracted by the custom SpaCy model.</p>
                            )}
                        </CardContent>
                    </Card>
                </div>
            );
        }


        return null;
    };


    // --- 5. COMPONENT STRUCTURE ---
    return (
        <div className="size-full flex flex-col bg-muted/30">
            {/* Header */}
            <div className="bg-card border-b border-border px-8 py-4 flex items-center justify-between">
                <h1 className="text-lg font-semibold">Financial Insight</h1>
                <div className="flex items-center gap-3">
                    <Button variant="ghost">Login</Button>
                    <Button variant="outline">Sign Up</Button>
                    <Button>Get Started</Button>
                </div>
            </div>

            {/* Main Content */}
            <div className="flex flex-1 overflow-hidden">
                {/* Left Sidebar - Model Selection */}
                <div className="w-64 bg-card border-r border-border p-6">
                    <h2 className="text-base font-semibold mb-6">Select Model</h2>
                    <div className="space-y-2">
                        <button
                            onClick={() => handleModelSelect('bert')}
                            className={`w-full p-4 rounded-lg text-left transition-colors ${
                                selectedModel === 'bert'
                                    ? 'bg-primary text-primary-foreground'
                                    : 'bg-secondary hover:bg-secondary/80'
                            }`}
                        >
                            <div>Sentiment Classification</div>
                            <div className="text-sm opacity-80 mt-1">(BERT)</div>
                        </button>

                        <button
                            onClick={() => handleModelSelect('spacy')}
                            className={`w-full p-4 rounded-lg text-left transition-colors ${
                                selectedModel === 'spacy'
                                    ? 'bg-primary text-primary-foreground'
                                    : 'bg-secondary hover:bg-secondary/80'
                            }`}
                        >
                            <div>Custom Entity Recognition</div>
                            <div className="text-sm opacity-80 mt-1">(SpaCy NER)</div>
                        </button>

                        <button
                            onClick={() => handleModelSelect('langchain')}
                            className={`w-full p-4 rounded-lg text-left transition-colors ${
                                selectedModel === 'langchain'
                                    ? 'bg-primary text-primary-foreground'
                                    : 'bg-secondary hover:bg-secondary/80'
                            }`}
                        >
                            <div>LLM Prompt Extraction</div>
                            <div className="text-sm opacity-80 mt-1">(LangExtract)</div>
                        </button>
                    </div>
                </div>

                {/* Center - Document Upload & Output */}
                <div className="flex-1 flex flex-col items-center p-8 overflow-y-auto">
                    <Card className="w-full max-w-2xl">
                        <CardHeader>
                            <CardTitle>Upload Document</CardTitle>
                            <CardDescription>
                                Upload a PDF, DOCX, or TXT file for processing
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div
                                onDragOver={handleDragOver}
                                onDragLeave={handleDragLeave}
                                onDrop={handleDrop}
                                className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
                                    isDragging
                                        ? 'border-primary bg-primary/5'
                                        : 'border-border hover:border-primary/50'
                                }`}
                            >
                                {uploadedFile ? (
                                    <div className="space-y-4">
                                        <FileText className="w-16 h-16 mx-auto text-primary" />
                                        <div>
                                            <p className="mb-2 font-semibold">{uploadedFile.name}</p>
                                            <p className="text-sm text-muted-foreground">
                                                {(uploadedFile.size / 1024).toFixed(2)} KB
                                            </p>
                                        </div>
                                        <Button variant="outline" onClick={() => { setUploadedFile(null); setBertOutput(null); setExtractionOutput(null); setSpacyOutput(null); setError(null); } }>
                                            Remove File
                                        </Button>
                                    </div>
                                ) : (
                                    <div className="space-y-4">
                                        <Upload className="w-16 h-16 mx-auto text-muted-foreground" />
                                        <div>
                                            <p className="mb-2">Drag and drop your document here</p>
                                            <p className="text-sm text-muted-foreground mb-4">
                                                or click the button below to browse
                                            </p>
                                        </div>
                                        <div>
                                            <input
                                                type="file"
                                                id="file-upload"
                                                accept=".pdf,.docx,.txt"
                                                onChange={handleFileInput}
                                                className="hidden"
                                            />
                                            <Button asChild>
                                                <label htmlFor="file-upload" className="cursor-pointer">
                                                    Upload Document
                                                </label>
                                            </Button>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </CardContent>
                    </Card>

                    {/* Error Message */}
                    {error && (
                        <div className="mt-6 w-full max-w-2xl p-4 border rounded-lg bg-destructive/10 text-destructive font-medium text-center">
                            {error}
                        </div>
                    )}

                    {/* Output Area (Renders one of the three model outputs) */}
                    {renderOutput()}

                </div>

                {/* Right Sidebar - Dynamic Configuration */}
                <div className="w-80 bg-card border-l border-border p-6 flex flex-col overflow-hidden">
                    <div className="flex-1 overflow-y-auto">
                        {selectedModel === 'bert' && (
                            <div className="space-y-4">
                                <div>
                                    <Label htmlFor="sentiment-select">Sentiment Filter</Label>
                                    <Select value={bertSentiment} onValueChange={setBertSentiment}>
                                        <SelectTrigger id="sentiment-select" className="mt-2">
                                            <SelectValue />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="all">All Sentiments</SelectItem>
                                            <SelectItem value="positive">Positive Only</SelectItem>
                                            <SelectItem value="negative">Negative Only</SelectItem>
                                            <SelectItem value="neutral">Neutral Only</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>
                                <p className="text-sm text-muted-foreground">
                                    Select which sentiment categories to analyze and display from your document.
                                </p>
                            </div>
                        )}

                        {selectedModel === 'spacy' && (
                            <div className="space-y-4">
                                <h3 className="text-base font-semibold border-b pb-2 mb-4">SpaCy Custom NER</h3>
                                <p className="text-sm text-muted-foreground">
                                    This model uses the **locally-trained SpaCy pipeline** to extract predefined financial entities (e.g., PERSON, COMPANY, MONEY, DATE).
                                </p>
                                <p className="text-xs text-muted-foreground italic">
                                    Requires no additional configuration, just upload your file and run.
                                </p>
                            </div>
                        )}

                        {selectedModel === 'langchain' && (
                            <div className="space-y-4">
                                <h3 className="text-base font-semibold border-b pb-2 mb-4 flex items-center gap-2"><Zap className="w-4 h-4"/> LangExtract Config</h3>
                                
                                <div>
                                    <Label htmlFor="langextract-key">LLM API Key (Required)</Label>
                                    <Input 
                                        id="langextract-key" 
                                        type="password" 
                                        placeholder="Enter Gemini/LLM API Key" 
                                        className="mt-2"
                                        value={langExtractApiKey}
                                        onChange={(e) => setLangExtractApiKey(e.target.value)}
                                    />
                                    <p className="text-xs text-muted-foreground mt-1">Key for cloud-based extraction.</p>
                                </div>
                                
                                <div>
                                    <Label htmlFor="langextract-prompt">Extraction Prompt</Label>
                                    <Textarea
                                        id="langextract-prompt"
                                        placeholder="E.g., Extract all financial metrics and executives..."
                                        rows={5}
                                        className="mt-2"
                                        value={langExtractPrompt}
                                        onChange={(e) => setLangExtractPrompt(e.target.value)}
                                    />
                                    <p className="text-xs text-muted-foreground mt-1">Defines the specific data to extract.</p>
                                </div>
                            </div>
                        )}

                        {!selectedModel && (
                            <p className="text-muted-foreground">
                                Please select a model from the left sidebar to configure options.
                            </p>
                        )}
                    </div>

                    {/* Submit Button */}
                    <div className="pt-6 border-t border-border mt-6">
                        <Button
                            onClick={handleRunModel}
                            className="w-full"
                            size="lg"
                            disabled={!uploadedFile || !selectedModel || isProcessing}
                        >
                            {isProcessing ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Running...</> : 'Run Model'}
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    );
}