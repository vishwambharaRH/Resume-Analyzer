import { Award, TrendingUp, CheckCircle, Download } from "lucide-react";
import PropTypes from 'prop-types';
import { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import GapIndicator from './GapIndicator';
import WordCountIndicator from './WordCountIndicator';

const Results = ({ onNavigate, jobData }) => {
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(true);

  // Mock results with FR-009 data (fallback)
  const mockResults = useMemo(() => ({
    overallScore: 87,
    sections: {
      skills: {
        score: 92,
        status: "excellent",
        items: ["Python", "React", "FastAPI", "Machine Learning"],
      },
      experience: {
        score: 85,
        status: "good",
        items: ["3+ years as Software Engineer", "Led team of 5 developers"],
      },
      education: {
        score: 88,
        status: "excellent",
        items: ["BS Computer Science", "Stanford University"],
      },
      projects: {
        score: 78,
        status: "good",
        items: ["AI Chatbot", "E-commerce Platform"],
      },
    },
    strengths: [
      "Strong technical skills in modern frameworks",
      "Clear career progression",
      "Relevant industry experience",
    ],
    improvements: [
      "Add quantifiable achievements",
      "Include more project details",
      "Add certifications section",
    ],
    //  FR-009 mock data
    word_count: 450,
    word_count_status: "optimal",
    word_count_feedback: " Perfect! Your resume is 450 words, which is in the optimal range.",
    employment_gaps: [
      {
        gap_start: "Dec 2020",
        gap_end: "Jun 2022",
        gap_months: 18,
        previous_job: "TechCorp",
        next_job: "Google"
      }
    ],
    gap_count: 1,
    gap_feedback: [
      " 18-month gap detected between TechCorp (Dec 2020) and Google (Jun 2022). Consider adding an explanation."
    ]
  }), []);

  // Utility to choose color for section score
  const getScoreColor = (score) => {
    if (score >= 85) return "text-green-500";
    if (score >= 70) return "text-blue-500";
    return "text-orange-500";
  };

  // Fetch results from backend (with polling)
  useEffect(() => {
    if (!jobData?.jobId) {
      // Use mock data if no jobId
      setAnalysisData(mockResults);
      setLoading(false);
      return;
    }

    let stopped = false;

    const fetchResults = async () => {
      try {
        const response = await axios.get(
          `http://localhost:8000/api/v1/results/${jobData.jobId}`
        );
        console.log("✅ API Response:", response.data);
        if (!stopped) {
          setAnalysisData(response.data);
          setLoading(false);
        }
      } catch (error) {
        console.error('Error fetching results:', error);
        if (!stopped) {
          setAnalysisData(mockResults);
          setLoading(false);
        }
      }
    };

    // Poll every 2 seconds for results
    fetchResults();
    const interval =  window.setInterval(fetchResults, 2000);

    return () => {
      stopped = true;
       window.clearInterval(interval);
    };
  }, [jobData, mockResults]);

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-purple-600 mx-auto mb-4"></div>
          <p className="text-xl text-gray-700">Analyzing your resume...</p>
        </div>
      </div>
    );
  }

  // Helper to render a section entry safely based on shape
  const renderSectionContent = (content, fallbackData) => {
    // If backend returned structured object with score & items
    if (content && typeof content === 'object' && ('score' in content || 'items' in content)) {
      const items = Array.isArray(content.items) ? content.items : [];
      return (
        <>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-bold text-gray-800 capitalize">{fallbackData?.title || ''}</h3>
            {typeof content.score === 'number' ? (
              <div className={`text-3xl font-bold ${getScoreColor(content.score)}`}>
                {content.score}
              </div>
            ) : (
              <CheckCircle className="w-6 h-6 text-green-500" />
            )}
          </div>
          <div className="space-y-2">
            {items.length > 0 ? (
              items.map((item, idx) => (
                <div key={idx} className="flex items-start">
                  <CheckCircle className="w-4 h-4 text-green-500 mr-2 mt-1 flex-shrink-0" />
                  <span className="text-gray-600 text-sm">{item}</span>
                </div>
              ))
            ) : (
              <p className="text-gray-600 text-sm">{JSON.stringify(content)}</p>
            )}
          </div>
        </>
      );
    }

    // If content is an array of strings
    if (Array.isArray(content)) {
      return (
        <div className="space-y-2">
          {content.map((item, idx) => (
            <div key={idx} className="flex items-start">
              <CheckCircle className="w-4 h-4 text-green-500 mr-2 mt-1 flex-shrink-0" />
              <span className="text-gray-600 text-sm">{String(item)}</span>
            </div>
          ))}
        </div>
      );
    }

    // If content is a simple string
    if (typeof content === 'string') {
      return <p className="text-gray-600 text-sm">{content}</p>;
    }

    // Fallback to mock fallbackData if available
    if (fallbackData) {
      return (
        <>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-bold text-gray-800 capitalize">{fallbackData.title || ''}</h3>
            {typeof fallbackData.score === 'number' && (
              <div className={`text-3xl font-bold ${getScoreColor(fallbackData.score)}`}>
                {fallbackData.score}
              </div>
            )}
          </div>
          <div className="space-y-2">
            {(fallbackData.items || []).map((item, i) => (
              <div key={i} className="flex items-start">
                <CheckCircle className="w-4 h-4 text-green-500 mr-2 mt-1 flex-shrink-0" />
                <span className="text-gray-600 text-sm">{item}</span>
              </div>
            ))}
          </div>
        </>
      );
    }

    // Ultimate fallback
    return <p className="text-gray-600 text-sm">No section data available</p>;
  };

  // Use the analysisData if it exists, otherwise fallback to mockResults
  const sectionsSource = (analysisData && analysisData.sections && typeof analysisData.sections === 'object')
    ? analysisData.sections
    : mockResults.sections;

  const strengthsSource = Array.isArray(analysisData?.strengths) ? analysisData.strengths : mockResults.strengths;
  const improvementsSource = Array.isArray(analysisData?.improvements) ? analysisData.improvements : mockResults.improvements;

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => onNavigate("upload")}
            className="text-purple-600 hover:text-purple-700 mb-4 inline-flex items-center font-semibold"
          >
            ← Analyze Another Resume
          </button>
          <h2 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
            Analysis Results
          </h2>
        </div>

        {/* Word Count Analysis */}
        {analysisData?.word_count && (
          <WordCountIndicator
            wordAnalysis={{
              word_count: analysisData.word_count,
              word_count_status: analysisData.word_count_status,
              word_count_feedback: analysisData.word_count_feedback,
            }}
          />
        )}

        {/* Employment Gap Analysis */}
        {analysisData?.gap_count !== undefined && (
          <GapIndicator
            gapAnalysis={{
              gap_count: analysisData.gap_count,
              employment_gaps: analysisData.employment_gaps,
              gap_feedback: analysisData.gap_feedback,
            }}
          />
        )}

        {/* Overall Score Card */}
        <div className="bg-white rounded-3xl shadow-2xl p-8 mb-8">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-lg mb-2">Overall Resume Score</p>
              <div className="flex items-baseline">
                <span className="text-6xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                  {analysisData?.overallScore ?? mockResults.overallScore}
                </span>
                <span className="text-3xl text-gray-400 ml-2">/100</span>
              </div>
            </div>
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
                  strokeDashoffset={`${2 * Math.PI * 56 * (1 - ((analysisData?.overallScore ?? mockResults.overallScore) / 100))}`}
                  strokeLinecap="round"
                />
                <defs>
                  <linearGradient
                    id="gradient"
                    x1="0%"
                    y1="0%"
                    x2="100%"
                    y2="100%"
                  >
                    <stop offset="0%" stopColor="#9333ea" />
                    <stop offset="100%" stopColor="#2563eb" />
                  </linearGradient>
                </defs>
              </svg>
            </div>
          </div>
        </div>

        {/* Section Scores */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {Object.entries(sectionsSource).map(([sectionKey, content]) => (
            <div key={sectionKey} className="bg-white rounded-2xl shadow-lg p-6">
              {renderSectionContent(content, { title: sectionKey, ...(mockResults.sections?.[sectionKey] || {}) })}
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
              {strengthsSource.map((strength, idx) => (
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
              {improvementsSource.map((improvement, idx) => (
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
          <a
            href={`http://127.0.0.1:8000/api/v1/download/${jobData?.jobId || '123'}`}
            target="_blank"
            rel="noopener noreferrer"
          >
            <button className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-8 py-4 rounded-2xl text-lg font-semibold shadow-xl hover:shadow-2xl transform hover:scale-105 transition-all duration-300 inline-flex items-center">
              <Download className="w-5 h-5 mr-2" />
              Download Full Report (PDF)
            </button>
          </a>
        </div>
      </div>
    </div>
  );
};

Results.propTypes = {
  onNavigate: PropTypes.func.isRequired,
  jobData: PropTypes.object,
};

export default Results;
