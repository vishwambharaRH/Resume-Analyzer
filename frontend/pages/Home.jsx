import React from 'react';
import { Zap, Target, Award, TrendingUp, CheckCircle, ArrowRight } from 'lucide-react';

const Home = ({ onNavigate }) => {
  return (
    <div className="min-h-screen bg-gradient-to-b from-purple-50 via-pink-50 to-white">
      {/* Navbar */}
      <nav className="flex items-center justify-between px-10 py-6 max-w-7xl mx-auto">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-purple-600 to-blue-600 rounded-xl flex items-center justify-center">
            <Zap className="w-6 h-6 text-white" />
          </div>
          <p className="text-2xl font-bold bg-gradient-to-r from-purple-600 via-gray-900 to-blue-600 bg-clip-text text-transparent">
            RESUMIND
          </p>
        </div>
        <button
          onClick={() => onNavigate('upload')}
          className="bg-gradient-to-b from-purple-500 to-purple-700 text-white px-6 py-3 rounded-full font-semibold hover:shadow-xl transition-all duration-300"
        >
          Upload Resume
        </button>
      </nav>

      {/* Hero Section */}
      <div className="container mx-auto px-8 py-20 max-w-6xl text-center">
        <div className="mb-12">
          <div className="inline-block mb-8">
            <div className="w-24 h-24 bg-gradient-to-br from-purple-600 to-blue-600 rounded-3xl flex items-center justify-center shadow-2xl mx-auto">
              <Zap className="w-12 h-12 text-white" />
            </div>
          </div>
          
          <h1 className="text-7xl font-extrabold mb-6 leading-tight tracking-tight">
            <span className="bg-gradient-to-r from-purple-600 via-gray-900 to-blue-600 bg-clip-text text-transparent">
              Smart Feedback for
            </span>
            <br />
            <span className="bg-gradient-to-r from-purple-600 via-gray-900 to-blue-600 bg-clip-text text-transparent">
              Your Dream Job
            </span>
          </h1>
          
          <p className="text-2xl text-gray-600 mb-12 max-w-3xl mx-auto">
            Drop your resume for an ATS score and improvement tips powered by AI
          </p>
          
          <button
            onClick={() => onNavigate('upload')}
            className="group bg-gradient-to-b from-purple-500 to-purple-700 text-white px-12 py-5 rounded-full text-xl font-bold shadow-2xl hover:shadow-purple-500/50 transform hover:scale-105 transition-all duration-300 inline-flex items-center gap-3"
          >
            Analyze Your Resume
            <ArrowRight className="w-6 h-6 group-hover:translate-x-2 transition-transform duration-300" />
          </button>
        </div>

        {/* Feature Cards */}
        <div className="grid md:grid-cols-3 gap-8 mt-24 max-w-5xl mx-auto">
          <div className="bg-white rounded-3xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2">
            <div className="w-16 h-16 bg-gradient-to-br from-purple-100 to-purple-200 rounded-2xl flex items-center justify-center mb-6 mx-auto">
              <Target className="w-8 h-8 text-purple-600" />
            </div>
            <h3 className="text-xl font-bold mb-4 text-gray-900">
              Instant Analysis
            </h3>
            <p className="text-gray-600 leading-relaxed">
              Get comprehensive feedback on your resume in seconds
            </p>
          </div>

          <div className="bg-white rounded-3xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-100 to-blue-200 rounded-2xl flex items-center justify-center mb-6 mx-auto">
              <Award className="w-8 h-8 text-blue-600" />
            </div>
            <h3 className="text-xl font-bold mb-4 text-gray-900">
              ATS Score
            </h3>
            <p className="text-gray-600 leading-relaxed">
              See how well your resume performs with applicant tracking systems
            </p>
          </div>

          <div className="bg-white rounded-3xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2">
            <div className="w-16 h-16 bg-gradient-to-br from-pink-100 to-pink-200 rounded-2xl flex items-center justify-center mb-6 mx-auto">
              <TrendingUp className="w-8 h-8 text-pink-600" />
            </div>
            <h3 className="text-xl font-bold mb-4 text-gray-900">
              Improvement Tips
            </h3>
            <p className="text-gray-600 leading-relaxed">
              Actionable suggestions to make your resume stand out
            </p>
          </div>
        </div>

        {/* What We Analyze */}
        <div className="mt-24 bg-white rounded-3xl shadow-2xl p-12 max-w-4xl mx-auto">
          <h2 className="text-4xl font-bold mb-10 bg-gradient-to-r from-purple-600 via-gray-900 to-blue-600 bg-clip-text text-transparent">
            What We Analyze
          </h2>
          <div className="grid md:grid-cols-2 gap-6">
            {[
              'Skills & Keywords Optimization',
              'Experience Quality Assessment',
              'Education Credentials',
              'Project Descriptions',
              'ATS Compatibility Score',
              'Format & Structure Analysis',
              'Content Relevance',
              'Professional Tone & Style'
            ].map((feature, idx) => (
              <div key={idx} className="flex items-center gap-4 p-4 rounded-xl hover:bg-purple-50 transition-colors duration-200">
                <CheckCircle className="w-6 h-6 text-green-500 flex-shrink-0" />
                <span className="text-gray-700 text-lg font-medium">{feature}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;