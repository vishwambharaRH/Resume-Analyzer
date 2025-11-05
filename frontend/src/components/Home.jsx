import React from "react";
import { Upload, Target, Award, TrendingUp, Zap } from "lucide-react";

const Home = ({ onNavigate }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 flex items-center justify-center p-8">
      <div className="max-w-5xl w-full">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <div className="inline-block mb-6">
            <div className="w-20 h-20 bg-gradient-to-br from-purple-600 to-blue-600 rounded-2xl flex items-center justify-center shadow-2xl transform hover:scale-110 transition-transform duration-300">
              <Zap className="w-10 h-10 text-white" />
            </div>
          </div>
          <h1 className="text-6xl font-bold mb-4 bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
            AI Resume Analyzer
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Get instant feedback on your resume with AI-powered insights
          </p>
          <button
            onClick={() => onNavigate("upload")}
            className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-12 py-4 rounded-full text-lg font-semibold shadow-xl hover:shadow-2xl transform hover:scale-105 transition-all duration-300"
          >
            Analyze Your Resume
          </button>
        </div>

        {/* Feature Cards */}
        <div className="grid md:grid-cols-3 gap-6 mt-16">
          <div className="bg-white rounded-3xl p-8 shadow-lg hover:shadow-2xl transition-shadow duration-300">
            <div className="w-14 h-14 bg-purple-100 rounded-2xl flex items-center justify-center mb-4">
              <Target className="w-7 h-7 text-purple-600" />
            </div>
            <h3 className="text-xl font-bold mb-2 text-gray-800">
              Instant Analysis
            </h3>
            <p className="text-gray-600">
              Get comprehensive feedback in seconds
            </p>
          </div>

          <div className="bg-white rounded-3xl p-8 shadow-lg hover:shadow-2xl transition-shadow duration-300">
            <div className="w-14 h-14 bg-blue-100 rounded-2xl flex items-center justify-center mb-4">
              <Award className="w-7 h-7 text-blue-600" />
            </div>
            <h3 className="text-xl font-bold mb-2 text-gray-800">
              Smart Scoring
            </h3>
            <p className="text-gray-600">
              AI-powered evaluation of every section
            </p>
          </div>

          <div className="bg-white rounded-3xl p-8 shadow-lg hover:shadow-2xl transition-shadow duration-300">
            <div className="w-14 h-14 bg-pink-100 rounded-2xl flex items-center justify-center mb-4">
              <TrendingUp className="w-7 h-7 text-pink-600" />
            </div>
            <h3 className="text-xl font-bold mb-2 text-gray-800">
              Actionable Tips
            </h3>
            <p className="text-gray-600">
              Clear suggestions to improve your resume
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
