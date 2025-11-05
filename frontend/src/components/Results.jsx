import { Award, TrendingUp, CheckCircle, Download } from "lucide-react";
import PropTypes from 'prop-types';

const Results = ({ onNavigate}) => {
  // Mock results (replace with real data from jobData later)
  const mockResults = {
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
  };

  const getScoreColor = (score) => {
    if (score >= 85) return "text-green-500";
    if (score >= 70) return "text-blue-500";
    return "text-orange-500";
  };

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

        {/* Overall Score Card */}
        <div className="bg-white rounded-3xl shadow-2xl p-8 mb-8">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-lg mb-2">Overall Resume Score</p>
              <div className="flex items-baseline">
                <span className="text-6xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                  {mockResults.overallScore}
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
                  strokeDashoffset={`${2 * Math.PI * 56 * (1 - mockResults.overallScore / 100)}`}
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
          {Object.entries(mockResults.sections).map(([section, data]) => (
            <div key={section} className="bg-white rounded-2xl shadow-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-gray-800 capitalize">
                  {section}
                </h3>
                <div
                  className={`text-3xl font-bold ${getScoreColor(data.score)}`}
                >
                  {data.score}
                </div>
              </div>
              <div className="space-y-2">
                {data.items.map((item, idx) => (
                  <div key={idx} className="flex items-start">
                    <CheckCircle className="w-4 h-4 text-green-500 mr-2 mt-1 flex-shrink-0" />
                    <span className="text-gray-600 text-sm">{item}</span>
                  </div>
                ))}
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

Results.propTypes = {
  onNavigate: PropTypes.func.isRequired,
  jobData: PropTypes.object,
};

export default Results;
