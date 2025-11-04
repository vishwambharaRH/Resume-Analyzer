import React from 'react';
import { ArrowLeft, Download } from 'lucide-react';
import Summary from './Summary';
import Details from './Details';

const Results = ({ onNavigate, jobData }) => {
  // Mock feedback data matching the structure
  const mockFeedback = {
    overallScore: 87,
    toneAndStyle: {
      score: 92,
      tips: [
        {
          type: 'good',
          tip: 'Professional Language',
          explanation:
            'Your resume uses appropriate professional terminology and maintains a formal tone throughout.',
        },
        {
          type: 'good',
          tip: 'Action-Oriented Verbs',
          explanation:
            'Great use of strong action verbs like "Led," "Implemented," and "Optimized" to describe your achievements.',
        },
        {
          type: 'improve',
          tip: 'Consistency in Tense',
          explanation:
            'Mix of past and present tense detected. Use past tense for previous roles and present tense for current position.',
        },
      ],
    },
    content: {
      score: 85,
      tips: [
        {
          type: 'good',
          tip: 'Quantifiable Achievements',
          explanation:
            'Excellent use of metrics and numbers to demonstrate impact (e.g., "Increased efficiency by 40%").',
        },
        {
          type: 'improve',
          tip: 'Add More Project Details',
          explanation:
            'Include specific technologies used, team size, and measurable outcomes for each project.',
        },
        {
          type: 'improve',
          tip: 'Expand Professional Summary',
          explanation:
            'Your summary is good but could include more career highlights and unique value propositions.',
        },
      ],
    },
    structure: {
      score: 88,
      tips: [
        {
          type: 'good',
          tip: 'Clear Section Headers',
          explanation: 'Well-defined sections make your resume easy to navigate and ATS-friendly.',
        },
        {
          type: 'good',
          tip: 'Logical Flow',
          explanation:
            'Information is presented in a logical order: summary, experience, education, skills.',
        },
        {
          type: 'improve',
          tip: 'Consistent Formatting',
          explanation:
            'Minor inconsistencies in bullet point indentation and date formatting detected.',
        },
      ],
    },
    skills: {
      score: 78,
      tips: [
        {
          type: 'good',
          tip: 'Relevant Technical Skills',
          explanation:
            'Strong list of in-demand technical skills including Python, React, and cloud technologies.',
        },
        {
          type: 'improve',
          tip: 'Add Certifications',
          explanation:
            'Consider adding a certifications section to showcase continuous learning (AWS, Azure, etc.).',
        },
        {
          type: 'improve',
          tip: 'Group Skills by Category',
          explanation:
            'Organize skills into categories: Programming Languages, Frameworks, Tools, Cloud Platforms.',
        },
      ],
    },
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 py-12">
      <div className="container mx-auto px-6 max-w-7xl">
        {/* Header */}
        <div className="mb-12">
          <button
            onClick={() => onNavigate('upload')}
            className="inline-flex items-center gap-3 text-purple-600 hover:text-purple-700 mb-8 font-semibold text-lg transition-colors duration-200 group"
          >
            <ArrowLeft className="w-5 h-5 group-hover:-translate-x-2 transition-transform duration-200" />
            Analyze Another Resume
          </button>

          <h2 className="text-6xl font-black bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent mb-4">
            Analysis Results
          </h2>
          <p className="text-gray-600 text-xl">
            Here's your comprehensive resume analysis with actionable insights
          </p>
        </div>

        {/* Main Content */}
        <div className="space-y-8">
          {/* Summary Card */}
          <Summary feedback={mockFeedback} />

          {/* Detailed Feedback */}
          <Details feedback={mockFeedback} />

          {/* Download Button */}
          <div className="flex justify-center pt-8">
            <button className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-12 py-5 rounded-full text-xl font-bold shadow-2xl hover:shadow-purple-500/50 transform hover:scale-105 transition-all duration-300 inline-flex items-center gap-3">
              <Download className="w-6 h-6" />
              Download Full Report (PDF)
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Results;