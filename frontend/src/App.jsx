import React, { useState } from 'react';
import Home from '../pages/Home';
import Upload from '../pages/Upload';
import Results from '../pages/Results';

function App() {
  const [currentView, setCurrentView] = useState('home'); // home, upload, results
  const [jobData, setJobData] = useState(null);

  const handleUploadSuccess = (data) => {
    console.log('Upload successful:', data);
    setJobData(data);
  };

  return (
    <div className="App">
      {currentView === 'home' && <Home onNavigate={setCurrentView} />}
      {currentView === 'upload' && (
        <Upload 
          onNavigate={setCurrentView} 
          onUploadSuccess={handleUploadSuccess}
        />
      )}
      {currentView === 'results' && (
        <Results 
          onNavigate={setCurrentView} 
          jobData={jobData}
        />
      )}
    </div>
  );
}

export default App;