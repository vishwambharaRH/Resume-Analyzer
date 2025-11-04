import React from 'react';
import { Award, TrendingUp, CheckCircle, AlertCircle, Download, XCircle } from 'lucide-react';

const Results = ({ onNavigate, jobData }) => {
  // Mock results with validation data
  const mockResults = {
    overallScore: 75,  // Completeness score from backend
    validation: {
      has_all_required: false,
      missing_sections: ['skills'],
      present_sections: ['education', 'experience', 'projects'],
      completeness_score: 75.0
    },
    sections: {
      education: { 
        score: 88, 
        status: 'complete', 
        items: ['BS Computer Science, MIT, 2020'] 
      },
      skills: { 
        score: 0, 
        status: 'missing', 
        items: [] 
      },
      experience: { 
        score: 85, 
        status: 'complete', 
        items: ['Software Engineer, Google, 2020-Present'] 
      },
      projects: { 
        score: 78, 
        status: 'complete', 
        items: ['AI Chatbot using NLP'] 
      }
    },
    strengths: [
      'Resume partially complete',
      '3 out of 4 required sections present',
      'Clear structure and organization'
    ],
    improvements: [
      'Add skills section - CRITICAL',
      'Add quantifiable achievements',
      'Include specific technologies used'
    ]
  };

  const getSectionIcon = (status) => {
    switch(status) {
      case 'complete':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'missing':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'incomplete':
        return <AlertCircle className="w-5 h-5 text-yellow-500" />;
      default:
        return <CheckCircle className="w-5 h-5 text-gray-400" />;
    }
  };

  const getSectionColor = (status) => {
    switch(status) {
      case 'complete':
        return 'border-green-200 bg-green-50';
      case 'missing':
        return 'border-red-200 bg-red-50';
      case 'incomplete':
        return 'border-yellow-200 bg-yellow-50';
      default:
        return 'border-gray-200 bg-white';
    }
  };

  const getScoreColor = (score) => {
    if (score >= 85) return 'text-green-500';
    if (score >= 70) return 'text-blue-500';
    if (score >= 50) return 'text-yellow-500';
    return 'text-red-500';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => onNavigate('upload')}
            className="text-purple-600 hover:text-purple-700 mb-4 inline-flex items-center font-semibold"
          >
            ← Analyze Another Resume
          </button>
          <h2 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
            Analysis Results
          </h2>
        </div>

        {/* Overall Score Card with Validation Status */}
        <div className="bg-white rounded-3xl shadow-2xl p-8 mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <p className="text-gray-600 text-lg mb-2">Resume Completeness Score</p>
              <div className="flex items-baseline">
                <span className={`text-6xl font-bold ${getScoreColor(mockResults.overallScore)}`}>
                  {mockResults.overallScore}
                </span>
                <span className="text-3xl text-gray-400 ml-2">/100</span>
              </div>
              
              {/* Validation Status */}
              {!mockResults.validation.has_all_required && (
                <div className="mt-4 flex items-center text-red-600">
                  <AlertCircle className="w-5 h-5 mr-2" />
                  <span className="font-semibold">
                    {mockResults.validation.missing_sections.length} required section(s) missing
                  </span>
                </div>
              )}
              {mockResults.validation.has_all_required && (
                <div className="mt-4 flex items-center text-green-600">
                  <CheckCircle className="w-5 h-5 mr-2" />
                  <span className="font-semibold">All required sections present!</span>
                </div>
              )}
            </div>
            
            {/* Circular Progress */}
            <div className="relative w-32 h-32">
              <svg className="transform -rotate-90 w-32 h-32">
                <circle
                  cx="64"
                  cy="64"
                  r="56"
                  stroke="#e5e7eb"
                  strokeWidth="12"
                  fill="none"
                />
                <circle
                  cx="64"
                  cy="64"
                  r="56"
                  stroke="url(#gradient)"
                  strokeWidth="12"
                  fill="none"
                  strokeDasharray={`${2 * Math.PI * 56}`}
                  strokeDashoffset={`${2 * Math.PI * 56 * (1 - mockResults.overallScore / 100)}`}
                  strokeLinecap="round"
                />
                <defs>
                  <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#9333ea" />
                    <stop offset="100%" stopColor="#2563eb" />
                  </linearGradient>
                </defs>
              </svg>
            </div>
          </div>

          {/* Missing Sections Alert */}
          {mockResults.validation.missing_sections.length > 0 && (
            <div className="mt-6 p-4 bg-red-50 border-2 border-red-200 rounded-2xl">
              <h4 className="font-bold text-red-800 mb-2 flex items-center">
                <XCircle className="w-5 h-5 mr-2" />
                Missing Sections (Critical)
              </h4>
              <div className="flex flex-wrap gap-2">
                {mockResults.validation.missing_sections.map((section, idx) => (
                  <span 
                    key={idx}
                    className="px-3 py-1 bg-red-200 text-red-800 rounded-full text-sm font-semibold capitalize"
                  >
                    {section}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Section Scores with Status Indicators */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {Object.entries(mockResults.sections).map(([section, data]) => (
            <div 
              key={section} 
              className={`rounded-2xl shadow-lg p-6 border-2 ${getSectionColor(data.status)}`}
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  {getSectionIcon(data.status)}
                  <h3 className="text-xl font-bold text-gray-800 capitalize ml-2">
                    {section}
                  </h3>
                </div>
                <div className={`text-3xl font-bold ${getScoreColor(data.score)}`}>
                  {data.score}
                </div>
              </div>
              
              {data.status === 'missing' && (
                <div className="bg-red-100 border border-red-300 rounded-lg p-3 mb-3">
                  <p className="text-red-800 font-semibold text-sm">
                    ⚠️ This section is required but not found in your resume
                  </p>
                </div>
              )}
              
              <div className="space-y-2">
                {data.items.length > 0 ? (
                  data.items.map((item, idx) => (
                    <div key={idx} className="flex items-start">
                      <CheckCircle className="w-4 h-4 text-green-500 mr-2 mt-1 flex-shrink-0" />
                      <span className="text-gray-600 text-sm">{item}</span>
                    </div>
                  ))
                ) : (
                  <p className="text-gray-500 italic text-sm">No content found</p>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Strengths & Improvements */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
              <Award className="w-6 h-6 text-green-500 mr-2" />
              Strengths
            </h3>
            <ul className="space-y-3">
              {mockResults.strengths.map((strength, idx) => (
                <li key={idx} className="flex items-start">
                  <div className="w-2 h-2 bg-green-500 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  <span className="text-gray-700">{strength}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="bg-white rounded-2xl shadow-lg p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
              <TrendingUp className="w-6 h-6 text-blue-500 mr-2" />
              Areas for Improvement
            </h3>
            <ul className="space-y-3">
              {mockResults.improvements.map((improvement, idx) => (
                <li key={idx} className="flex items-start">
                  <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  <span className="text-gray-700">{improvement}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Download Button */}
        <div className="text-center">
          <button className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-8 py-4 rounded-2xl text-lg font-semibold shadow-xl hover:shadow-2xl transform hover:scale-105 transition-all duration-300 inline-flex items-center">
            <Download className="w-5 h-5 mr-2" />
            Download Full Report (PDF)
          </button>
        </div>
      </div>
    </div>
  );
};

export default Results;
