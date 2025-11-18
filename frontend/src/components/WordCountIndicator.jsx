import { FileText, AlertCircle, CheckCircle } from 'lucide-react';
import PropTypes from "prop-types";

const WordCountIndicator = ({ wordAnalysis }) => {
  const { word_count, word_count_status, word_count_feedback } = wordAnalysis;

  const getStatusColor = () => {
    switch (word_count_status) {
      case 'optimal':
        return 'bg-green-50 border-green-200 text-green-700';
      case 'too_short':
        return 'bg-red-50 border-red-200 text-red-700';
      case 'too_long':
        return 'bg-yellow-50 border-yellow-200 text-yellow-700';
      default:
        return 'bg-gray-50 border-gray-200 text-gray-700';
    }
  };

  const getStatusIcon = () => {
    switch (word_count_status) {
      case 'optimal':
        return <CheckCircle className="w-6 h-6 text-green-600" />;
      default:
        return <AlertCircle className="w-6 h-6 text-yellow-600" />;
    }
  };

  return (
    <div className="bg-white rounded-3xl shadow-xl p-8 mb-8">
      <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
        <FileText className="w-7 h-7 text-purple-600" />
        Resume Length Analysis
      </h3>

      <div className={`p-6 rounded-2xl border-2 ${getStatusColor()}`}>
        <div className="flex items-start gap-4">
          {getStatusIcon()}
          <div className="flex-1">
            <p className="font-bold text-xl mb-2">
              Word Count: {word_count}
            </p>
            <p className="leading-relaxed">{word_count_feedback}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

WordCountIndicator.propTypes = {
  wordAnalysis: PropTypes.shape({
    word_count: PropTypes.number.isRequired,
    word_count_status: PropTypes.string.isRequired,
    word_count_feedback: PropTypes.string.isRequired,
  }).isRequired,
};

export default WordCountIndicator;