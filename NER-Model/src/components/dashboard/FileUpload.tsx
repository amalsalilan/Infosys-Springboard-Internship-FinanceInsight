import React, { useCallback, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, File, X, CheckCircle } from 'lucide-react';

interface FileUploadProps {
  uploadedFile: File | null;
  onFileSelect: (file: File) => void;
  onFileRemove: () => void;
}

export const FileUpload: React.FC<FileUploadProps> = ({
  uploadedFile,
  onFileSelect,
  onFileRemove,
}) => {
  const [isDragOver, setIsDragOver] = useState(false);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      onFileSelect(files[0]);
    }
  }, [onFileSelect]);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      onFileSelect(files[0]);
    }
  }, [onFileSelect]);

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-2">3. Upload Document</h2>
        <p className="text-gray-600">Upload the financial document for analysis</p>
      </div>

      <AnimatePresence mode="wait">
        {!uploadedFile ? (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            key="upload"
          >
            <motion.div
              animate={{
                borderColor: isDragOver ? '#3B82F6' : '#D1D5DB',
                backgroundColor: isDragOver ? '#EFF6FF' : '#FAFAFA',
              }}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-gray-400 transition-colors duration-200"
            >
              <motion.div
                animate={{ scale: isDragOver ? 1.1 : 1 }}
                transition={{ duration: 0.2 }}
              >
                <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                <p className="text-lg font-medium text-gray-600 mb-2">
                  Drop your file here, or{' '}
                  <label htmlFor="file-upload" className="text-blue-600 hover:text-blue-700 cursor-pointer">
                    browse
                  </label>
                </p>
                <p className="text-sm text-gray-500">
                  Supports PDF, DOC, DOCX, TXT files up to 10MB
                </p>
              </motion.div>
              
              <input
                id="file-upload"
                type="file"
                className="hidden"
                accept=".pdf,.doc,.docx,.txt"
                onChange={handleFileInput}
              />
            </motion.div>
          </motion.div>
        ) : (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            key="preview"
            className="border border-gray-200 rounded-lg p-4 bg-green-50"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="flex-shrink-0 mr-3">
                  <File className="h-8 w-8 text-green-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">{uploadedFile.name}</p>
                  <p className="text-sm text-gray-500">{formatFileSize(uploadedFile.size)}</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-5 w-5 text-green-600" />
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={onFileRemove}
                  className="text-gray-400 hover:text-red-500 transition-colors duration-200"
                >
                  <X size={20} />
                </motion.button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};