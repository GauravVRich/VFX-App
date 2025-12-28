import React, { useState, useEffect } from 'react';

export default function App() {
  const [imgA, setImgA] = useState(null);
  const [imgB, setImgB] = useState(null);
  const [prompt, setPrompt] = useState("");
  const [frames, setFrames] = useState([]);
  const [loading, setLoading] = useState(false);
  const [currentFrame, setCurrentFrame] = useState(0);

  // Animation Loop for the Player
  useEffect(() => {
    if (frames.length > 0) {
      const interval = setInterval(() => {
        setCurrentFrame((prev) => (prev + 1) % frames.length);
      }, 100);
      return () => clearInterval(interval);
    }
  }, [frames]);

  const handleGenerate = async () => {
    setLoading(true);
    const formData = new FormData();
    formData.append("image_a", imgA);
    formData.append("image_b", imgB);
    formData.append("prompt", prompt);

    const res = await fetch("http://localhost:8000/generate", { method: "POST", body: formData });
    const data = await res.json();
    setFrames(data.frames);
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      {/* Upper Section */}
      <div className="flex transition-all duration-500 ease-in-out">
        {/* Left Column: Uploads (Reduces width after generation) */}
        <div className={`${frames.length > 0 ? 'w-1/3' : 'w-full'} space-y-4 border-r border-gray-700 pr-4`}>
          <div className="grid grid-cols-2 gap-4">
            <div className="border-2 border-dashed p-4 text-center">
              <p>Image A (Initial)</p>
              <input type="file" onChange={(e) => setImgA(e.target.files[0])} className="mt-2 text-xs" />
            </div>
            <div className="border-2 border-dashed p-4 text-center">
              <p>Image B (Target)</p>
              <input type="file" onChange={(e) => setImgB(e.target.files[0])} className="mt-2 text-xs" />
            </div>
          </div>
          <textarea 
            className="w-full bg-gray-800 p-2 rounded" 
            placeholder="Context Prompt (e.g., 'smile naturally')"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
          />
          <button 
            onClick={handleGenerate}
            className="w-full bg-blue-600 py-2 rounded hover:bg-blue-500 disabled:bg-gray-600"
            disabled={loading}
          >
            {loading ? "Processing Latents..." : "Generate Frames"}
          </button>
        </div>

        {/* Right Column: Player (Appears after generation) */}
        {frames.length > 0 && (
          <div className="w-2/3 pl-8 flex flex-col items-center justify-center">
            <h2 className="mb-4 text-xl font-bold">Motion Sequence</h2>
            <img src={frames[currentFrame]} className="rounded-lg shadow-2xl w-96 h-96 object-contain bg-black" alt="Tween" />
            <div className="mt-4 text-gray-400">Frame: {currentFrame + 1} / {frames.length}</div>
          </div>
        )}
      </div>

      {/* Bottom Section: Frame Strip */}
      <div className="mt-12 overflow-x-auto">
        <div className="flex space-x-2">
          {frames.map((f, i) => (
            <img key={i} src={f} className="w-24 h-24 object-cover border border-gray-600 rounded" />
          ))}
        </div>
      </div>
    </div>
  );
}