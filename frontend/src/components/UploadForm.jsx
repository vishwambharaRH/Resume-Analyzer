import React, { useState } from 'react';
import { Upload, CheckCircle, AlertCircle, FileText, ArrowLeft, Lock } from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import apiService from '../services/api';

const UploadForm = ({ onNavigate, onUploadSuccess }) => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState(null);

  const onDrop = (acceptedFiles, rejectedFiles) => {
    setError(null);

    if (rejectedFiles.length > 0) {
      const rejection = rejectedFiles[0];
      if (rejection.file.size > 10 * 1024 * 1024) {
        setError('File size exceeds 10MB limit. Please upload a smaller file.');
      } else {
        setError('Invalid file type. Please upload PDF, DOCX, or TXT files only.');
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
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
    },
    maxSize: 10 * 1024 * 1024,
    multiple: false,
  });

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const response = await apiService.uploadResume(file, (progress) => {
        setUploadProgress(progress);
      });

      console.log('Upload response:', response);
      onUploadSuccess(response);
      
      setTimeout(() => {
        setUploading(false);
        onNavigate('results');
      }, 1000);

    } catch (err) {
      console.error('Upload error:', err);
      setError(err.message || 'Upload failed. Please try again.');
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 py-20">
      <div className="container mx-auto px-8 max-w-6xl">
        
        {/* Header - Perfectly Centered */}
        <div className="flex flex-col items-center text-center mb-20">
          <button
            onClick={() => onNavigate('home')}
            className="inline-flex items-center gap-3 text-purple-600 hover:text-purple-700 mb-10 font-semibold text-xl transition-colors duration-200 group"
          >
            <ArrowLeft className="w-6 h-6 group-hover:-translate-x-2 transition-transform duration-200" />
            Back to Home
          </button>
          
          <h2 className="text-6xl md:text-7xl font-black bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent mb-8 tracking-tight">
            Upload Your Resume
          </h2>
          <p className="text-gray-600 text-2xl font-medium">
            Supported formats: PDF, DOCX, TXT • Maximum size: 10MB
          </p>
        </div>

        {/* Upload Area - Larger, Better Centered */}
        <div className="bg-white rounded-[40px] shadow-2xl p-16 mb-16 max-w-4xl mx-auto">
          <div
            {...getRootProps()}
            className={`border-4 border-dashed rounded-[32px] p-20 text-center transition-all duration-300 cursor-pointer ${
              isDragActive
                ? 'border-purple-500 bg-purple-50 scale-[1.02]'
                : file
                ? 'border-green-400 bg-green-50'
                : 'border-gray-300 hover:border-purple-400 hover:bg-purple-50'
            }`}
          >
            <input {...getInputProps()} />
            
            {file ? (
              <div className="space-y-8">
                <CheckCircle className="w-24 h-24 text-green-500 mx-auto" />
                <div className="space-y-5">
                  <p className="text-3xl font-bold text-green-600">
                    File Selected Successfully!
                  </p>
                  <div className="bg-white rounded-3xl p-8 max-w-lg mx-auto shadow-lg border-2 border-green-200">
                    <div className="flex items-center justify-center gap-6">
                      <FileText className="w-10 h-10 text-gray-600" />
                      <div className="text-left">
                        <p className="text-gray-900 font-bold text-xl truncate max-w-sm">
                          {file.name}
                        </p>
                        <p className="text-gray-500 text-base mt-2">
                          {formatFileSize(file.size)}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="space-y-8">
                <Upload className="w-24 h-24 text-gray-400 mx-auto" />
                <div className="space-y-5">
                  <p className="text-3xl font-bold text-gray-800">
                    {isDragActive ? 'Drop your resume here' : 'Drag & drop your resume'}
                  </p>
                  <p className="text-purple-600 font-bold text-xl">
                    or click to browse files
                  </p>
                  <div className="pt-8 space-y-3">
                    <p className="text-gray-600 text-lg">
                      📄 Supported formats: PDF, DOCX, TXT
                    </p>
                    <p className="text-gray-600 text-lg">
                      📏 Maximum size: 10MB
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Error Message */}
          {error && (
            <div className="mt-10 p-8 bg-red-50 border-2 border-red-300 rounded-3xl flex items-start gap-5">
              <AlertCircle className="w-8 h-8 text-red-500 flex-shrink-0 mt-1" />
              <div>
                <p className="text-red-800 font-bold text-xl mb-2">Upload Error</p>
                <p className="text-red-600 text-lg">{error}</p>
              </div>
            </div>
          )}

          {/* Upload Progress */}
          {uploading && (
            <div className="mt-10 space-y-6">
              <div className="flex items-center justify-between">
                <span className="text-gray-800 font-bold text-xl">
                  Uploading and analyzing...
                </span>
                <span className="text-purple-600 font-black text-2xl">
                  {uploadProgress}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-5 overflow-hidden">
                <div
                  className="bg-gradient-to-r from-purple-600 to-blue-600 h-5 rounded-full transition-all duration-300 relative overflow-hidden"
                  style={{ width: `${uploadProgress}%` }}
                >
                  <div className="absolute inset-0 bg-white/20 animate-pulse"></div>
                </div>
              </div>
              <p className="text-center text-gray-600 text-lg flex items-center justify-center gap-3">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-purple-600"></div>
                Processing your resume...
              </p>
            </div>
          )}

          {/* Upload Button */}
          {file && !uploading && (
            <button
              onClick={handleUpload}
              className="w-full mt-10 bg-gradient-to-r from-purple-600 to-blue-600 text-white py-6 rounded-3xl text-2xl font-bold shadow-2xl hover:shadow-purple-500/50 transform hover:scale-[1.02] transition-all duration-300"
            >
              Analyze Resume Now
            </button>
          )}
        </div>

        {/* Info Cards - Centered, Better Spacing */}
        <div className="grid md:grid-cols-2 gap-10 max-w-5xl mx-auto">
          
          {/* What we analyze */}
          <div className="bg-white rounded-[32px] p-10 shadow-xl">
            <div className="flex items-center gap-4 mb-8">
              <div className="w-14 h-14 bg-gradient-to-br from-purple-100 to-purple-200 rounded-2xl flex items-center justify-center">
                <CheckCircle className="w-8 h-8 text-purple-600" />
              </div>
              <h4 className="text-2xl font-bold text-gray-900">
                What We Analyze
              </h4>
            </div>
            <ul className="space-y-5">
              {[
                'Skills & Keywords',
                'Experience Quality',
                'Education Details',
                'Project Descriptions',
                'Missing Sections',
                'Format & Structure'
              ].map((item, idx) => (
                <li key={idx} className="flex items-center gap-4 p-3 rounded-xl hover:bg-purple-50 transition-colors duration-200">
                  <div className="w-3 h-3 bg-green-500 rounded-full flex-shrink-0"></div>
                  <span className="text-gray-700 text-lg font-medium">{item}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Your data is safe */}
          <div className="bg-white rounded-[32px] p-10 shadow-xl">
            <div className="flex items-center gap-4 mb-8">
              <div className="w-14 h-14 bg-gradient-to-br from-blue-100 to-blue-200 rounded-2xl flex items-center justify-center">
                <Lock className="w-8 h-8 text-blue-600" />
              </div>
              <h4 className="text-2xl font-bold text-gray-900">
                Your Data is Safe
              </h4>
            </div>
            <ul className="space-y-5">
              {[
                'Encrypted Uploads (TLS 1.3)',
                'Auto-deleted After Analysis',
                'No Data Retention',
                'Privacy Guaranteed',
                'GDPR Compliant',
                'Secure Processing'
              ].map((item, idx) => (
                <li key={idx} className="flex items-center gap-4 p-3 rounded-xl hover:bg-blue-50 transition-colors duration-200">
                  <div className="w-3 h-3 bg-blue-500 rounded-full flex-shrink-0"></div>
                  <span className="text-gray-700 text-lg font-medium">{item}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

      </div>
    </div>
  );
};

export default UploadForm;