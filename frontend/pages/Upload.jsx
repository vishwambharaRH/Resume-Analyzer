import React, { useState } from 'react';
import { ArrowLeft, Upload as UploadIcon, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import apiService from '../services/api';

const Upload = ({ onNavigate, onUploadSuccess }) => {
  const [file, setFile] = useState(null);
  const [companyName, setCompanyName] = useState('');
  const [jobTitle, setJobTitle] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [statusText, setStatusText] = useState('');
  const [error, setError] = useState(null);

  const onDrop = (acceptedFiles, rejectedFiles) => {
    setError(null);

    if (rejectedFiles.length > 0) {
      const rejection = rejectedFiles[0];
      if (rejection.file.size > 20 * 1024 * 1024) {
        setError('File size exceeds 20MB limit');
      } else {
        setError('Invalid file type. Please upload PDF only');
      }
      return;
    }

    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
      setError(null);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
    },
    maxSize: 20 * 1024 * 1024,
    multiple: false,
  });

  const formatSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!file) {
      setError('Please select a file first');
      return;
    }

    setUploading(true);
    setError(null);

    try {
      setStatusText('Uploading the file...');
      setUploadProgress(20);

      const response = await apiService.uploadResume(file, (progress) => {
        setUploadProgress(20 + (progress * 0.3)); // 20-50%
      });

      setStatusText('Analyzing your resume...');
      setUploadProgress(60);

      // Simulate analysis progress
      await new Promise(resolve => setTimeout(resolve, 2000));
      setUploadProgress(80);

      setStatusText('Generating feedback...');
      await new Promise(resolve => setTimeout(resolve, 1000));
      setUploadProgress(100);

      onUploadSuccess(response);
      
      setTimeout(() => {
        setUploading(false);
        onNavigate('results');
      }, 500);

    } catch (err) {
      console.error('Upload error:', err);
      setError(err.message || 'Upload failed. Please try again.');
      setUploading(false);
      setUploadProgress(0);
      setStatusText('');
    }
  };

  return (
    <div className="min-h-screen bg-[url('/images/bg-main.svg')] bg-cover bg-gradient-to-b from-purple-50 via-pink-50 to-white">
      {/* Navbar */}
      <nav className="flex items-center justify-between px-10 py-6 max-w-7xl mx-auto">
        <button
          onClick={() => onNavigate('home')}
          className="flex items-center gap-2 text-gray-700 hover:text-gray-900 transition-colors duration-200"
        >
          <ArrowLeft className="w-5 h-5" />
          <span className="font-semibold">Back to Home</span>
        </button>
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-purple-600 to-blue-600 rounded-xl flex items-center justify-center">
            <UploadIcon className="w-6 h-6 text-white" />
          </div>
          <p className="text-2xl font-bold bg-gradient-to-r from-purple-600 via-gray-900 to-blue-600 bg-clip-text text-transparent">
            RESUMIND
          </p>
        </div>
      </nav>

      {/* Main Content */}
      <div className="container mx-auto px-8 py-12 max-w-4xl">
        <div className="text-center mb-12">
          <h1 className="text-6xl font-extrabold mb-6 leading-tight tracking-tight">
            <span className="bg-gradient-to-r from-purple-600 via-gray-900 to-blue-600 bg-clip-text text-transparent">
              Smart Feedback for
            </span>
            <br />
            <span className="bg-gradient-to-r from-purple-600 via-gray-900 to-blue-600 bg-clip-text text-transparent">
              Your Dream Job
            </span>
          </h1>

          {uploading ? (
            <div className="space-y-6">
              <h2 className="text-2xl text-gray-600">{statusText}</h2>
              <div className="flex justify-center">
                <img src="/images/resume-scan.gif" alt="Analyzing" className="w-64 h-64 object-contain" />
              </div>
              <div className="max-w-md mx-auto">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">Processing...</span>
                  <span className="text-sm font-bold text-purple-600">{uploadProgress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className="bg-gradient-to-r from-purple-500 to-blue-500 h-3 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  ></div>
                </div>
              </div>
            </div>
          ) : (
            <h2 className="text-2xl text-gray-600">
              Drop your resume for an ATS score and improvement tips
            </h2>
          )}
        </div>

        {!uploading && (
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* File Upload */}
            <div className="bg-gradient-to-b from-blue-50/30 to-blue-100/30 p-1 rounded-3xl">
              <div
                {...getRootProps()}
                className={`bg-white rounded-3xl p-12 cursor-pointer transition-all duration-300 ${
                  isDragActive
                    ? 'bg-purple-50 border-4 border-dashed border-purple-400'
                    : file
                    ? 'bg-green-50 border-4 border-dashed border-green-400'
                    : 'border-4 border-dashed border-gray-300 hover:border-purple-300 hover:bg-purple-50'
                }`}
              >
                <input {...getInputProps()} />
                
                {file ? (
                  <div className="flex items-center justify-between" onClick={(e) => e.stopPropagation()}>
                    <div className="flex items-center gap-4">
                      <img src="/images/pdf.png" alt="PDF" className="w-12 h-12" />
                      <div>
                        <p className="text-lg font-semibold text-gray-900">{file.name}</p>
                        <p className="text-sm text-gray-500">{formatSize(file.size)}</p>
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        setFile(null);
                      }}
                      className="p-2 hover:bg-red-100 rounded-full transition-colors"
                    >
                      <svg className="w-6 h-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                ) : (
                  <div className="text-center">
                    <div className="flex justify-center mb-6">
                      <div className="w-20 h-20 bg-purple-100 rounded-full flex items-center justify-center">
                        <UploadIcon className="w-10 h-10 text-purple-600" />
                      </div>
                    </div>
                    <p className="text-xl text-gray-700 mb-2">
                      <span className="font-bold text-purple-600">Click to upload</span> or drag and drop
                    </p>
                    <p className="text-gray-500">PDF (max 20MB)</p>
                  </div>
                )}
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="flex items-start gap-3 p-4 bg-red-50 border-2 border-red-200 rounded-2xl">
                <AlertCircle className="w-6 h-6 text-red-500 flex-shrink-0 mt-0.5" />
                <p className="text-red-700 font-medium">{error}</p>
              </div>
            )}

            {/* Optional Fields */}
            <div className="space-y-4">
              <div>
                <label htmlFor="company-name" className="block text-gray-700 font-medium mb-2">
                  Company Name (Optional)
                </label>
                <input
                  type="text"
                  id="company-name"
                  value={companyName}
                  onChange={(e) => setCompanyName(e.target.value)}
                  placeholder="e.g., Google, Microsoft"
                  className="w-full p-4 border-2 border-gray-200 rounded-2xl focus:border-purple-400 focus:outline-none transition-colors"
                />
              </div>

              <div>
                <label htmlFor="job-title" className="block text-gray-700 font-medium mb-2">
                  Job Title (Optional)
                </label>
                <input
                  type="text"
                  id="job-title"
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  placeholder="e.g., Software Engineer"
                  className="w-full p-4 border-2 border-gray-200 rounded-2xl focus:border-purple-400 focus:outline-none transition-colors"
                />
              </div>

              <div>
                <label htmlFor="job-description" className="block text-gray-700 font-medium mb-2">
                  Job Description (Optional)
                </label>
                <textarea
                  id="job-description"
                  rows={5}
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  placeholder="Paste the job description here for better analysis..."
                  className="w-full p-4 border-2 border-gray-200 rounded-2xl focus:border-purple-400 focus:outline-none transition-colors resize-none"
                />
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={!file || uploading}
              className="w-full bg-gradient-to-b from-purple-500 to-purple-700 text-white py-5 rounded-full text-xl font-bold shadow-2xl hover:shadow-purple-500/50 transform hover:scale-[1.02] transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
            >
              Analyze Resume
            </button>
          </form>
        )}
      </div>
    </div>
  );
};

export default Upload;