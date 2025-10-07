import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Plus, Trash2, BookOpen, FileJson, AlertCircle } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { cn } from "@/lib/utils";

// Default fallback examples for contract-based extraction
const DEFAULT_EXAMPLES: ExtractionExample[] = [
  {
    text: "Either Party may terminate this Agreement with ninety (90) days' prior written notice to the other Party. Upon termination, all outstanding obligations shall be fulfilled, including payment of any amounts due and the return of Confidential Information.",
    extractions: [
      {
        extraction_class: "termination_clause",
        extraction_text: "terminate this Agreement with ninety (90) days' prior written notice",
        attributes: {
          notice_period_days: "90",
          type: "without cause"
        }
      },
      {
        extraction_class: "obligation",
        extraction_text: "all outstanding obligations shall be fulfilled, including payment of any amounts due and the return of Confidential Information",
        attributes: {
          category: "financial_and_confidentiality"
        }
      }
    ]
  },
  {
    text: "This Agreement shall be governed by and construed in accordance with the laws of the State of New York, without regard to its conflict of law provisions. Any disputes arising under this Agreement shall be subject to the exclusive jurisdiction of the courts located in New York County.",
    extractions: [
      {
        extraction_class: "governing_law",
        extraction_text: "governed by and construed in accordance with the laws of the State of New York",
        attributes: {
          jurisdiction: "New York",
          excludes_conflict_provisions: "true"
        }
      },
      {
        extraction_class: "dispute_resolution",
        extraction_text: "disputes arising under this Agreement shall be subject to the exclusive jurisdiction of the courts located in New York County",
        attributes: {
          venue: "New York County",
          type: "exclusive_jurisdiction"
        }
      }
    ]
  }
];

export interface ExtractionExample {
  text: string;
  extractions: Array<{
    extraction_class: string;
    extraction_text: string;
    attributes: Record<string, string>;
  }>;
}

export interface LangExtractConfig {
  promptDescription: string;
  examples: ExtractionExample[];
  modelId: string;
}

interface LangExtractConfigDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (config: LangExtractConfig) => void;
}

