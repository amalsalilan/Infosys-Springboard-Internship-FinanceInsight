import React from 'react';
import { motion } from 'framer-motion';
import { EntityType } from '../../types';

interface EntitySelectionProps {
  selectedEntities: EntityType[];
  onEntityToggle: (entity: EntityType) => void;
}

const entities: { id: EntityType; name: string; description: string }[] = [
  { id: 'company-names', name: 'Company Names', description: 'Extract corporate entity names' },
  { id: 'stock-prices', name: 'Stock Prices', description: 'Identify stock price mentions' },
  { id: 'revenue', name: 'Revenue', description: 'Find revenue figures and data' },
  { id: 'market-cap', name: 'Market Cap', description: 'Extract market capitalization values' },
  { id: 'earnings', name: 'Earnings', description: 'Identify earnings and profit data' },
  { id: 'financial-ratios', name: 'Financial Ratios', description: 'Extract P/E, ROI, and other ratios' },
  { id: 'financial-dates', name: 'Financial Dates', description: 'Find reporting dates and periods' },
  { id: 'financial-statements', name: 'Financial Statements', description: 'Identify statement references' },
  { id: 'phone-number', name: 'Phone Number', description: 'Extract contact information' },
];

export const EntitySelection: React.FC<EntitySelectionProps> = ({
  selectedEntities,
  onEntityToggle,
}) => {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-2">2. Select Entity Types</h2>
        <p className="text-gray-600">Choose the types of entities you want to extract</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {entities.map((entity) => (
          <motion.label
            key={entity.id}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className={`
              flex items-start p-4 rounded-lg border-2 cursor-pointer transition-all duration-200
              ${selectedEntities.includes(entity.id)
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
              }
            `}
          >
            <input
              type="checkbox"
              checked={selectedEntities.includes(entity.id)}
              onChange={() => onEntityToggle(entity.id)}
              className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <div className="ml-3">
              <div className="font-medium text-gray-900 text-sm">{entity.name}</div>
              <div className="text-xs text-gray-500 mt-1">{entity.description}</div>
            </div>
          </motion.label>
        ))}
      </div>

      <div className="mt-4 text-sm text-gray-500">
        {selectedEntities.length} of {entities.length} entity types selected
      </div>
    </div>
  );
};