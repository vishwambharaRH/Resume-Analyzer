/* global FormData */
import { useState } from 'react';
import { Upload, FileText, Loader, TrendingUp } from 'lucide-react';
import axios from 'axios';
import CompareResults from './CompareResults';

const CompareForm = () => {
  const [file, setFile] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError('');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please upload a resume file');
      return;
    }
    
    if (!jobDescription.trim()) {
      setError('Please enter a job description');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('job_description', jobDescription);

      const response = await axios.post(
        'http://localhost:8000/api/v1/compare',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      setResults(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error comparing resume with job description');
    } finally {
      setLoading(false);
    }
  };

  if (results) {
    return <CompareResults results={results} onReset={() => setResults(null)} />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-black bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent mb-4">
            Resume vs Job Match
          </h1>
          <p className="text-gray-600 text-xl">
            Compare your resume with a job description to see your fit percentage
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* File Upload */}
          <div className="bg-white rounded-3xl shadow-2xl p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
              <Upload className="w-7 h-7 text-purple-600" />
              Upload Your Resume
            </h2>
            
            <div className="border-2 border-dashed border-purple-300 rounded-2xl p-8 text-center hover:border-purple-500 transition-colors">
              <input
                type="file"
                accept=".pdf,.docx,.txt"
                onChange={handleFileChange}
                className="hidden"
                id="resume-upload"
              />
              <label
                htmlFor="resume-upload"
                className="cursor-pointer flex flex-col items-center"
              >
                <FileText className="w-16 h-16 text-purple-500 mb-4" />
                <p className="text-lg font-semibold text-gray-700 mb-2">
                  {file ? file.name : 'Click to upload resume'}
                </p>
                <p className="text-sm text-gray-500">
                  PDF, DOCX, or TXT (Max 10MB)
                </p>
              </label>
            </div>
          </div>

          {/* Job Description */}
          <div className="bg-white rounded-3xl shadow-2xl p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
              <FileText className="w-7 h-7 text-purple-600" />
              Job Description
            </h2>
            
            <textarea
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="Paste the job description here... Include required skills, qualifications, and experience."
              className="w-full h-64 p-6 border-2 border-gray-200 rounded-2xl focus:border-purple-500 focus:ring-2 focus:ring-purple-200 outline-none resize-none text-gray-700"
            />
            <p className="text-sm text-gray-500 mt-3">
              💡 Include skills, required experience, and education requirements for best results
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border-2 border-red-200 rounded-2xl p-6 text-red-700">
              {error}
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-purple-600 to-blue-600 text-white py-6 rounded-2xl text-xl font-bold shadow-2xl hover:shadow-purple-500/50 transform hover:scale-105 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3"
          >
            {loading ? (
              <>
                <Loader className="w-6 h-6 animate-spin" />
                Analyzing Match...
              </>
            ) : (
              <>
                <TrendingUp className="w-6 h-6" />
                Compare & Get Fit Score
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

export default CompareForm;