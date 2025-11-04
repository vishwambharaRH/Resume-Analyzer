import React from 'react';
import ScoreGauge from './ScoreGauge';
import ScoreBadge from './ScoreBadge';

const Category = ({ title, score }) => {
  const textColor =
    score > 70 ? 'text-green-600' : score > 49 ? 'text-yellow-600' : 'text-red-600';

  return (
    <div className="border-t border-gray-100 p-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <p className="text-xl font-semibold text-gray-800">{title}</p>
          <ScoreBadge score={score} />
        </div>
        <p className="text-2xl font-bold">
          <span className={textColor}>{score}</span>
          <span className="text-gray-400">/100</span>
        </p>
      </div>
    </div>
  );
};

const Summary = ({ feedback }) => {
  return (
    <div className="bg-white rounded-3xl shadow-xl w-full overflow-hidden">
      {/* Header with Gauge */}
      <div className="flex items-center p-8 gap-8 border-b border-gray-100">
        <ScoreGauge score={feedback.overallScore} />
        <div className="flex flex-col gap-2">
          <h2 className="text-3xl font-bold text-gray-900">Your Resume Score</h2>
          <p className="text-base text-gray-500">
            This score is calculated based on the variables listed below.
          </p>
        </div>
      </div>

      {/* Categories */}
      <Category title="Tone & Style" score={feedback.toneAndStyle.score} />
      <Category title="Content" score={feedback.content.score} />
      <Category title="Structure" score={feedback.structure.score} />
      <Category title="Skills" score={feedback.skills.score} />
    </div>
  );
};

export default Summary;