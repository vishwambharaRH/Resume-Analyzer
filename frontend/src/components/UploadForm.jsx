import { useState } from "react";
import { Upload, CheckCircle, AlertCircle} from "lucide-react";
import { useDropzone } from "react-dropzone";
import PropTypes from 'prop-types';
import apiService from "../services/api";

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
        setError("File size exceeds 10MB limit");
      } else {
        setError("Invalid file type. Please upload PDF, DOCX, or TXT");
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
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        [".docx"],
      "text/plain": [".txt"],
    },
    maxSize: 10 * 1024 * 1024,
    multiple: false,
  });

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a file first");
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const response = await apiService.uploadResume(file, (progress) => {
        setUploadProgress(progress);
      });

      console.log("Upload response:", response);

      // Pass job ID to parent
      onUploadSuccess(response);

      // Navigate to results (mock for now)
      setTimeout(() => {
        setUploading(false);
        onNavigate("results");
      }, 1000);
    } catch (err) {
      console.error("Upload error:", err);
      setError(err.message || "Upload failed. Please try again.");
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i];
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 p-8">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <button
            onClick={() => onNavigate("home")}
            className="text-purple-600 hover:text-purple-700 mb-6 inline-flex items-center font-semibold"
          >
            ← Back to Home
          </button>
          <h2 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent mb-4">
            Upload Your Resume
          </h2>
          <p className="text-gray-600">
            Supported formats: PDF, DOCX, TXT (Max 10MB)
          </p>
        </div>

        {/* Upload Area */}
        <div className="bg-white rounded-3xl shadow-2xl p-12 mb-8">
          <div
            {...getRootProps()}
            className={`border-4 border-dashed rounded-2xl p-12 text-center transition-all duration-300 cursor-pointer ${
              isDragActive
                ? "border-purple-500 bg-purple-50 scale-105"
                : file
                  ? "border-green-400 bg-green-50"
                  : "border-gray-300 hover:border-purple-400 hover:bg-purple-50"
            }`}
          >
            <input {...getInputProps()} />

            {file ? (
              <div className="space-y-4">
                <CheckCircle className="w-16 h-16 text-green-500 mx-auto" />
                <div>
                  <p className="text-xl font-semibold text-green-600 mb-2">
                    File Selected!
                  </p>
                  <p className="text-gray-700 font-medium">{file.name}</p>
                  <p className="text-gray-500 text-sm mt-1">
                    {formatFileSize(file.size)}
                  </p>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <Upload className="w-16 h-16 text-gray-400 mx-auto" />
                <div>
                  <p className="text-xl font-semibold text-gray-700 mb-2">
                    {isDragActive
                      ? "Drop your resume here"
                      : "Drag & drop your resume"}
                  </p>
                  <p className="text-purple-600 font-medium">
                    or click to browse
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Error Message */}
          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-xl flex items-start">
              <AlertCircle className="w-5 h-5 text-red-500 mr-3 mt-0.5 flex-shrink-0" />
              <p className="text-red-700">{error}</p>
            </div>
          )}

          {/* Upload Progress */}
          {uploading && (
            <div className="mt-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">
                  Uploading...
                </span>
                <span className="text-sm font-medium text-purple-600">
                  {uploadProgress}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="bg-gradient-to-r from-purple-600 to-blue-600 h-3 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
            </div>
          )}

          {/* Upload Button */}
          {file && !uploading && (
            <button
              onClick={handleUpload}
              className="w-full mt-6 bg-gradient-to-r from-purple-600 to-blue-600 text-white py-4 rounded-2xl text-lg font-semibold shadow-xl hover:shadow-2xl transform hover:scale-105 transition-all duration-300"
            >
              Analyze Resume
            </button>
          )}

          {uploading && (
            <div className="mt-6 flex items-center justify-center text-gray-600">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-purple-600 mr-3"></div>
              Processing your resume...
            </div>
          )}
        </div>

        {/* Info Cards */}
        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-white rounded-2xl p-6 shadow-lg">
            <h4 className="font-semibold text-gray-800 mb-3">
              What we analyze
            </h4>
            <ul className="space-y-2 text-gray-600">
              <li className="flex items-center">
                <CheckCircle className="w-4 h-4 text-green-500 mr-2 flex-shrink-0" />
                Skills & Keywords
              </li>
              <li className="flex items-center">
                <CheckCircle className="w-4 h-4 text-green-500 mr-2 flex-shrink-0" />
                Experience Quality
              </li>
              <li className="flex items-center">
                <CheckCircle className="w-4 h-4 text-green-500 mr-2 flex-shrink-0" />
                Education Details
              </li>
              <li className="flex items-center">
                <CheckCircle className="w-4 h-4 text-green-500 mr-2 flex-shrink-0" />
                Project Descriptions
              </li>
            </ul>
          </div>

          <div className="bg-white rounded-2xl p-6 shadow-lg">
            <h4 className="font-semibold text-gray-800 mb-3">
              Your data is safe
            </h4>
            <ul className="space-y-2 text-gray-600">
              <li className="flex items-center">
                <CheckCircle className="w-4 h-4 text-blue-500 mr-2 flex-shrink-0" />
                Encrypted uploads
              </li>
              <li className="flex items-center">
                <CheckCircle className="w-4 h-4 text-blue-500 mr-2 flex-shrink-0" />
                Auto-deleted after analysis
              </li>
              <li className="flex items-center">
                <CheckCircle className="w-4 h-4 text-blue-500 mr-2 flex-shrink-0" />
                No data retention
              </li>
              <li className="flex items-center">
                <CheckCircle className="w-4 h-4 text-blue-500 mr-2 flex-shrink-0" />
                Privacy guaranteed
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

UploadForm.propTypes = {
  onNavigate: PropTypes.func.isRequired,
  onUploadSuccess: PropTypes.func.isRequired,
};

export default UploadForm;
