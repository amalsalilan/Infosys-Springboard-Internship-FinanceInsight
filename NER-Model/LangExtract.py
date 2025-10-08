"""
Entity Extraction Model Configuration & Training
Save trained extraction configs for backend deployment
"""

import os
import json
import textwrap
import pickle 
from pathlib import Path 
from datetime import datetime
import langextract as lx

class EntityExtractionModel:
    """Configured entity extraction model for financial documents"""
    
    def __init__(self, api_key=None):
        # NOTE: Using environment variable first, then the provided key, then the placeholder.
        # This MUST be replaced with a real key for the script to run successfully.
        self.api_key = api_key or os.getenv("LANGEXTRACT_API_KEY") 
        
        # Ensure the key is available to the LangExtract library
        if self.api_key:
            os.environ["LANGEXTRACT_API_KEY"] = self.api_key
        
        # Model configuration
        self.model_id = "gemini-2.5-flash"
        self.max_workers = 1
        
        # Define extraction schema - CORRECTED TO INCLUDE 'date'
        self.prompt = textwrap.dedent("""\
            Extract financial entities from the document in order of appearance.
            
            Entity Types:
            - company_name: Any company, corporation, or business entity
            - person_name: Names of executives, analysts, or individuals mentioned
            - financial_metric: Revenue, profit, earnings, stock prices, percentages, growth rates
            - product: Products, services, or product lines
            - location: Geographic locations, markets, regions
            - date: Specific dates or time periods mentioned
            
            Rules:
            1. Use exact text from document (no paraphrasing)
            2. Extract in order of appearance
            3. Provide contextual attributes for each entity
            4. Avoid overlapping extractions
        """)
        
        # Training examples - CORRECTED TO INCLUDE 'date' EXTRACTION
        self.examples = [
            lx.data.ExampleData(
                text=(
                    "Apple Inc reported Q4 revenue of $89.5 billion, a 12% increase. "
                    "CEO Tim Cook announced the new iPhone 15 Pro will launch in Cupertino."
                ),
                extractions=[
                    lx.data.Extraction(
                        extraction_class="company_name",
                        extraction_text="Apple Inc",
                        attributes={"ceo": "Tim Cook", "location": "Cupertino"},
                    ),
                    lx.data.Extraction(
                        extraction_class="financial_metric",
                        extraction_text="$89.5 billion",
                        attributes={"type": "revenue", "period": "Q4"},
                    ),
                    lx.data.Extraction(
                        extraction_class="financial_metric",
                        extraction_text="12%",
                        attributes={"type": "growth_rate"},
                    ),
                    lx.data.Extraction(
                        extraction_class="person_name",
                        extraction_text="Tim Cook",
                        attributes={"title": "CEO", "company": "Apple Inc"},
                    ),
                    lx.data.Extraction(
                        extraction_class="product",
                        extraction_text="iPhone 15 Pro",
                        attributes={"company": "Apple Inc"},
                    ),
                    lx.data.Extraction(
                        extraction_class="location",
                        extraction_text="Cupertino",
                        attributes={"company": "Apple Inc"},
                    ),
                ],
            ),
            lx.data.ExampleData(
                text=(
                    "Tesla missed earnings expectations with EPS of $0.85. "
                    "Analysts at Goldman Sachs downgraded the stock in January 2024."
                ),
                extractions=[
                    lx.data.Extraction(
                        extraction_class="company_name",
                        extraction_text="Tesla",
                    ),
                    lx.data.Extraction(
                        extraction_class="financial_metric",
                        extraction_text="$0.85",
                        attributes={"type": "EPS"},
                    ),
                    lx.data.Extraction(
                        extraction_class="company_name",
                        extraction_text="Goldman Sachs",
                        attributes={"type": "investment_bank"},
                    ),
                    lx.data.Extraction(
                        extraction_class="date",
                        extraction_text="January 2024",
                    ),
                ],
            ),
        ]
        
        # Configuration - CORRECTED TO INCLUDE 'date'
        self.config = {
            "model_id": self.model_id,
            "max_workers": self.max_workers,
            "prompt": self.prompt,
            "entity_classes": [
                "company_name",
                "person_name", 
                "financial_metric",
                "product",
                "location",
                "date" 
            ],
            "version": "1.0.0",
            "created_at": datetime.now().isoformat()
        }
    
    def extract(self, text):
        """Run extraction on input text"""
        if not self.api_key:
            raise Exception("API Key is missing or invalid.")
            
        try:
            result = lx.extract(
                text_or_documents=text,
                prompt_description=self.prompt,
                examples=self.examples,
                model_id=self.model_id,
                max_workers=self.max_workers,
            )
            return self._format_results(result)
        except Exception as e:
            # Propagate a more specific error if needed, but rely on LangExtract's error for now.
            raise Exception(f"Extraction failed: {str(e)}")
    
    def _format_results(self, result):
        """Format extraction results into structured output"""
        formatted = {
            "entities": {},
            "all_extractions": []
        }
        
        for entity_type in self.config["entity_classes"]:
            formatted["entities"][entity_type] = []
        
        for ex in result.extractions:
            try:
                if hasattr(ex.char_interval, 'start') and hasattr(ex.char_interval, 'end'):
                    position = {"start": ex.char_interval.start, "end": ex.char_interval.end}
                elif isinstance(ex.char_interval, (list, tuple)) and len(ex.char_interval) >= 2:
                    position = {"start": ex.char_interval[0], "end": ex.char_interval[1]}
                else:
                    position = {"start": 0, "end": 0}
            except:
                position = {"start": 0, "end": 0}

            entity_data = {
                "text": ex.extraction_text,
                "type": ex.extraction_class,
                "attributes": ex.attributes or {},
                "position": position
            }
            
            if ex.extraction_class in formatted["entities"]:
                formatted["entities"][ex.extraction_class].append(entity_data)
            
            formatted["all_extractions"].append(entity_data)
        
        formatted["summary"] = {
            "total_extractions": len(result.extractions),
            "counts": {
                entity_type: len(formatted["entities"][entity_type])
                for entity_type in self.config["entity_classes"]
            }
        }
        
        return formatted
    
    def save_config(self, filepath="model_config.json"):
        """Save model configuration"""
        config_data = {
            **self.config,
            "examples": [
                {
                    "text": ex.text,
                    "extractions": [
                        {
                            "class": e.extraction_class,
                            "text": e.extraction_text,
                            "attributes": e.attributes
                        }
                        for e in ex.extractions
                    ]
                }
                for ex in self.examples
            ]
        }
        
        # Ensure the prompt description is saved cleanly
        config_data['prompt'] = self.prompt
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Model config saved to: {filepath}")
        return filepath
    
    def load_config(self, filepath="model_config.json"):
        """Load model configuration"""
        with open(filepath, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        self.config = config_data
        self.model_id = config_data["model_id"]
        self.prompt = config_data["prompt"]
        
        print(f"✓ Model config loaded from: {filepath}")
        return self


# Training/Setup Script
def train_and_save_model():
    """Train and save the extraction model"""
    print("="*70)
    print("ENTITY EXTRACTION MODEL TRAINING")
    print("="*70 + "\n")
    
    # Initialize model
    # >>>>>> CRITICAL FIX: REPLACE THE PLACEHOLDER KEY BELOW WITH YOUR REAL KEY <<<<<<
    # The default value "AIzaSyD-JzTTvGVL4uDE5ABFKMJniQBzJm6ZVXg" is a dummy and WILL FAIL.
    api_key_for_setup = os.getenv("LANGEXTRACT_API_KEY", "YOUR_ACTUAL_GEMINI_API_KEY_HERE") 
    
    model = EntityExtractionModel(api_key=api_key_for_setup)
    
    if not model.api_key or model.api_key == "YOUR_ACTUAL_GEMINI_API_KEY_HERE":
         print("✗ ERROR: API Key is missing or is the placeholder value.")
         print("   Please set the LANGEXTRACT_API_KEY environment variable or replace")
         print("   'YOUR_ACTUAL_GEMINI_API_KEY_HERE' in the script with your real key.")
         return

    print("✓ Model initialized")
    print(f"✓ Model: {model.model_id}")
    print(f"✓ Entity classes: {', '.join(model.config['entity_classes'])}")
    print(f"✓ Training examples: {len(model.examples)}\n")
    
    # Test on sample text
    print("─" * 70)
    print("Testing extraction on sample text...")
    print("─" * 70)
    
    test_text = """
    Innovate Corp announced quarterly earnings that surpassed expectations,
    with revenue of $250 million and EPS of $2.50. CEO John Smith stated
    the success was driven by their new CloudPlatform product. The company
    operates primarily in North America and Europe. This was on October 5, 2024.
    """
    
    try:
        results = model.extract(test_text.strip())
        
        print("\n✓ Extraction successful!\n")
        print("Results:")
        print(json.dumps(results["summary"], indent=2))
        
        print("\nSample extractions:")
        for entity_type, entities in results["entities"].items():
            if entities:
                print(f"\n{entity_type.upper()}:")
                for ent in entities[:3]:  # Show first 3
                    print(f"  - {ent['text']}")
        
    except Exception as e:
        print(f"\n✗ Test extraction failed: {e}")
        print("   This means the API call failed, possibly due to an invalid key or network issue.")
        print("   (Model configuration can still be saved)")
    
    # Save model configuration
    print("\n" + "─" * 70)
    print("Saving model configuration...")
    print("─" * 70)
    
    config_file = model.save_config("model_config.json")
    
    # Save metadata
    metadata = {
        "model_version": model.config["version"],
        "created_at": model.config["created_at"],
        "api_provider": "google-gemini",
        "model_id": model.model_id,
        "entity_classes": model.config["entity_classes"],
        "ready_for_deployment": True
    }
    
    with open("model_metadata.json", 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    
    print("✓ Model metadata saved to: model_metadata.json")
    
    print("\n" + "="*70)
    print("✓ MODEL TRAINING COMPLETE!")
    print("="*70)


if __name__ == "__main__":
    train_and_save_model()