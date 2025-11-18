import { ArrowLeft, CheckCircle, XCircle, TrendingUp, Award } from 'lucide-react';
import PropTypes from 'prop-types';

const CompareResults = ({ results, onReset }) => {
  // [DRA-62 FIX]
  // 1. We now read 'overall_score' and 'overall_suggestions' from the results
  const {
    fit_percentage,
    overall_score, // This is your new score (e.g., 57)
    fit_category,
    matched_skills,
    missing_skills,
    skill_match_percentage,
    experience_match_percentage,
    education_match_percentage,
    recommendations,
    overall_suggestions, // The new suggestions from FeedbackGenerator
    explanation
  } = results;

  // [DRA-62 FIX]
  // 2. We set the main score to your new 'overall_score'.
  //    We default to 'fit_percentage' just in case the new score isn't sent.
  const mainScore = Math.round(overall_score || fit_percentage || 0);

  // [DRA-62 FIX]
  // 3. All color logic now uses the new 'mainScore'
  const getFitColor = () => {
    if (mainScore >= 80) return 'text-green-500';
    if (mainScore >= 60) return 'text-blue-500';
    if (mainScore >= 40) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getCategoryColor = () => {
    if (mainScore >= 80) return 'bg-green-50 border-green-200 text-green-700';
    if (mainScore >= 60) return 'bg-blue-50 border-blue-200 text-blue-700';
    if (mainScore >= 40) return 'bg-yellow-50 border-yellow-200 text-yellow-700';
    return 'bg-red-50 border-red-200 text-red-700';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={onReset}
            className="text-purple-600 hover:text-purple-700 mb-4 inline-flex items-center font-semibold text-lg"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            Compare Another Resume
          </button>
          <h2 className="text-5xl font-black bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent mb-4">
            Match Results
          </h2>
        </div>

        {/* Overall Fit Score */}
        <div className="bg-white rounded-3xl shadow-2xl p-8 mb-8">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <p className="text-gray-600 text-lg mb-2">Overall Job Fit</p>
              <div className="flex items-baseline gap-4 mb-4">
                <span className={`text-7xl font-black ${getFitColor()}`}>
                  {/* [DRA-62 FIX] 4. Display the new 'mainScore' */}
                  {mainScore}%
                </span>
                <span className={`px-6 py-3 rounded-2xl border-2 text-xl font-bold ${getCategoryColor()}`}>
                  {/* We can still use fit_category, or create new logic */}
                  {fit_category}
                </span>
              </div>
              <p className="text-gray-700 text-lg leading-relaxed">
                {explanation}
              </p>
            </div>
            
            {/* Circular Progress */}
            <div className="relative w-48 h-48">
              <svg className="transform -rotate-90 w-48 h-48">
                <circle
                  cx="96"
                  cy="96"
                  r="80"
                  stroke="#e5e7eb"
                  strokeWidth="16"
                  fill="none"
                />
                <circle
                  cx="96"
                  cy="96"
                  r="80"
                  // [DRA-62 FIX] 5. Use 'mainScore' for the circle color
                  stroke={mainScore >= 80 ? '#22c55e' : mainScore >= 60 ? '#3b82f6' : mainScore >= 40 ? '#eab308' : '#ef4444'}
                  strokeWidth="16"
                  fill="none"
                  strokeDasharray={`${2 * Math.PI * 80}`}
                  // [DRA-62 FIX] 6. Use 'mainScore' for the circle fill amount
                  strokeDashoffset={`${2 * Math.PI * 80 * (1 - mainScore / 100)}`}
                  strokeLinecap="round"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <Award className="w-16 h-16 text-purple-600" />
              </div>
            </div>
          </div>
        </div>

        {/* Breakdown Scores */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <h3 className="text-lg font-bold text-gray-800 mb-2">Skills Match</h3>
            <div className="flex items-baseline">
              <span className="text-4xl font-bold text-purple-600">{skill_match_percentage}%</span>
              <span className="text-gray-500 ml-2">(60% weight)</span>
            </div>
          </div>
          
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <h3 className="text-lg font-bold text-gray-800 mb-2">Experience Match</h3>
            <div className="flex items-baseline">
              <span className="text-4xl font-bold text-blue-600">{experience_match_percentage}%</span>
              <span className="text-gray-500 ml-2">(20% weight)</span>
            </div>
          </div>
          
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <h3 className="text-lg font-bold text-gray-800 mb-2">Education Match</h3>
            <div className="flex items-baseline">
              <span className="text-4xl font-bold text-green-600">{education_match_percentage}%</span>
              <span className="text-gray-500 ml-2">(20% weight)</span>
            </div>
          </div>
        </div>

        {/* Skills Breakdown */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {/* Matched Skills */}
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
              <CheckCircle className="w-6 h-6 text-green-500 mr-2" />
              Matched Skills ({matched_skills.length})
            </h3>
            {matched_skills.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {matched_skills.map((skill, idx) => (
                  <span
                    key={idx}
                    className="px-4 py-2 bg-green-50 text-green-700 rounded-full text-sm font-semibold border-2 border-green-200"
                  >
                    ✓ {skill}
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-gray-500">No skills matched</p>
            )}
          </div>

          {/* Missing Skills */}
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
              <XCircle className="w-6 h-6 text-red-500 mr-2" />
              Missing Skills ({missing_skills.length})
            </h3>
            {missing_skills.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {missing_skills.map((skill, idx) => (
                  <span
                    key={idx}
                    className="px-4 py-2 bg-red-50 text-red-700 rounded-full text-sm font-semibold border-2 border-red-200"
                  >
                    ✗ {skill}
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-gray-500">All required skills are present! 🎉</p>
            )}
          </div>
        </div>

        {/* Recommendations */}
        <div className="bg-white rounded-2xl shadow-lg p-8">
          <h3 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
            <TrendingUp className="w-7 h-7 text-purple-600 mr-3" />
            Recommendations
          </h3>
          <div className="space-y-4">
            {/* [DRA-62 FIX] 7. Add the new suggestions first */}
            {overall_suggestions && overall_suggestions.length > 0 && (
              <div className="space-y-4">
                {overall_suggestions.map((rec, idx) => (
                  <div
                    key={`sug-${idx}`}
                    className="p-5 bg-blue-50 rounded-2xl border-2 border-blue-200"
                  >
                    <p className="text-gray-700 leading-relaxed">{rec}</p>
                  </div>
                ))}
              </div>
            )}
            
            {/* Then add the old recommendations */}
            {recommendations && recommendations.length > 0 && (
              <div className="space-y-4 mt-4">
                {recommendations.map((rec, idx) => (
                  <div
                    key={`rec-${idx}`}
                    className="p-5 bg-purple-50 rounded-2xl border-2 border-purple-200"
                  >
                    <p className="text-gray-700 leading-relaxed">{rec}</p>
                  </div>
                ))}
              </div>
            )}

            {(!recommendations || recommendations.length === 0) && (!overall_suggestions || overall_suggestions.length === 0) && (
              <p className="text-gray-500">Your resume looks great, no immediate suggestions!</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// [DRA-62 FIX] 8. Add the new props to PropTypes for safety
CompareResults.propTypes = {
  results: PropTypes.shape({
    fit_percentage: PropTypes.number.isRequired,
    overall_score: PropTypes.number, // This is your new score
    fit_category: PropTypes.string.isRequired,
    matched_skills: PropTypes.arrayOf(PropTypes.string).isRequired,
    missing_skills: PropTypes.arrayOf(PropTypes.string).isRequired,
    skill_match_percentage: PropTypes.number.isRequired,
    experience_match_percentage: PropTypes.number.isRequired,
    education_match_percentage: PropTypes.number.isRequired,
    recommendations: PropTypes.arrayOf(PropTypes.string).isRequired,
    overall_suggestions: PropTypes.arrayOf(PropTypes.string), // New suggestions
    explanation: PropTypes.string.isRequired,
  }).isRequired,
  onReset: PropTypes.func.isRequired,
};

export default CompareResults;