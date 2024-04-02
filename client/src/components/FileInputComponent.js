import React, { useState,useRef } from 'react';
import './styles/FileInputComponent.css';

function FileInputComponent() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedFileExtension, setSelectedFileExtension] = useState(null);
  const [selectedLanguage, setSelectedLanguage] = useState('en'); 
  const [languageFrom, setLanguageFrom] = useState('en'); 
  const [loading, setLoading] = useState(false);
  const abortControllerRef = useRef(null);

  const languageOptions = [
    { value: 'en', label: 'English' },
    { value: 'es', label: 'Spanish' },
    { value: 'fr', label: 'French' },
    { value: 'de', label: 'German' },
    { value: 'it', label: 'Italian' },
    { value: 'ja', label: 'Japanese' },
    { value: 'ko', label: 'Korean' },
    { value: 'ru', label: 'Russian' },
    { value: 'zh-CN', label: 'Chinese (Simplified)' },
    { value: 'ar', label: 'Arabic' },
    { value: 'pt', label: 'Portuguese' },
    { value: 'tr', label: 'Turkish' },
    { value: 'hi', label: 'Hindi' },
    { value: 'vi', label: 'Vietnamese' },
    { value: 'nl', label: 'Dutch' },
    { value: 'sv', label: 'Swedish' },
    { value: 'fi', label: 'Finnish' },
    { value: 'da', label: 'Danish' },
    { value: 'no', label: 'Norwegian' },
    { value: 'pl', label: 'Polish' },
  ];

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);
    setSelectedFileExtension(file ? file.name : null);
  };

  const handleLanguageFromChange = (event) => {
    setLanguageFrom(event.target.value);
  };

  const handleSelectedLanguageChange = (event) => {
    setSelectedLanguage(event.target.value);
  };

  const handleUpload = () => {
    if (selectedFile) {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('languageTo', selectedLanguage);
      formData.append('languageFrom', languageFrom);
      formData.append('fileExtension', selectedFileExtension);
  
      if (languageFrom !== null && selectedLanguage !== null) {
        setLoading(true);
        // Initialize the AbortController
        abortControllerRef.current = new AbortController();
      }
  
      const reader = new FileReader();
  
      reader.onload = (event) => {
        const base64Content = btoa(event.target.result);
        formData.append('fileContent', base64Content);
  
        // Send the request with the file content included
        console.log('FormData before fetch:', formData);
  
        fetch('/convert', {
          method: 'POST',
          body: formData,
          signal: abortControllerRef.current.signal,
        })
          .then(response => {
            console.log('Response inside fetch:', response);
            if (!response.ok) {
              throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.blob();
          })
          .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = selectedFile.name;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
          })
          .catch(error => {
            if (error.name === 'AbortError') {
              console.log('Request aborted');
            } else {
              console.error('Error converting file:', error);
              alert(`Error converting file: ${error.message}`);
            }
          })
          .finally(() => {
            setLoading(false);
          });
      };
  
      reader.readAsBinaryString(selectedFile);
    }
  };
  

  const handleDragOver = (event) => {
    event.preventDefault();
  };

  const handleDrop = (event) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    if (file) {
      setSelectedFile(file);
      setSelectedFileExtension(file.name);
    }
  };

  const stopProcessing = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort(); // Abort the ongoing request
      setLoading(false); // Update loading state
    }
  };

  return (
    <div
      className="file-input-container"
      onDragOver={handleDragOver}
      onDrop={handleDrop}
    >
      <div className='fileInput'>
        <input type="file" id="fileInput" onChange={handleFileChange} accept=".xlsx, .docx, .pptx, .pdf" style={{ display: 'none' }} />
        <label htmlFor="fileInput" className="custom-file-label">
          Browse Your Files
        </label>
        <label className='selectedFile'>
          {selectedFileExtension ? `${selectedFileExtension}` : 'No file selected'}
        </label>
      </div>
      <span className="drag-text">{('or drag a file here')}</span>
      <div className="selectLang">
      <select
        value={languageFrom}
        onChange={handleLanguageFromChange}
      >
        <option value="" disabled>Source Language</option>
        {languageOptions.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>

      <select
        value={selectedLanguage}
        onChange={handleSelectedLanguageChange}
      >
        <option value="" disabled>Destination Language</option>
        {languageOptions.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </div>

    <div className="button-container">
      <button onClick={handleUpload} disabled={loading}>
        {loading ? 'Translating file...' : 'Translate'}
      </button>

      {loading && (
        <div className="loading-container">
          <div className="loading-spinner" onClick={stopProcessing}>
          
          </div>

        </div>
      )}
    </div>
    </div>
  );
}

export default FileInputComponent;
