import PropTypes from "prop-types";
import { AlertTriangle, CheckCircle, TrendingDown } from 'lucide-react';

const GapIndicator = ({ gapAnalysis }) => {
  const { gap_count, employment_gaps, gap_feedback } = gapAnalysis;

  return (
    <div className="bg-white rounded-3xl shadow-xl p-8 mb-8">
      <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
        <TrendingDown className="w-7 h-7 text-purple-600" />
        Employment History Analysis
      </h3>

      {/* Gap Count */}
      <div className="mb-6">
        {gap_count === 0 ? (
          <div className="flex items-center gap-3 p-4 bg-green-50 rounded-2xl border-2 border-green-200">
            <CheckCircle className="w-6 h-6 text-green-600" />
            <p className="text-green-800 font-semibold">
              No significant employment gaps detected!
            </p>
          </div>
        ) : (
          <div className="flex items-center gap-3 p-4 bg-yellow-50 rounded-2xl border-2 border-yellow-200">
            <AlertTriangle className="w-6 h-6 text-yellow-600" />
            <p className="text-yellow-800 font-semibold">
              {gap_count} employment gap{gap_count > 1 ? 's' : ''} detected
            </p>
          </div>
        )}
      </div>

      {/* Gap Details */}
      {employment_gaps && employment_gaps.length > 0 && (
        <div className="space-y-4 mb-6">
          {employment_gaps.map((gap, idx) => (
            <div
              key={idx}
              className="p-5 bg-yellow-50 rounded-2xl border border-yellow-200"
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <p className="font-bold text-yellow-900">
                    Gap #{idx + 1}: {gap.gap_months} months
                  </p>
                  <p className="text-sm text-yellow-700 mt-1">
                    {gap.gap_start} → {gap.gap_end}
                  </p>
                </div>
                <div className="text-right text-sm text-yellow-700">
                  <p>From: {gap.previous_job}</p>
                  <p>To: {gap.next_job}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Feedback Messages */}
      <div className="space-y-3">
        {gap_feedback && gap_feedback.map((feedback, idx) => (
          <div
            key={idx}
            className={`p-4 rounded-xl ${
              gap_count === 0
                ? 'bg-green-50 text-green-700'
                : 'bg-yellow-50 text-yellow-700'
            }`}
          >
            <p className="leading-relaxed">{feedback}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

GapIndicator.propTypes = {
  gapAnalysis: PropTypes.shape({
    gap_count: PropTypes.number.isRequired,
    employment_gaps: PropTypes.arrayOf(
      PropTypes.shape({
        gap_months: PropTypes.number,
        gap_start: PropTypes.string,
        gap_end: PropTypes.string,
        previous_job: PropTypes.string,
        next_job: PropTypes.string
      })
    ),
    gap_feedback: PropTypes.arrayOf(PropTypes.string)
  }).isRequired
};

export default GapIndicator;