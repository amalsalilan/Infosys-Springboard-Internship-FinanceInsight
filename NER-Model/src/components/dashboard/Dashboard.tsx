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
  const [isProcessing, setIsProcessing] = useState(false);

  const handleModelSelect = (model: AIModel) => {
    setState(prev => ({ ...prev, selectedModel: model }));
    toast.success(`${model.toUpperCase()} model selected`);
  };

  const handleEntityToggle = (entity: EntityType) => {
    setState(prev => ({
      ...prev,
      selectedEntities: prev.selectedEntities.includes(entity)
        ? prev.selectedEntities.filter(e => e !== entity)
        : [...prev.selectedEntities, entity],
    }));
  };

  const handleFileSelect = (file: File) => {
    setState(prev => ({ ...prev, uploadedFile: file }));
    toast.success('File uploaded successfully');
  };

  const handleFileRemove = () => {
    setState(prev => ({ ...prev, uploadedFile: null }));
  };

  const handleProcess = async () => {
    if (!state.selectedModel) {
      toast.error('Please select an AI model');
      return;
    }
    if (state.selectedEntities.length === 0) {
      toast.error('Please select at least one entity type');
      return;
    }
    if (!state.uploadedFile) {
      toast.error('Please upload a document');
      return;
    }

    setIsProcessing(true);
    try {
      // Simulate processing
      await new Promise(resolve => setTimeout(resolve, 3000));
      toast.success('Document processed successfully!');
    } catch (error) {
      toast.error('Processing failed. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const isReadyToProcess = state.selectedModel && state.selectedEntities.length > 0 && state.uploadedFile;

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Finance Document Analysis
          </h1>
          <p className="text-gray-600">
            Extract named entities from financial documents using AI models
          </p>
        </motion.div>

        <div className="space-y-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <ModelSelection
              selectedModel={state.selectedModel}
              onModelSelect={handleModelSelect}
            />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <EntitySelection
              selectedEntities={state.selectedEntities}
              onEntityToggle={handleEntityToggle}
            />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <FileUpload
              uploadedFile={state.uploadedFile}
              onFileSelect={handleFileSelect}
              onFileRemove={handleFileRemove}
            />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="flex justify-center"
          >
            <div className="w-full max-w-md">
              <LoadingButton
                onClick={handleProcess}
                isLoading={isProcessing}
                disabled={!isReadyToProcess}
              >
                {isProcessing ? 'Processing Document...' : 'Start Analysis'}
              </LoadingButton>
            </div>
          </motion.div>
        </div>
      </main>
    </div>
  );
};