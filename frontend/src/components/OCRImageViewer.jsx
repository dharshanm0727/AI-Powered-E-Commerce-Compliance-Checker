import React, { useState } from 'react';
import { Eye, FileText, Sparkles } from 'lucide-react';

const OCRImageViewer = ({ images, ocrDeclarations }) => {
  const [selectedImg, setSelectedImg] = useState(images && images.length > 0 ? images[0] : null);

  if (!images || images.length === 0) {
    return (
      <div className="p-6 glass-card rounded-xl text-center text-slate-400">
        No product images available for OCR analysis.
      </div>
    );
  }

  return (
    <div className="glass-card rounded-xl p-5 space-y-4 border border-slate-800">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
          <Eye className="w-4 h-4 text-cyan-400" />
          OCR Multi-Image Declarations Viewer
        </h3>
        <span className="text-xs text-slate-400">{images.length} Image(s) Scanned</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Main Image Display */}
        <div className="space-y-3">
          <div className="relative aspect-square rounded-lg bg-slate-900 border border-slate-800 overflow-hidden flex items-center justify-center p-2">
            {selectedImg ? (
              <img src={selectedImg} alt="OCR Target" className="object-contain max-h-full max-w-full rounded" />
            ) : (
              <span className="text-xs text-slate-500">Select an image</span>
            )}
          </div>
          <div className="flex gap-2 overflow-x-auto pb-1">
            {images.map((img, i) => (
              <button
                key={i}
                onClick={() => setSelectedImg(img)}
                className={`w-14 h-14 rounded-lg overflow-hidden border-2 transition-all flex-shrink-0 ${
                  selectedImg === img ? 'border-cyan-400 ring-2 ring-cyan-500/30' : 'border-slate-800 opacity-60 hover:opacity-100'
                }`}
              >
                <img src={img} alt={`Thumb ${i}`} className="w-full h-full object-cover" />
              </button>
            ))}
          </div>
        </div>

        {/* OCR Text & Extracted Declarations */}
        <div className="space-y-3">
          <div className="p-3 bg-slate-900/80 rounded-lg border border-slate-800 max-h-64 overflow-y-auto">
            <h4 className="text-xs font-semibold text-slate-300 mb-2 flex items-center gap-1.5">
              <FileText className="w-3.5 h-3.5 text-cyan-400" />
              Normalized Text Extracted via EasyOCR
            </h4>
            <div className="space-y-2">
              {ocrDeclarations && ocrDeclarations.length > 0 ? (
                ocrDeclarations.map((item, idx) => (
                  <div key={idx} className="p-2 bg-slate-800/50 rounded text-xs space-y-1">
                    <div className="flex items-center justify-between text-slate-300 font-medium">
                      <span>{item.image_url.slice(-25)}</span>
                    </div>
                    <p className="text-slate-400 font-mono whitespace-pre-wrap text-[11px]">
                      {item.detected_text || "No text detected"}
                    </p>
                  </div>
                ))
              ) : (
                <p className="text-xs text-slate-500 italic">No OCR declaration details found.</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OCRImageViewer;
