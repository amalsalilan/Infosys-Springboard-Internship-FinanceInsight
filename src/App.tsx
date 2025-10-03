import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Button } from './components/ui/button';
import { Label } from './components/ui/label';
import { Input } from './components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';
import { Textarea } from './components/ui/textarea';
import { Checkbox } from './components/ui/checkbox';
import { Upload, FileText } from 'lucide-react';

type ModelType = 'bert' | 'langchain' | 'spacy' | null;

export default function App() {
  const [selectedModel, setSelectedModel] = useState<ModelType>('bert');
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  
  // BERT config
  const [bertSentiment, setBertSentiment] = useState('all');
  
  // LangChain config
  const [langchainPrompt, setLangchainPrompt] = useState('');
  const [langchainExample, setLangchainExample] = useState('');
  
  // SpaCy config - Entity types
  const [spacyEntityTypes, setSpacyEntityTypes] = useState({
    companyNames: true,
    stockPrices: true,
    revenue: true,
    marketCap: false,
    earnings: false,
    financialRatios: false,
    financialDates: false,
    financialStatements: false,
    phoneNumber: false,
  });

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
      }
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files[0]) {
      setUploadedFile(files[0]);
    }
  };

  const handleRunModel = () => {
    if (!uploadedFile) {
      alert('Please upload a document first');
      return;
    }
    
    const config = selectedModel === 'bert' 
      ? { sentiment: bertSentiment }
      : selectedModel === 'langchain'
      ? { prompt: langchainPrompt, example: langchainExample }
      : { entityTypes: spacyEntityTypes };
    
    console.log('Running model:', selectedModel);
    console.log('File:', uploadedFile.name);
    console.log('Config:', config);
    
    alert(`Model: ${selectedModel}\nFile: ${uploadedFile.name}\nConfiguration applied successfully!`);
  };

  return (
    <div className="size-full flex flex-col bg-muted/30">
      {/* Header */}
      <div className="bg-card border-b border-border px-8 py-4 flex items-center justify-between">
        <h1>Financial Insight</h1>
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
          <h2 className="mb-6">Select Model</h2>
          <div className="space-y-2">
            <button
              onClick={() => setSelectedModel('bert')}
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
              onClick={() => setSelectedModel('langchain')}
              className={`w-full p-4 rounded-lg text-left transition-colors ${
                selectedModel === 'langchain'
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-secondary hover:bg-secondary/80'
              }`}
            >
              <div>Data Extraction</div>
              <div className="text-sm opacity-80 mt-1">(Lang)</div>
            </button>
            
            <button
              onClick={() => setSelectedModel('spacy')}
              className={`w-full p-4 rounded-lg text-left transition-colors ${
                selectedModel === 'spacy'
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-secondary hover:bg-secondary/80'
              }`}
            >
              <div>Entity Recognition</div>
              <div className="text-sm opacity-80 mt-1">(SpaCy)</div>
            </button>
          </div>
        </div>

        {/* Center - Document Upload */}
        <div className="flex-1 flex items-center justify-center p-8">
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
                      <p className="mb-2">{uploadedFile.name}</p>
                      <p className="text-sm text-muted-foreground">
                        {(uploadedFile.size / 1024).toFixed(2)} KB
                      </p>
                    </div>
                    <Button variant="outline" onClick={() => setUploadedFile(null)}>
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
        </div>

        {/* Right Sidebar - Dynamic Configuration */}
        <div className="w-80 bg-card border-l border-border p-6 flex flex-col overflow-hidden">
          <div className="flex-1 overflow-y-auto">
            <h2 className="mb-6">Configuration</h2>
            
            {selectedModel === 'bert' && (
              <div className="space-y-4">
                <div>
                  <Label htmlFor="sentiment-select">Sentiment Filter</Label>
                  <Select value={bertSentiment} onValueChange={setBertSentiment}>
                    <SelectTrigger id="sentiment-select" className="mt-2">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All</SelectItem>
                      <SelectItem value="positive">Positive</SelectItem>
                      <SelectItem value="negative">Negative</SelectItem>
                      <SelectItem value="neutral">Neutral</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <p className="text-sm text-muted-foreground">
                  Select which sentiment categories to analyze in your document.
                </p>
              </div>
            )}
            
            {selectedModel === 'langchain' && (
              <div className="space-y-4">
                <div>
                  <Label htmlFor="prompt-input">Custom Prompt</Label>
                  <Textarea
                    id="prompt-input"
                    placeholder="Enter your extraction prompt..."
                    value={langchainPrompt}
                    onChange={(e) => setLangchainPrompt(e.target.value)}
                    className="mt-2 min-h-32"
                  />
                </div>
                <div>
                  <Label htmlFor="example-input">Example</Label>
                  <Input
                    id="example-input"
                    placeholder='e.g., "Extract all dates, names, and monetary amounts..."'
                    value={langchainExample}
                    onChange={(e) => setLangchainExample(e.target.value)}
                    className="mt-2"
                  />
                  <p className="text-sm text-muted-foreground mt-2">
                    Provide an example to guide the extraction format.
                  </p>
                </div>
              </div>
            )}
            
            {selectedModel === 'spacy' && (
              <div className="space-y-4">
                <div>
                  <Label>Select Entity Types</Label>
                  <p className="text-sm text-muted-foreground mt-1">
                    Choose the types of entities you want to extract
                  </p>
                </div>
                
                <div className="space-y-4 mt-4 max-h-96 overflow-y-auto pr-2">
                  {/* Company Names */}
                  <div className="flex items-start space-x-3">
                    <Checkbox
                      id="companyNames"
                      checked={spacyEntityTypes.companyNames}
                      onCheckedChange={(checked: boolean | "indeterminate") =>
                        setSpacyEntityTypes({ ...spacyEntityTypes, companyNames: checked === true })
                      }
                      className="mt-1"
                    />
                    <div className="flex-1">
                      <label htmlFor="companyNames" className="cursor-pointer block">Company Names</label>
                      <p className="text-sm text-muted-foreground">Extract corporate entity names</p>
                    </div>
                  </div>

                  {/* Stock Prices */}
                  <div className="flex items-start space-x-3">
                    <Checkbox
                      id="stockPrices"
                      checked={spacyEntityTypes.stockPrices}
                      onCheckedChange={(checked: boolean | "indeterminate") =>
                        setSpacyEntityTypes({ ...spacyEntityTypes, stockPrices: checked === true })
                      }
                      className="mt-1"
                    />
                    <div className="flex-1">
                      <label htmlFor="stockPrices" className="cursor-pointer block">Stock Prices</label>
                      <p className="text-sm text-muted-foreground">Identify stock price mentions</p>
                    </div>
                  </div>

                  {/* Revenue */}
                  <div className="flex items-start space-x-3">
                    <Checkbox
                      id="revenue"
                      checked={spacyEntityTypes.revenue}
                      onCheckedChange={(checked: boolean | "indeterminate") =>
                        setSpacyEntityTypes({ ...spacyEntityTypes, revenue: checked === true })
                      }
                      className="mt-1"
                    />
                    <div className="flex-1">
                      <label htmlFor="revenue" className="cursor-pointer block">Revenue</label>
                      <p className="text-sm text-muted-foreground">Find revenue figures and data</p>
                    </div>
                  </div>

                  {/* Market Cap */}
                  <div className="flex items-start space-x-3">
                    <Checkbox
                      id="marketCap"
                      checked={spacyEntityTypes.marketCap}
                      onCheckedChange={(checked: boolean | "indeterminate") =>
                        setSpacyEntityTypes({ ...spacyEntityTypes, marketCap: checked === true })
                      }
                      className="mt-1"
                    />
                    <div className="flex-1">
                      <label htmlFor="marketCap" className="cursor-pointer block">Market Cap</label>
                      <p className="text-sm text-muted-foreground">Extract market capitalization values</p>
                    </div>
                  </div>

                  {/* Earnings */}
                  <div className="flex items-start space-x-3">
                    <Checkbox
                      id="earnings"
                      checked={spacyEntityTypes.earnings}
                      onCheckedChange={(checked: boolean | "indeterminate") =>
                        setSpacyEntityTypes({ ...spacyEntityTypes, earnings: checked === true })
                      }
                      className="mt-1"
                    />
                    <div className="flex-1">
                      <label htmlFor="earnings" className="cursor-pointer block">Earnings</label>
                      <p className="text-sm text-muted-foreground">Identify earnings and profit data</p>
                    </div>
                  </div>

                  {/* Financial Ratios */}
                  <div className="flex items-start space-x-3">
                    <Checkbox
                      id="financialRatios"
                      checked={spacyEntityTypes.financialRatios}
                      onCheckedChange={(checked: boolean | "indeterminate") =>
                        setSpacyEntityTypes({ ...spacyEntityTypes, financialRatios: checked === true })
                      }
                      className="mt-1"
                    />
                    <div className="flex-1">
                      <label htmlFor="financialRatios" className="cursor-pointer block">Financial Ratios</label>
                      <p className="text-sm text-muted-foreground">Extract P/E, ROI, and other ratios</p>
                    </div>
                  </div>

                  {/* Financial Dates */}
                  <div className="flex items-start space-x-3">
                    <Checkbox
                      id="financialDates"
                      checked={spacyEntityTypes.financialDates}
                      onCheckedChange={(checked: boolean | "indeterminate") =>
                        setSpacyEntityTypes({ ...spacyEntityTypes, financialDates: checked === true })
                      }
                      className="mt-1"
                    />
                    <div className="flex-1">
                      <label htmlFor="financialDates" className="cursor-pointer block">Financial Dates</label>
                      <p className="text-sm text-muted-foreground">Find reporting dates and periods</p>
                    </div>
                  </div>

                  {/* Financial Statements */}
                  <div className="flex items-start space-x-3">
                    <Checkbox
                      id="financialStatements"
                      checked={spacyEntityTypes.financialStatements}
                      onCheckedChange={(checked: boolean | "indeterminate") =>
                        setSpacyEntityTypes({ ...spacyEntityTypes, financialStatements: checked === true })
                      }
                      className="mt-1"
                    />
                    <div className="flex-1">
                      <label htmlFor="financialStatements" className="cursor-pointer block">Financial Statements</label>
                      <p className="text-sm text-muted-foreground">Identify statement references</p>
                    </div>
                  </div>

                  {/* Phone Number */}
                  <div className="flex items-start space-x-3">
                    <Checkbox
                      id="phoneNumber"
                      checked={spacyEntityTypes.phoneNumber}
                      onCheckedChange={(checked: boolean | "indeterminate") =>
                        setSpacyEntityTypes({ ...spacyEntityTypes, phoneNumber: checked === true })
                      }
                      className="mt-1"
                    />
                    <div className="flex-1">
                      <label htmlFor="phoneNumber" className="cursor-pointer block">Phone Number</label>
                      <p className="text-sm text-muted-foreground">Extract contact information</p>
                    </div>
                  </div>
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
              disabled={!uploadedFile || !selectedModel}
            >
              Run Model
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
