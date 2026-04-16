import React, { useState } from 'react';
import { Upload, ChevronRight, CheckCircle, AlertCircle, Loader2, CreditCard } from 'lucide-react';
import { apiService } from '../services/api';

const IdentityVerification = () => {
  // Steps: 
  // 1: Upload PAN, 2: Verify PAN, 3: PAN Success
  // 4: Upload Aadhar, 5: Verify Aadhar, 6: Final Success
  const [step, setStep] = useState(1); 
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [extractedData, setExtractedData] = useState(null);
  const [panNumber, setPanNumber] = useState('');
  const [file, setFile] = useState(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const docType = step === 1 ? 'PAN' : 'AADHAR';
      const response = await apiService.extractDocument(file, docType);
      const data = response.data; // Backend returns { status: 'success', data: ... }
      
      if (data.is_error) {
        setError(data.error_message || 'The provided document is invalid.');
        setFile(null);
        return;
      }
      
      setExtractedData(data.extraction_data);
      // Move to verify step
      setStep(step === 1 ? 2 : 5); 
      setFile(null); // Clear file for next upload
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handlePanConfirm = async (e) => {
    e.preventDefault();
    // BUG-02: Validate required field before sending
    if (!extractedData.last_name?.trim()) {
      setError('Last name is required. Please correct it above.');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      // BUG-02: Explicitly map to TaxpayerCreateRequest — do not send raw extraction schema
      await apiService.createTaxpayer({
        pan_number: extractedData.pan_number,
        first_name: extractedData.first_name,
        middle_name: extractedData.middle_name,
        last_name: extractedData.last_name,
        dob: extractedData.dob,
        father_name: extractedData.father_name,
      });
      setPanNumber(extractedData.pan_number);
      setStep(3);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAadharConfirm = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      // BUG-05: Explicitly map to TaxpayerLinkAadharRequest — strip extra Aadhar schema fields
      await apiService.linkAadhar(panNumber, {
        aadhar_number: extractedData.aadhar_number,
        gender: extractedData.gender,
        address_line: extractedData.address_line,
        pincode: extractedData.pincode,
      });
      setStep(6);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="animate-fade">
      <div className="card" style={{ maxWidth: '600px', margin: '0 auto' }}>
        
        {/* PROGRESS INDICATOR */}
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2rem', padding: '0 1rem' }}>
          {[1, 2, 3].map((i) => (
            <div key={i} style={{ 
              width: '32%', height: '4px', 
              background: step >= (i*2-1) ? 'var(--primary)' : 'var(--border)',
              borderRadius: '2px',
              transition: 'background 0.3s'
            }} />
          ))}
        </div>

        {/* STEP 1: UPLOAD PAN */}
        {step === 1 && (
          <div>
            <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', marginBottom: '1rem' }}>
              <div style={{ background: 'var(--bg-main)', padding: '0.5rem', borderRadius: '8px' }}>
                <CreditCard size={20} color="var(--primary)" />
              </div>
              <h2 style={{ margin: 0 }}>PAN Card Verification</h2>
            </div>
            <p style={{ marginBottom: '2rem' }}>Upload your PAN card image. We'll use AI to extract your identification details automatically.</p>
            
            <UploadBox file={file} onChange={handleFileChange} inputId="pan-upload" />

            {error && <ErrorMessage message={error} />}

            <button 
              className="btn btn-primary" style={{ width: '100%' }}
              disabled={!file || loading} onClick={handleUpload}
            >
              {loading ? <Loader2 className="animate-spin" /> : 'Process PAN Card'}
              {!loading && <ChevronRight size={18} />}
            </button>
          </div>
        )}

        {/* STEP 2: VERIFY PAN */}
        {step === 2 && extractedData && (
          <form onSubmit={handlePanConfirm}>
            <h2>Verify PAN Details</h2>
            <p style={{ marginBottom: '1.5rem' }}>Confirm the information extracted from your PAN card.</p>
            
            <FormInput label="PAN Number" value={extractedData.pan_number} 
              onChange={(v) => setExtractedData({ ...extractedData, pan_number: v })} />
            
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <FormInput label="First Name" value={extractedData.first_name} 
                onChange={(v) => setExtractedData({ ...extractedData, first_name: v })} />
              <FormInput label="Last Name" value={extractedData.last_name} 
                onChange={(v) => setExtractedData({ ...extractedData, last_name: v })} />
            </div>

            <FormInput label="Father's Name" value={extractedData.father_name} 
              onChange={(v) => setExtractedData({ ...extractedData, father_name: v })} />
            
            <FormInput label="Date of Birth" type="date" value={extractedData.dob} 
              onChange={(v) => setExtractedData({ ...extractedData, dob: v })} />

            {error && <ErrorMessage message={error} />}

            <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
              <button type="button" className="btn btn-outline" style={{ flex: 1 }} onClick={() => setStep(1)}>Back</button>
              <button type="submit" className="btn btn-primary" style={{ flex: 2 }} disabled={loading}>
                {loading ? <Loader2 className="animate-spin" /> : 'Save & Continue'}
              </button>
            </div>
          </form>
        )}

        {/* STEP 3: PAN SUCCESS / OFFER AADHAR */}
        {step === 3 && (
          <div style={{ textAlign: 'center', padding: '1rem 0' }}>
            <div style={{ background: '#ecfdf5', width: '64px', height: '64px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1.5rem' }}>
              <CheckCircle size={32} color="var(--success)" />
            </div>
            <h2>PAN Verified Successfully</h2>
            <p style={{ marginBottom: '2rem' }}>Great! Your basic profile is ready. To complete your identity verification, we recommend linking your Aadhar card.</p>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <button className="btn btn-primary" onClick={() => setStep(4)}>
                Link Aadhar Card
                <ChevronRight size={18} />
              </button>
              <button className="btn btn-outline" onClick={() => setStep(6)}>
                I'll do this later
              </button>
            </div>
          </div>
        )}

        {/* STEP 4: UPLOAD AADHAR */}
        {step === 4 && (
          <div>
            <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', marginBottom: '1rem' }}>
              <div style={{ background: 'var(--bg-main)', padding: '0.5rem', borderRadius: '8px' }}>
                <CreditCard size={20} color="var(--primary)" />
              </div>
              <h2 style={{ margin: 0 }}>Aadhar Card Linkage</h2>
            </div>
            <p style={{ marginBottom: '2rem' }}>Upload your Aadhar card image. This will link your biometric data to your tax profile.</p>
            
            <UploadBox file={file} onChange={handleFileChange} inputId="aadhar-upload" />

            {error && <ErrorMessage message={error} />}

            <button 
              className="btn btn-primary" style={{ width: '100%' }}
              disabled={!file || loading} onClick={handleUpload}
            >
              {loading ? <Loader2 className="animate-spin" /> : 'Process Aadhar Card'}
              {!loading && <ChevronRight size={18} />}
            </button>
            <button className="btn btn-outline" style={{ width: '100%', marginTop: '0.75rem' }} onClick={() => setStep(3)}>Back</button>
          </div>
        )}

        {/* STEP 5: VERIFY AADHAR */}
        {step === 5 && extractedData && (
          <form onSubmit={handleAadharConfirm}>
            <h2>Verify Aadhar Details</h2>
            <p style={{ marginBottom: '1.5rem' }}>Confirm the information extracted from your Aadhar card.</p>
            
            <FormInput label="Aadhar Number" value={extractedData.aadhar_number} 
              onChange={(v) => setExtractedData({ ...extractedData, aadhar_number: v })} />
            
            <div className="input-group">
              <label className="input-label">Gender</label>
              <select className="input-field" value={extractedData.gender || ''} 
                onChange={(e) => setExtractedData({ ...extractedData, gender: e.target.value })}>
                <option value="">Select Gender</option>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <FormInput label="Address" value={extractedData.address_line} 
              onChange={(v) => setExtractedData({ ...extractedData, address_line: v })} />
            
            <FormInput label="Pincode" value={extractedData.pincode} 
              onChange={(v) => setExtractedData({ ...extractedData, pincode: v })} />

            {error && <ErrorMessage message={error} />}

            <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
              <button type="button" className="btn btn-outline" style={{ flex: 1 }} onClick={() => setStep(4)}>Back</button>
              <button type="submit" className="btn btn-primary" style={{ flex: 2 }} disabled={loading}>
                {loading ? <Loader2 className="animate-spin" /> : 'Link Aadhar'}
              </button>
            </div>
          </form>
        )}

        {/* STEP 6: FINAL SUCCESS */}
        {step === 6 && (
          <div style={{ textAlign: 'center', padding: '2rem 0' }}>
            <div style={{ background: '#ecfdf5', width: '80px', height: '80px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 2rem' }}>
              <CheckCircle size={40} color="var(--success)" />
            </div>
            <h2>Full Identity Verified</h2>
            <p style={{ marginBottom: '2.5rem' }}>Everything looks perfect! Your PAN and Aadhar are verified and linked. You can now proceed to declare your income and investments.</p>
            <button className="btn btn-primary" style={{ padding: '0.75rem 2.5rem' }} onClick={() => window.location.reload()}>
              Proceed to Declarations
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

// HELPER COMPONENTS
// BUG-01: Accept unique inputId per instance to avoid ID collision between PAN and Aadhar upload boxes
const UploadBox = ({ file, onChange, inputId }) => (
  <div 
    style={{
      border: '2px dashed var(--border)', borderRadius: 'var(--radius)',
      padding: '3rem', textAlign: 'center', cursor: 'pointer',
      marginBottom: '1.5rem', transition: 'background 0.2s',
    }}
    onClick={() => document.getElementById(inputId).click()}
    onMouseOver={(e) => e.currentTarget.style.background = 'var(--bg-main)'}
    onMouseOut={(e) => e.currentTarget.style.background = 'transparent'}
  >
    <Upload size={40} color="var(--primary)" style={{ marginBottom: '1rem' }} />
    <input id={inputId} type="file" hidden accept="image/*,application/pdf" onChange={onChange} />
    {file ? (
      <p style={{ color: 'var(--text-main)', fontWeight: 500 }}>{file.name}</p>
    ) : (
      <p>Click to browse or drag and drop your document</p>
    )}
  </div>
);

const FormInput = ({ label, value, type = 'text', onChange, placeholder = '' }) => (
  <div className="input-group">
    <label className="input-label">{label}</label>
    <input 
      className="input-field" 
      type={type} 
      value={value || ''} 
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
    />
  </div>
);

const ErrorMessage = ({ message }) => (
  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--error)', marginBottom: '1.5rem', fontSize: '0.875rem', background: '#fef2f2', padding: '0.75rem', borderRadius: '8px' }}>
    <AlertCircle size={16} />
    <span>{message}</span>
  </div>
);

export default IdentityVerification;
