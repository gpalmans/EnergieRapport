import { usePDFDownload } from '../hooks/usePDFDownload';

const PDFDownloadButton = ({ reportData }) => {
  const { downloadPDF, isGenerating, error } = usePDFDownload();

  const handleDownload = async () => {
    await downloadPDF(reportData);
  };

  return (
    <div style={{ display: 'inline-block' }}>
      <button
        onClick={handleDownload}
        disabled={isGenerating}
        style={{
          background: '#1e293b',
          border: '1px solid #334155',
          color: isGenerating ? '#64748b' : '#94a3b8',
          padding: '7px 16px',
          borderRadius: 8,
          fontSize: 12,
          fontWeight: 600,
          cursor: isGenerating ? 'not-allowed' : 'pointer',
          whiteSpace: 'nowrap',
          transition: 'all 0.2s ease'
        }}
        onMouseEnter={(e) => {
          if (!isGenerating) {
            e.target.style.background = '#334155';
            e.target.style.borderColor = '#475569';
          }
        }}
        onMouseLeave={(e) => {
          if (!isGenerating) {
            e.target.style.background = '#1e293b';
            e.target.style.borderColor = '#334155';
          }
        }}
      >
        {isGenerating ? '⏳ PDF genereren...' : '📄 Download PDF'}
      </button>
      
      {error && (
        <div style={{
          position: 'absolute',
          marginTop: 8,
          padding: '8px 12px',
          background: '#7f1d1d22',
          border: '1px solid #ef4444',
          borderRadius: 6,
          fontSize: 11,
          color: '#ef4444',
          zIndex: 10
        }}>
          ⚠️ Fout: {error}
        </div>
      )}
    </div>
  );
};

export default PDFDownloadButton;
