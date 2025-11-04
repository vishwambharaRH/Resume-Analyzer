import React from 'react';

const ScoreBadge = ({ score }) => {
  let badgeClasses = '';
  let badgeText = '';

  if (score > 70) {
    badgeClasses = 'bg-green-100 text-green-700 border-green-200';
    badgeText = 'Strong';
  } else if (score > 49) {
    badgeClasses = 'bg-yellow-100 text-yellow-700 border-yellow-200';
    badgeText = 'Good Start';
  } else {
    badgeClasses = 'bg-red-100 text-red-700 border-red-200';
    badgeText = 'Needs Work';
  }

  return (
    <div className={`px-4 py-1.5 rounded-full border ${badgeClasses} inline-flex items-center gap-2`}>
      <div className="w-2 h-2 rounded-full bg-current"></div>
      <p className="text-sm font-semibold">{badgeText}</p>
    </div>
  );
};

export default ScoreBadge;