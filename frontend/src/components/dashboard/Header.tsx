import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp } from 'lucide-react';

export const Header: React.FC = () => {
  return (
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="bg-white shadow-sm border-b border-gray-200"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="flex items-center">
                <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center mr-3">
                  <TrendingUp className="text-white" size={20} />
                </div>
                <h1 className="text-xl font-bold text-gray-900">Finance Insight NER</h1>
              </div>
            </div>
          </div>

          <div className="flex items-center">
            <span className="text-sm font-medium text-gray-700">
              Welcome to Finance Insight NER
            </span>
          </div>
        </div>
      </div>
    </motion.header>
  );
};