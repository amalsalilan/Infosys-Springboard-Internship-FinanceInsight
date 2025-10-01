import React, { useState } from 'react';
import axios from 'axios';

// --- Helper Components ---

const UploadIcon = () => (
  <svg className="w-12 h-12 mx-auto text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
    <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

const TabButton = ({ isActive, onClick, children }) => (
    <button
        onClick={onClick}
        className={`py-2 px-4 font-medium text-sm rounded-t-lg transition-colors ${
            isActive
                ? 'border-b-2 border-blue-500 text-blue-600 bg-blue-50'
                : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
        }`}
    >
        {children}
    </button>
);

// --- Main App Component ---

function App() {
  const [file, setFile] = useState(null);
  const [fileName, setFileName] = useState('');
  const [prompt, setPrompt] = useState('');
  const [example, setExample] = useState('');
  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('spacy');

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setFileName(selectedFile.name);
      setError('');
      setResults(null);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a PDF file.');
      return;
    }

    setIsLoading(true);
    setError('');
    setResults(null);
    setActiveTab('spacy'); // Reset to the first tab on new submission

    const formData = new FormData();
    formData.append('file', file);
    if (prompt) formData.append('langextract_prompt', prompt);
    if (example) formData.append('langextract_example', example);

    try {
      const response = await axios.post('http://localhost:5000/api/extract-text', formData);
      setResults(response.data);
    } catch (err) {
      const errorMessage = err.response?.data?.error || 'A network or server error occurred.';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 font-sans p-4 sm:p-6 md:p-8">
      <div className="w-full max-w-6xl mx-auto bg-white rounded-2xl shadow-lg p-8 space-y-8">

        <div className="text-center">
            <h1 className="text-4xl font-bold text-gray-800">Financial Document Analysis</h1>
            <p className="text-gray-500 mt-2">Powered by Docling, SpaCy, and LangExtract</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-6">
                <label htmlFor="file-upload" className="relative block w-full h-full min-h-[150px] border-2 border-gray-300 border-dashed rounded-lg p-6 text-center cursor-pointer hover:border-blue-500 hover:bg-gray-50 transition-colors">
                    <div className="flex flex-col items-center justify-center h-full">
                        <UploadIcon />
                        <span className="mt-2 block text-sm font-medium text-gray-900">{fileName || 'Click to upload or drag and drop'}</span>
                        <span className="block text-xs text-gray-500">PDF Document</span>
                    </div>
                    <input id="file-upload" type="file" className="sr-only" onChange={handleFileChange} accept=".pdf"/>
                </label>
            </div>
            <div className="space-y-6">
                <input
                  type="text"
                  placeholder="Enter LangExtract prompt (e.g., Extract invoice details)"
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  className="w-full border-gray-300 rounded-md shadow-sm p-3 focus:ring-blue-500 focus:border-blue-500 transition"
                />
                <textarea
                  placeholder='Enter Example JSON for LangExtract'
                  value={example}
                  onChange={(e) => setExample(e.target.value)}
                  className="w-full border-gray-300 rounded-md shadow-sm p-3 h-48 focus:ring-blue-500 focus:border-blue-500 transition font-mono text-xs"
                />
            </div>
          </div>
          <button
            type="submit"
            disabled={isLoading}
            className="w-full flex justify-center items-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-base font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all"
          >
            {isLoading ? (
                <>
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w-3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Processing...
                </>
            ) : 'Analyze Document'}
          </button>
        </form>

        {error && <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded-md" role="alert"><p>{error}</p></div>}

        {results && (
          <div className="pt-6 border-t">
            <div className="border-b border-gray-200">
                <nav className="-mb-px flex space-x-6" aria-label="Tabs">
                    <TabButton isActive={activeTab === 'spacy'} onClick={() => setActiveTab('spacy')}>SpaCy Visualizer</TabButton>
                    <TabButton isActive={activeTab === 'langextract_viz'} onClick={() => setActiveTab('langextract_viz')}>LangExtract Visualizer</TabButton>
                    <TabButton isActive={activeTab === 'langextract_table'} onClick={() => setActiveTab('langextract_table')}>LangExtract Table</TabButton>
                    <TabButton isActive={activeTab === 'raw'} onClick={() => setActiveTab('raw')}>Raw Text</TabButton>
                </nav>
            </div>
            
            <div className="mt-4 p-4 bg-gray-50 rounded-lg border max-h-96 overflow-y-auto">
                {activeTab === 'spacy' && <div className="prose max-w-none" dangerouslySetInnerHTML={{ __html: results.spacy_html }} />}
                
                {activeTab === 'langextract_viz' && <div className="prose max-w-none" dangerouslySetInnerHTML={{ __html: results.langextract_html }} />}

                {activeTab === 'langextract_table' && (
                    <table className="min-w-full bg-white divide-y divide-gray-200">
                        <thead className="bg-gray-100">
                            <tr>
                                {/* --- CHANGE 1: Swapped column headers --- */}
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Label</th>
                                {/* --- CHANGE 2: Renamed this column header --- */}
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Extracted Text</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {results.langextract_entities.map((entity, index) => (
                                <tr key={index} className="odd:bg-white even:bg-gray-50">
                                    {/* --- CHANGE 1: Swapped column data --- */}
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{entity.extraction_class}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-800">{String(entity.extraction_text)}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
                
                {activeTab === 'raw' && <pre className="whitespace-pre-wrap font-mono text-xs">{results.raw_text}</pre>}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
