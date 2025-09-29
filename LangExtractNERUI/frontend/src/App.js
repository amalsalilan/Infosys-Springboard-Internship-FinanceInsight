// import React, { useState } from 'react';
// import axios from 'axios';

// const UploadIcon = () => (
//   <svg className="w-12 h-12 mx-auto text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48" aria-hidden="true">
//     <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
//   </svg>
// );

// function App() {
//   const [file, setFile] = useState(null);
//   const [fileName, setFileName] = useState('');
//   const [extractedText, setExtractedText] = useState('');
//   const [isLoading, setIsLoading] = useState(false);
//   const [error, setError] = useState('');

//   const handleFileChange = (e) => {
//     const selectedFile = e.target.files[0];
//     if (selectedFile) {
//       setFile(selectedFile);
//       setFileName(selectedFile.name);
//       setError('');
//       setExtractedText('');
//     }
//   };

//   const handleSubmit = async (e) => {
//     e.preventDefault();
//     if (!file) {
//       setError('Please select a PDF file to analyze.');
//       return;
//     }

//     setIsLoading(true);
//     setError('');
//     setExtractedText('');

//     const formData = new FormData();
//     formData.append('file', file);

//     try {
//       // This URL points to your Flask backend
//       const response = await axios.post('http://localhost:5000/api/extract-text', formData);
//       setExtractedText(response.data.extractedText);
//     } catch (err) {
//       const errorMessage = err.response ? err.response.data.error : 'Network or server error occurred.';
//       setError(errorMessage);
//     } finally {
//       setIsLoading(false);
//     }
//   };

//   return (
//     <div className="bg-gray-50 min-h-screen flex items-center justify-center p-4">
//       <div className="w-full max-w-2xl bg-white rounded-2xl shadow-lg p-8 space-y-6">

//         <div className="text-center">
//           <h1 className="text-3xl font-bold text-gray-800">DocuExtract AI</h1>
//           <p className="text-gray-500 mt-2">Instantly extract text from any PDF document.</p>
//         </div>

//         <form onSubmit={handleSubmit} className="space-y-6">
//           <div>
//             <label htmlFor="file-upload" className="relative block w-full h-48 border-2 border-gray-300 border-dashed rounded-lg p-6 text-center cursor-pointer hover:border-blue-500 hover:bg-gray-50 transition-colors">
//               <div className="flex flex-col items-center justify-center h-full">
//                 <UploadIcon />
//                 <span className="mt-2 block text-sm font-medium text-gray-900">
//                   {fileName ? fileName : 'Click to upload or drag and drop'}
//                 </span>
//                 <span className="block text-xs text-gray-500">PDF only</span>
//               </div>
//               <input id="file-upload" name="file-upload" type="file" className="sr-only" onChange={handleFileChange} accept=".pdf" />
//             </label>
//           </div>

//           <button
//             type="submit"
//             disabled={isLoading}
//             className="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
//           >
//             {isLoading ? 'Analyzing...' : 'Extract Text'}
//           </button>
//         </form>

//         {error && (
//           <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg relative" role="alert">
//             <strong className="font-bold">Error: </strong>
//             <span className="block sm:inline">{error}</span>
//           </div>
//         )}

//         {extractedText && (
//           <div className="space-y-3">
//             <h2 className="text-xl font-semibold text-gray-800">Extracted Text</h2>
//             <div className="w-full bg-gray-50 rounded-lg p-4 border border-gray-200 max-h-80 overflow-y-auto">
//               <pre className="text-sm text-gray-700 whitespace-pre-wrap font-mono">{extractedText}</pre>
//             </div>
//           </div>
//         )}
//       </div>
//     </div>
//   );
// }

// export default App;

import React, { useState } from 'react';
import axios from 'axios';

const UploadIcon = () => (
  <svg className="w-12 h-12 mx-auto text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
    <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

const ResultCard = ({ title, children }) => (
  <div className="bg-white rounded-lg shadow-md border border-gray-200">
    <h2 className="text-lg font-semibold text-gray-700 p-4 border-b border-gray-200">{title}</h2>
    <div className="p-4 max-h-80 overflow-y-auto">
      {children}
    </div>
  </div>
);

function App() {
  const [file, setFile] = useState(null);
  const [fileName, setFileName] = useState('');
  const [prompt, setPrompt] = useState('');
  const [example, setExample] = useState('');
  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

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
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w.org/2000/svg" fill="none" viewBox="0 0 24 24">
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
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-6 border-t">
            <ResultCard title="SpaCy NER Entities (Visualized)">
              <div className="prose max-w-none" dangerouslySetInnerHTML={{ __html: results.spacy_html }} />
            </ResultCard>
            
            <ResultCard title="LangExtract Entities (Visualized)">
              <div className="prose max-w-none" dangerouslySetInnerHTML={{ __html: results.langextract_html }} />
            </ResultCard>
            
            <ResultCard title="Raw Extracted Text">
              <pre className="whitespace-pre-wrap font-mono text-xs">{results.raw_text}</pre>
            </ResultCard>

            <ResultCard title="LangExtract Entities (JSON)">
              <pre className="whitespace-pre-wrap font-mono text-xs">{JSON.stringify(results.langextract_entities, null, 2)}</pre>
            </ResultCard>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;