const LangExtractConfigDialog = ({ open, onOpenChange, onSubmit }: LangExtractConfigDialogProps) => {
  const [inputMode, setInputMode] = useState<"form" | "json">("form");
  const [promptDescription, setPromptDescription] = useState("");
  const [modelId, setModelId] = useState("gemini-2.0-flash-exp");
  const [examples, setExamples] = useState<ExtractionExample[]>([
    {
      text: "",
      extractions: [
        {
          extraction_class: "",
          extraction_text: "",
          attributes: {},
        },
      ],
    },
  ]);
  const [jsonInput, setJsonInput] = useState("");
  const [jsonError, setJsonError] = useState<string | null>(null);

  const addExample = () => {
    setExamples([
      ...examples,
      {
        text: "",
        extractions: [
          {
            extraction_class: "",
            extraction_text: "",
            attributes: {},
          },
        ],
      },
    ]);
  };

  const removeExample = (index: number) => {
    setExamples(examples.filter((_, i) => i !== index));
  };

  const updateExampleText = (index: number, text: string) => {
    const updated = [...examples];
    updated[index].text = text;
    setExamples(updated);
  };

  const addExtraction = (exampleIndex: number) => {
    const updated = [...examples];
    updated[exampleIndex].extractions.push({
      extraction_class: "",
      extraction_text: "",
      attributes: {},
    });
    setExamples(updated);
  };

  const removeExtraction = (exampleIndex: number, extractionIndex: number) => {
    const updated = [...examples];
    updated[exampleIndex].extractions = updated[exampleIndex].extractions.filter(
      (_, i) => i !== extractionIndex
    );
    setExamples(updated);
  };

  const updateExtraction = (
    exampleIndex: number,
    extractionIndex: number,
    field: "extraction_class" | "extraction_text",
    value: string
  ) => {
    const updated = [...examples];
    updated[exampleIndex].extractions[extractionIndex][field] = value;
    setExamples(updated);
  };

  const addAttribute = (exampleIndex: number, extractionIndex: number, key: string, value: string) => {
    const updated = [...examples];
    updated[exampleIndex].extractions[extractionIndex].attributes[key] = value;
    setExamples(updated);
  };

  const removeAttribute = (exampleIndex: number, extractionIndex: number, key: string) => {
    const updated = [...examples];
    delete updated[exampleIndex].extractions[extractionIndex].attributes[key];
    setExamples(updated);
  };

  const handleSubmit = () => {
    if (inputMode === "json") {
      try {
        const parsed = JSON.parse(jsonInput);

        // Validate JSON structure
        if (!parsed.prompt_description || !Array.isArray(parsed.examples)) {
          setJsonError("JSON must include 'prompt_description' and 'examples' array");
          return;
        }

        // Check if examples are empty or all have empty text - inject fallback
        const hasValidExamples = parsed.examples.length > 0 &&
          parsed.examples.some((ex: any) => ex.text && ex.text.trim().length > 0);

        onSubmit({
          promptDescription: parsed.prompt_description,
          examples: hasValidExamples ? parsed.examples : DEFAULT_EXAMPLES,
          modelId: parsed.model_id || "gemini-2.0-flash-exp",
        });

        // Reset
        setJsonInput("");
        setJsonError(null);
      } catch (error) {
        setJsonError(error instanceof Error ? error.message : "Invalid JSON format");
        return;
      }
    } else {
      // Check if user-provided examples are empty or all have empty text
      const hasValidExamples = examples.length > 0 &&
        examples.some(ex => ex.text && ex.text.trim().length > 0);

      onSubmit({
        promptDescription,
        examples: hasValidExamples ? examples : DEFAULT_EXAMPLES,
        modelId,
      });

      // Reset form
      setPromptDescription("");
      setExamples([
        {
          text: "",
          extractions: [
            {
              extraction_class: "",
              extraction_text: "",
              attributes: {},
            },
          ],
        },
      ]);
    }
  };

  const isValid = () => {
    if (inputMode === "json") {
      return jsonInput.trim().length > 0;
    }
    // Only require prompt description - examples are optional (fallback will be used)
    return promptDescription.trim().length > 0;
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <BookOpen className="h-5 w-5" />
            Configure LangExtract
          </DialogTitle>
          <DialogDescription>
            Define extraction instructions and provide examples. The document text will be automatically populated.
          </DialogDescription>
        </DialogHeader>

        <Tabs value={inputMode} onValueChange={(value) => setInputMode(value as "form" | "json")} className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="form">Form Builder</TabsTrigger>
            <TabsTrigger value="json">
              <FileJson className="h-4 w-4 mr-2" />
              JSON Input
            </TabsTrigger>
          </TabsList>

          <TabsContent value="form" className="space-y-6 py-4">
            {/* Prompt Description */}
            <div className="space-y-2">
              <Label htmlFor="prompt">Extraction Instructions *</Label>
              <Textarea
                id="prompt"
                placeholder="Extract contract parties, values, and key dates from the document"
                value={promptDescription}
                onChange={(e) => setPromptDescription(e.target.value)}
                className="min-h-[100px]"
              />
              <p className="text-xs text-muted-foreground">
                Example: "Extract contract parties, financial amounts, effective dates, and contract durations"
              </p>
            </div>

          {/* Model Selection */}
          <div className="space-y-2">
            <Label htmlFor="model">AI Model</Label>
            <Select value={modelId} onValueChange={setModelId}>
              <SelectTrigger id="model">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="gemini-2.0-flash-exp">Gemini 2.0 Flash (Experimental)</SelectItem>
                <SelectItem value="gemini-1.5-pro">Gemini 1.5 Pro</SelectItem>
                <SelectItem value="gemini-1.5-flash">Gemini 1.5 Flash</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Examples */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <Label className="text-base">Examples (Optional)</Label>
              <Button onClick={addExample} variant="outline" size="sm">
                <Plus className="h-4 w-4 mr-2" />
                Add Example
              </Button>
            </div>
            <p className="text-xs text-muted-foreground">
              If no examples are provided, default contract-based examples will be used automatically.
            </p>

            {examples.map((example, exampleIndex) => (
              <Card key={exampleIndex}>
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm">Example {exampleIndex + 1}</CardTitle>
                    {examples.length > 1 && (
                      <Button
                        onClick={() => removeExample(exampleIndex)}
                        variant="ghost"
                        size="sm"
                        className="h-8 w-8 p-0"
                      >
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                    )}
                  </div>
                  <CardDescription>Provide sample text and expected extractions</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Example Text */}
                  <div className="space-y-2">
                    <Label>Sample Text *</Label>
                    <Textarea
                      placeholder="Alpha Finance Corp. enters into agreement with Beta Holdings for $2,500,000, valid until December 31, 2026..."
                      value={example.text}
                      onChange={(e) => updateExampleText(exampleIndex, e.target.value)}
                      className="min-h-[80px]"
                    />
                  </div>

                  {/* Extractions */}
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <Label className="text-sm">Extractions</Label>
                      <Button
                        onClick={() => addExtraction(exampleIndex)}
                        variant="outline"
                        size="sm"
                      >
                        <Plus className="h-3 w-3 mr-1" />
                        Add Extraction
                      </Button>
                    </div>

                    {example.extractions.map((extraction, extractionIndex) => (
                      <div
                        key={extractionIndex}
                        className="p-3 border rounded-lg space-y-3 bg-muted/30"
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex-1 grid grid-cols-2 gap-2">
                            <div className="space-y-1">
                              <Label className="text-xs">Class</Label>
                              <Input
                                placeholder="party, contract_value, duration"
                                value={extraction.extraction_class}
                                onChange={(e) =>
                                  updateExtraction(
                                    exampleIndex,
                                    extractionIndex,
                                    "extraction_class",
                                    e.target.value
                                  )
                                }
                                className="h-8 text-sm"
                              />
                            </div>
                            <div className="space-y-1">
                              <Label className="text-xs">Text</Label>
                              <Input
                                placeholder="Alpha Finance Corp., $2,500,000"
                                value={extraction.extraction_text}
                                onChange={(e) =>
                                  updateExtraction(
                                    exampleIndex,
                                    extractionIndex,
                                    "extraction_text",
                                    e.target.value
                                  )
                                }
                                className="h-8 text-sm"
                              />
                            </div>
                          </div>
                          {example.extractions.length > 1 && (
                            <Button
                              onClick={() => removeExtraction(exampleIndex, extractionIndex)}
                              variant="ghost"
                              size="sm"
                              className="h-8 w-8 p-0 mt-5"
                            >
                              <Trash2 className="h-3 w-3 text-destructive" />
                            </Button>
                          )}
                        </div>

                        {/* Attributes */}
                        <div className="space-y-2">
                          <Label className="text-xs">Attributes (Optional)</Label>
                          <div className="space-y-2">
                            {Object.entries(extraction.attributes).map(([key, value]) => (
                              <div key={key} className="flex gap-2">
                                <Input
                                  value={key}
                                  disabled
                                  className="h-7 text-xs flex-1"
                                  placeholder="Key"
                                />
                                <Input
                                  value={value}
                                  disabled
                                  className="h-7 text-xs flex-1"
                                  placeholder="Value"
                                />
                                <Button
                                  onClick={() => removeAttribute(exampleIndex, extractionIndex, key)}
                                  variant="ghost"
                                  size="sm"
                                  className="h-7 w-7 p-0"
                                >
                                  <Trash2 className="h-3 w-3" />
                                </Button>
                              </div>
                            ))}
                            <AttributeAdder
                              onAdd={(key, value) =>
                                addAttribute(exampleIndex, extractionIndex, key, value)
                              }
                            />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

            {/* Reference Guide */}
            <Accordion type="single" collapsible className="border rounded-lg">
              <AccordionItem value="reference" className="border-none">
                <AccordionTrigger className="px-4 hover:no-underline">
                  <span className="text-sm font-medium">📖 JSON Format Reference</span>
                </AccordionTrigger>
                <AccordionContent className="px-4 pb-4">
                  <pre className="text-xs bg-muted p-4 rounded-md overflow-x-auto">
                    {`{
  "prompt_description": "Extract contract parties, values, and dates",
  "examples": [
    {
      "text": "Alpha Finance Corp. and Beta Holdings...",
      "extractions": [
        {
          "extraction_class": "party",
          "extraction_text": "Alpha Finance Corp.",
          "attributes": {
            "role": "provider"
          }
        },
        {
          "extraction_class": "contract_value",
          "extraction_text": "$2,500,000",
          "attributes": {
            "currency": "USD"
          }
        }
      ]
    }
  ],
  "model_id": "gemini-2.0-flash-exp"
}`}
                  </pre>
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </TabsContent>

          <TabsContent value="json" className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="json-input">JSON Configuration</Label>
              <Textarea
                id="json-input"
                placeholder={`{
  "prompt_description": "Extract contract parties, financial amounts, and dates",
  "examples": [
    {
      "text": "Alpha Finance Corp. enters into agreement with Beta Holdings for $2,500,000, valid until December 31, 2026.",
      "extractions": [
        {
          "extraction_class": "party",
          "extraction_text": "Alpha Finance Corp.",
          "attributes": {"role": "provider"}
        },
        {
          "extraction_class": "contract_value",
          "extraction_text": "$2,500,000",
          "attributes": {"currency": "USD"}
        },
        {
          "extraction_class": "end_date",
          "extraction_text": "December 31, 2026",
          "attributes": {"type": "contract_expiry"}
        }
      ]
    }
  ],
  "model_id": "gemini-2.0-flash-exp"
}`}
                value={jsonInput}
                onChange={(e) => {
                  setJsonInput(e.target.value);
                  setJsonError(null);
                }}
                className="min-h-[400px] font-mono text-xs"
              />
              <p className="text-xs text-muted-foreground">
                Paste a complete JSON configuration. The "text" field will be auto-filled from your uploaded document.
              </p>
            </div>

            {jsonError && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{jsonError}</AlertDescription>
              </Alert>
            )}

            {/* JSON Reference */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Required JSON Structure</CardTitle>
                <CardDescription>Your JSON must include these fields</CardDescription>
              </CardHeader>
              <CardContent className="space-y-2 text-xs">
                <div>
                  <code className="bg-muted px-1 py-0.5 rounded">prompt_description</code>
                  <span className="text-muted-foreground ml-2">(string) - Extraction instructions</span>
                </div>
                <div>
                  <code className="bg-muted px-1 py-0.5 rounded">examples</code>
                  <span className="text-muted-foreground ml-2">(array) - List of example extractions</span>
                </div>
                <div>
                  <code className="bg-muted px-1 py-0.5 rounded">model_id</code>
                  <span className="text-muted-foreground ml-2">(string, optional) - AI model to use</span>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={handleSubmit} disabled={!isValid()}>
            Extract Information
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

// Helper component for adding attributes
const AttributeAdder = ({ onAdd }: { onAdd: (key: string, value: string) => void }) => {
  const [key, setKey] = useState("");
  const [value, setValue] = useState("");

  const handleAdd = () => {
    if (key.trim() && value.trim()) {
      onAdd(key, value);
      setKey("");
      setValue("");
    }
  };

  return (
    <div className="flex gap-2">
      <Input
        value={key}
        onChange={(e) => setKey(e.target.value)}
        placeholder="role, currency, type"
        className="h-7 text-xs flex-1"
      />
      <Input
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="provider, USD, fiscal_year"
        className="h-7 text-xs flex-1"
      />
      <Button
        onClick={handleAdd}
        variant="secondary"
        size="sm"
        className="h-7 px-2"
        disabled={!key.trim() || !value.trim()}
      >
        <Plus className="h-3 w-3" />
      </Button>
    </div>
  );
};

export default LangExtractConfigDialog;
