export type AIModel = 'langextract' | 'spacy' | 'docling' | 'bert';

export type EntityType = 
  | 'company-names'
  | 'stock-prices' 
  | 'revenue'
  | 'market-cap'
  | 'earnings'
  | 'financial-ratios'
  | 'financial-dates'
  | 'financial-statements'
  | 'phone-number';

export interface DashboardState {
  selectedModel: AIModel | null;
  selectedEntities: EntityType[];
  uploadedFile: File | null;
}