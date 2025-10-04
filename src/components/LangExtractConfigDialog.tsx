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
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Plus, Trash2, BookOpen } from "lucide-react";
import { cn } from "@/lib/utils";

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
    onSubmit({
      promptDescription,
      examples,
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
  };

  const isValid = () => {
    if (!promptDescription.trim()) return false;
    if (examples.length === 0) return false;
    return examples.every((ex) => ex.text.trim() && ex.extractions.length > 0);
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

        <div className="space-y-6 py-4">
          {/* Prompt Description */}
          <div className="space-y-2">
            <Label htmlFor="prompt">Extraction Instructions *</Label>
            <Textarea
              id="prompt"
              placeholder="Describe what information you want to extract from the document..."
              value={promptDescription}
              onChange={(e) => setPromptDescription(e.target.value)}
              className="min-h-[100px]"
            />
            <p className="text-xs text-muted-foreground">
              Example: "Extract character names, emotional states, and relationships from the text"
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
              <Label className="text-base">Examples *</Label>
              <Button onClick={addExample} variant="outline" size="sm">
                <Plus className="h-4 w-4 mr-2" />
                Add Example
              </Button>
            </div>

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
                      placeholder="Enter sample text that demonstrates the extraction pattern..."
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
                                placeholder="e.g., character"
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
                                placeholder="e.g., ROMEO"
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
  "text": "<auto-filled from uploaded document>",
  "prompt_description": "User's extraction instructions",
  "examples": [
    {
      "text": "Sample input text",
      "extractions": [
        {
          "extraction_class": "character",
          "extraction_text": "ROMEO",
          "attributes": {
            "emotional_state": "wonder"
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
        </div>

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
        placeholder="Key"
        className="h-7 text-xs flex-1"
      />
      <Input
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Value"
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
