import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Header } from './Header';
import { ModelSelection } from './ModelSelection';
import { EntitySelection } from './EntitySelection';
import { FileUpload } from './FileUpload';
import { LoadingButton } from '../ui/LoadingButton';
import { AIModel, EntityType, DashboardState } from '../../types';
import toast from 'react-hot-toast';

export const Dashboard: React.FC = () => {
  const [state, setState] = useState<DashboardState>({
    selectedModel: null,
    selectedEntities: [],
    uploadedFile: null,
  });
  const [langPrompt, setLangPrompt] = useState('');
  const [langExample, setLangExample] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [results, setResults] = useState<any>(null);

  const handleProcess = async () => {
    if (!state.selectedModel) return toast.error('Select an AI model');
    if (!state.uploadedFile) return toast.error('Upload a document');

    if (langPrompt && !langExample.trim()) {
      toast.error('Provide at least one example JSON if prompt is used');
      return;
    }

    setIsProcessing(true);
    try {
      const formData = new FormData();
      formData.append("file", state.uploadedFile);
      formData.append("model", state.selectedModel);
      formData.append("entities", JSON.stringify(state.selectedEntities));

      if (langPrompt) formData.append("langextract_prompt", langPrompt);
      if (langExample) formData.append("langextract_example", langExample);

      const response = await fetch("http://localhost:5000/process", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();
      if (response.ok && !result.error) {
        setResults(result);
        toast.success("Document processed successfully!");
      } else {
        toast.error(result.error || "Processing failed");
      }
    } catch (error: any) {
      toast.error(error.message || "Processing failed");
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="max-w-7xl mx-auto py-8 px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Finance Document Analysis
          </h1>
          <p className="text-gray-600">
            Extract entities, sentiment, and custom LangExtract fields.
          </p>
        </motion.div>

        {/* Selection / Upload Sections */}
        <ModelSelection
          selectedModel={state.selectedModel}
          onModelSelect={m => setState({ ...state, selectedModel: m })}
        />
        <EntitySelection
          selectedEntities={state.selectedEntities}
          onEntityToggle={e =>
            setState(prev => ({
              ...prev,
              selectedEntities: prev.selectedEntities.includes(e)
                ? prev.selectedEntities.filter(x => x !== e)
                : [...prev.selectedEntities, e],
            }))
          }
        />
        <FileUpload
          uploadedFile={state.uploadedFile}
          onFileSelect={f => setState({ ...state, uploadedFile: f })}
          onFileRemove={() => setState({ ...state, uploadedFile: null })}
        />

        {/* LangExtract Input */}
        <div className="mt-8 bg-white p-4 rounded-lg shadow">
          <h3 className="font-semibold mb-2 text-purple-700">🟣 LangExtract Options</h3>

          <label className="block text-sm font-medium mb-1">Prompt Description</label>
          <textarea
            value={langPrompt}
            onChange={e => setLangPrompt(e.target.value)}
            placeholder="Describe what to extract, e.g. 'Extract invoice details such as total, date, vendor name.'"
            className="w-full border rounded-md p-2 mb-4"
            rows={3}
          />

          <label className="block text-sm font-medium mb-1">Example JSON</label>
          <textarea
            value={langExample}
            onChange={e => setLangExample(e.target.value)}
            placeholder={`[
  {
    "text": "Invoice #456 from ACME Corp totaling $1200 issued on March 5, 2023.",
    "extractions": [
      {"field_name": "invoice_number", "value": "456"},
      {"field_name": "vendor", "value": "ACME Corp"},
      {"field_name": "amount", "value": "$1200"},
      {"field_name": "date", "value": "March 5, 2023"}
    ]
  }
]`}
            className="w-full border rounded-md p-2 font-mono"
            rows={8}
          />
        </div>

        {/* Process Button */}
        <div className="flex justify-center mt-6">
          <LoadingButton
            onClick={handleProcess}
            isLoading={isProcessing}
            disabled={!state.selectedModel || !state.uploadedFile}
          >
            {isProcessing ? "Processing..." : "Start Analysis"}
          </LoadingButton>
        </div>

        {/* Results Section */}
        {results && !results.error && (
          <motion.div
            className="mt-10 bg-white shadow-md rounded-xl p-6 space-y-6"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            <h2 className="text-xl font-bold">Results for {results.fileName}</h2>

            {/* Raw Text */}
            <div>
              <h3 className="font-semibold">📄 Extracted Text</h3>
              <pre className="bg-gray-100 p-3 rounded-md whitespace-pre-wrap max-h-64 overflow-y-auto">
                {results.raw_text}
              </pre>
            </div>

            {/* SpaCy NER */}
            <div>
              <h3 className="font-semibold">🟢 SpaCy NER</h3>
              <div
                dangerouslySetInnerHTML={{ __html: results.spacy_html }}
                className="p-3 border rounded-md bg-gray-50"
              />
            </div>

            {/* BERT Sentiment */}
            <div>
              <h3 className="font-semibold">🔵 BERT Sentiment</h3>
              <div
                dangerouslySetInnerHTML={{ __html: results.bert_html }}
                className="p-3 border rounded-md bg-gray-50"
              />
            </div>

            {/* LangExtract Table */}
            {results.langextract_entities && results.langextract_entities.length > 0 && (
              <div>
                <h3 className="font-semibold mt-6 text-purple-700">🟣 LangExtract Table</h3>
                <div className="overflow-x-auto">
                  <table className="min-w-full border border-gray-300 rounded-md">
                    <thead className="bg-gray-100">
                      <tr>
                        <th className="px-4 py-2 border text-left">Field</th>
                        <th className="px-4 py-2 border text-left">Value</th>
                      </tr>
                    </thead>
                    <tbody>
                      {results.langextract_entities.map((entity: any, idx: number) => (
                        <tr key={idx} className="hover:bg-gray-50">
                          <td className="px-4 py-2 border font-medium">{entity.extraction_class}</td>
                          <td className="px-4 py-2 border">{entity.extraction_text}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </motion.div>
        )}
      </main>
    </div>
  );
};
