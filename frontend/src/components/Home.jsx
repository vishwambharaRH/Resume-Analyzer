import React from 'react';
import { Target, Award, TrendingUp, Zap, CheckCircle } from 'lucide-react';

const Home = ({ onNavigate }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 py-20">
      <div className="container mx-auto px-8 max-w-7xl">
        
        {/* Hero Section - Perfectly Centered */}
        <div className="flex flex-col items-center text-center mb-32">
          
          {/* Icon */}
          <div className="mb-10">
            <div className="w-28 h-28 bg-gradient-to-br from-purple-600 to-blue-600 rounded-[28px] flex items-center justify-center shadow-2xl transform hover:scale-110 hover:rotate-3 transition-all duration-300">
              <Zap className="w-14 h-14 text-white" />
            </div>
          </div>
          
          {/* Title */}
          <h1 className="text-7xl md:text-8xl font-black mb-8 bg-gradient-to-r from-purple-600 via-purple-500 to-blue-600 bg-clip-text text-transparent leading-tight tracking-tight">
            AI Resume Analyzer
          </h1>
          
          {/* Subtitle */}
          <p className="text-2xl text-gray-600 mb-14 max-w-4xl mx-auto leading-relaxed font-medium">
            Get instant, AI-powered feedback on your resume with comprehensive insights and actionable improvements
          </p>
          
          {/* CTA Button */}
          <button
            onClick={() => onNavigate('upload')}
            className="group bg-gradient-to-r from-purple-600 to-blue-600 text-white px-16 py-6 rounded-full text-2xl font-bold shadow-2xl hover:shadow-purple-500/50 transform hover:scale-105 transition-all duration-300 inline-flex items-center gap-4"
          >
            Analyze Your Resume
            <svg 
              className="w-7 h-7 group-hover:translate-x-2 transition-transform duration-300" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </button>
        </div>

        {/* Feature Cards - Centered with Better Spacing */}
        <div className="grid md:grid-cols-3 gap-10 mb-32 max-w-6xl mx-auto">
          
          {/* Card 1 */}
          <div className="bg-white rounded-[32px] p-12 shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-3 flex flex-col items-center text-center">
            <div className="w-20 h-20 bg-gradient-to-br from-purple-100 to-purple-200 rounded-[24px] flex items-center justify-center mb-8">
              <Target className="w-10 h-10 text-purple-600" />
            </div>
            <h3 className="text-2xl font-bold mb-5 text-gray-900">
              Instant Analysis
            </h3>
            <p className="text-gray-600 text-lg leading-relaxed">
              Get comprehensive feedback on your resume in just seconds with AI-powered insights
            </p>
          </div>

          {/* Card 2 */}
          <div className="bg-white rounded-[32px] p-12 shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-3 flex flex-col items-center text-center">
            <div className="w-20 h-20 bg-gradient-to-br from-blue-100 to-blue-200 rounded-[24px] flex items-center justify-center mb-8">
              <Award className="w-10 h-10 text-blue-600" />
            </div>
            <h3 className="text-2xl font-bold mb-5 text-gray-900">
              Smart Scoring
            </h3>
            <p className="text-gray-600 text-lg leading-relaxed">
              AI-powered evaluation of every section with detailed scoring and recommendations
            </p>
          </div>

          {/* Card 3 */}
          <div className="bg-white rounded-[32px] p-12 shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-3 flex flex-col items-center text-center">
            <div className="w-20 h-20 bg-gradient-to-br from-pink-100 to-pink-200 rounded-[24px] flex items-center justify-center mb-8">
              <TrendingUp className="w-10 h-10 text-pink-600" />
            </div>
            <h3 className="text-2xl font-bold mb-5 text-gray-900">
              Actionable Tips
            </h3>
            <p className="text-gray-600 text-lg leading-relaxed">
              Clear, specific suggestions to improve your resume and stand out to recruiters
            </p>
          </div>
        </div>

        {/* What We Analyze Section - Centered */}
        <div className="max-w-5xl mx-auto">
          <div className="bg-white rounded-[40px] shadow-2xl p-16">
            <h2 className="text-4xl font-bold text-center mb-14 text-gray-900">
              What We Analyze
            </h2>
            
            <div className="grid md:grid-cols-2 gap-8">
              {[
                'Skills & Keywords Optimization',
                'Experience Quality Assessment',
                'Education Credentials',
                'Project Descriptions',
                'Missing Sections Detection',
                'Format & Structure Analysis',
                'Contact Information Validation',
                'Professional Summary Review'
              ].map((feature, idx) => (
                <div 
                  key={idx} 
                  className="flex items-start gap-5 p-5 rounded-2xl hover:bg-purple-50 transition-all duration-200 group"
                >
                  <CheckCircle className="w-7 h-7 text-green-500 flex-shrink-0 mt-1 group-hover:scale-110 transition-transform duration-200" />
                  <span className="text-gray-700 text-lg font-medium leading-relaxed">
                    {feature}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};

export default Home;