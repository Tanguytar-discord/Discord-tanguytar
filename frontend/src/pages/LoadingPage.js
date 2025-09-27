import React from 'react';

const LoadingPage = () => {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-900">
      <div className="text-center">
        <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-blue-500 mx-auto mb-4"></div>
        <h2 className="text-white text-xl font-semibold">ConvoTalk</h2>
        <p className="text-gray-400 mt-2">Chargement...</p>
      </div>
    </div>
  );
};

export default LoadingPage;