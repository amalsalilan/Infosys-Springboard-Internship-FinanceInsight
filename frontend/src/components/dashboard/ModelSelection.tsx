import React from 'react';
import { motion } from 'framer-motion';
import { AIModel } from '../../types';

interface ModelSelectionProps {
  selectedModel: AIModel | null;
  onModelSelect: (model: AIModel) => void;
}

const models: { id: AIModel; name: string; description: string }[] = [
  { id: 'langextract', name: 'LangExtract', description: 'Advanced language extraction model' },
  { id: 'spacy', name: 'spaCy', description: 'Industrial-strength NLP library' },
  { id: 'docling', name: 'Docling', description: 'Document processing specialist' },
  { id: 'bert', name: 'BERT/FinBERT', description: 'Financial domain pre-trained model' },
];

export const ModelSelection: React.FC<ModelSelectionProps> = ({
  selectedModel,
  onModelSelect,
}) => {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-2">1. Select AI Model</h2>
        <p className="text-gray-600">Choose the AI model for named entity recognition</p>
      </div>

      <div className="space-y-3">
        {models.map((model) => (
          <motion.label
            key={model.id}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className={`
              flex items-center p-4 rounded-lg border-2 cursor-pointer transition-all duration-200
              ${selectedModel === model.id
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
              }
            `}
          >
            <input
              type="radio"
              name="model"
              value={model.id}
              checked={selectedModel === model.id}
              onChange={() => onModelSelect(model.id)}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
            />
            <div className="ml-3">
              <div className="font-medium text-gray-900">{model.name}</div>
              <div className="text-sm text-gray-500">{model.description}</div>
            </div>
          </motion.label>
        ))}
      </div>
    </div>
  );
};