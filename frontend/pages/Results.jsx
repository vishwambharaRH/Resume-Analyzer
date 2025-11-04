// At the top of Results.jsx, add the navbar
<div className="sticky top-0 z-50 bg-white border-b border-gray-200">
  <nav className="flex items-center justify-between px-10 py-4 max-w-7xl mx-auto">
    <button
      onClick={() => onNavigate('home')}
      className="flex items-center gap-2 text-gray-700 hover:text-gray-900 transition-colors duration-200"
    >
      <ArrowLeft className="w-5 h-5" />
      <span className="font-semibold">Back to Homepage</span>
    </button>
    <div className="flex items-center gap-3">
      <p className="text-2xl font-bold bg-gradient-to-r from-purple-600 via-gray-900 to-blue-600 bg-clip-text text-transparent">
        RESUMIND
      </p>
    </div>
  </nav>
</div>