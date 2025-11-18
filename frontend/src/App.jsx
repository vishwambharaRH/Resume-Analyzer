import { useState } from "react";
import Home from "./components/Home";
import UploadForm from "./components/UploadForm";
import Results from "./components/Results";
import CompareForm from './components/CompareForm';

function App() {
  const [currentView, setCurrentView] = useState("home");
  const [jobData, setJobData] = useState(null);

  const handleUploadSuccess = (data) => {
    console.log("Upload successful:", data);
    setJobData(data);
  };

  return (
    <div className="App">
      {currentView === "home" && <Home onNavigate={setCurrentView} />}
      {currentView === "upload" && (
        <UploadForm
          onNavigate={setCurrentView}
          onUploadSuccess={handleUploadSuccess}
        />
      )}
      {currentView === "results" && (
        <Results onNavigate={setCurrentView} jobData={jobData} />
      )}
      {currentView === "compare" && (
        <CompareForm onNavigate={(view) => setCurrentView(view)} />
      )}
    </div>
  );
}

export default App;
