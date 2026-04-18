import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { LogIn, UserPlus, ArrowRight, ShieldCheck, Mail, Phone, Lock, Hash, MapPin, AlertCircle, Eye, EyeOff } from 'lucide-react';
import { apiService } from '../services/api';

const AuthPage = () => {
    const navigate = useNavigate();
    const [isLogin, setIsLogin] = useState(true);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);
    const [showPassword, setShowPassword] = useState(false);

    const [form, setForm] = useState({
        first_name: '',
        middle_name: '',
        last_name: '',
        pan_number: '',
        aadhar_number: '',
        aadhar_pincode: '',
        mobile_number: '',
        email: '',
        password: ''
    });

    // Validation Logic
    const validations = useMemo(() => {
        const panRegex = /^[A-Z]{5}[0-9]{4}[A-Z]$/;
        const aadharRegex = /^[0-9]{12}$/;
        const mobileRegex = /^[0-9]{10}$/;
        const pincodeRegex = /^[0-9]{6}$/;
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        return {
            pan: panRegex.test(form.pan_number.toUpperCase()),
            aadhar: aadharRegex.test(form.aadhar_number.replace(/\s/g, '')),
            mobile: mobileRegex.test(form.mobile_number),
            pincode: pincodeRegex.test(form.aadhar_pincode),
            email: emailRegex.test(form.email),
            password: form.password.length >= 8,
            first_name: form.first_name.trim().length > 0,
            last_name: form.last_name.trim().length > 0
        };
    }, [form]);

    const isFormValid = isLogin
        ? (validations.pan && validations.password)
        : (validations.first_name && validations.last_name && validations.pan &&
            validations.aadhar && validations.pincode && validations.mobile &&
            validations.email && validations.password);

    const handleChange = (e) => {
        let value = e.target.value;
        if (e.target.name === 'pan_number') value = value.toUpperCase();
        setForm({ ...form, [e.target.name]: value });
        if (error) setError(null);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!isFormValid) return;

        setLoading(true);
        setError(null);

        try {
            if (isLogin) {
                const user = await apiService.login(form.pan_number, form.password);
                setSuccess(`Welcome back, ${user.first_name}!`);
            } else {
                const user = await apiService.signup({
                    ...form,
                    aadhar_number: form.aadhar_number.replace(/\s/g, '')
                });
                setSuccess(`Account created! Welcome, ${user.first_name}.`);
            }
        } catch (err) {
            setError(err.message || "An unexpected error occurred");
        } finally {
            setLoading(false);
        }
    };

    if (success) {
        return (
            <div className="auth-container">
                <div className="glass-card" style={{ textAlign: 'center' }}>
                    <div style={{ background: 'var(--success)', width: '64px', height: '64px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1.5rem' }}>
                        <ShieldCheck size={32} color="#fff" />
                    </div>
                    <h1>Authenticated</h1>
                    <p className="subtitle">{success}</p>
                    <button className="btn btn-primary" onClick={() => navigate('/itr-select')}>
                        Continue to Filing <ArrowRight size={18} />
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="auth-container">
            <div className="glass-card">
                <header style={{ marginBottom: '2.5rem' }}>
                    <h1>{isLogin ? 'Welcome Back' : 'Join ITR Filing'}</h1>
                    <p className="subtitle">
                        {isLogin ? 'Enter your credentials to access your portal.' : 'Create your tax filing account in seconds.'}
                    </p>
                </header>

                <form onSubmit={handleSubmit}>
                    {!isLogin && (
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem' }}>
                            <div className="input-group">
                                <label className="input-label">First Name</label>
                                <input type="text" name="first_name" className="input-field" placeholder="John" required value={form.first_name} onChange={handleChange} />
                                {form.first_name && !validations.first_name && <span className="error-text">Required</span>}
                            </div>
                            <div className="input-group">
                                <label className="input-label">Middle Name</label>
                                <input type="text" name="middle_name" className="input-field" placeholder="Paul" value={form.middle_name} onChange={handleChange} />
                            </div>
                            <div className="input-group">
                                <label className="input-label">Last Name</label>
                                <input type="text" name="last_name" className="input-field" placeholder="Doe" required value={form.last_name} onChange={handleChange} />
                                {form.last_name && !validations.last_name && <span className="error-text">Required</span>}
                            </div>
                        </div>
                    )}

                    <div className="input-group">
                        <label className="input-label">PAN Number</label>
                        <div style={{ position: 'relative' }}>
                            <Hash size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-secondary)' }} />
                            <input type="text" name="pan_number" className="input-field" style={{ paddingLeft: '3rem', borderColor: form.pan_number && !validations.pan ? 'var(--error)' : '' }} placeholder="ABCDE1234F" required value={form.pan_number} onChange={handleChange} maxLength={10} />
                        </div>
                        {form.pan_number && !validations.pan && <span className="error-text">Invalid PAN format</span>}
                    </div>

                    {!isLogin && (
                        <>
                            <div className="input-group">
                                <label className="input-label">Aadhar Number</label>
                                <div style={{ position: 'relative' }}>
                                    <ShieldCheck size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-secondary)' }} />
                                    <input type="text" name="aadhar_number" className="input-field" style={{ paddingLeft: '3rem', borderColor: form.aadhar_number && !validations.aadhar ? 'var(--error)' : '' }} placeholder="1234 5678 9012" required value={form.aadhar_number} onChange={handleChange} maxLength={14} />
                                </div>
                                {form.aadhar_number && !validations.aadhar && <span className="error-text">Invalid Aadhar</span>}
                            </div>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                                <div className="input-group">
                                    <label className="input-label">Pincode</label>
                                    <input type="text" name="aadhar_pincode" className="input-field" style={{ borderColor: form.aadhar_pincode && !validations.pincode ? 'var(--error)' : '' }} placeholder="400001" required value={form.aadhar_pincode} onChange={handleChange} maxLength={6} />
                                    {form.aadhar_pincode && !validations.pincode && <span className="error-text">6 digits</span>}
                                </div>
                                <div className="input-group">
                                    <label className="input-label">Email</label>
                                    <input type="email" name="email" className="input-field" style={{ borderColor: form.email && !validations.email ? 'var(--error)' : '' }} placeholder="john@example.com" required value={form.email} onChange={handleChange} />
                                    {form.email && !validations.email && <span className="error-text">Invalid email</span>}
                                </div>
                            </div>

                            <div className="input-group">
                                <label className="input-label">Mobile Number</label>
                                <div style={{ position: 'relative' }}>
                                    <Phone size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-secondary)' }} />
                                    <input type="text" name="mobile_number" className="input-field" style={{ paddingLeft: '3rem', borderColor: form.mobile_number && !validations.mobile ? 'var(--error)' : '' }} placeholder="9876543210" required value={form.mobile_number} onChange={handleChange} maxLength={10} />
                                </div>
                                {form.mobile_number && !validations.mobile && <span className="error-text">10 digits</span>}
                            </div>
                        </>
                    )}

                    <div className="input-group">
                        <label className="input-label">Password</label>
                        <div style={{ position: 'relative' }}>
                            <Lock size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-secondary)' }} />
                            <input type={showPassword ? "text" : "password"} name="password" className="input-field" style={{ paddingLeft: '3rem', paddingRight: '3rem', borderColor: form.password && !validations.password ? 'var(--error)' : '' }} placeholder="••••••••" required value={form.password} onChange={handleChange} />
                            <div onClick={() => setShowPassword(!showPassword)} style={{ position: 'absolute', right: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-secondary)', cursor: 'pointer' }}>
                                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                            </div>
                        </div>
                        {form.password && !validations.password && <span className="error-text">Min 8 characters</span>}
                    </div>

                    {error && (
                        <div className="error-text" style={{ marginBottom: '1.5rem', textAlign: 'center', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', background: 'rgba(244, 63, 94, 0.1)', padding: '0.75rem', borderRadius: '10px' }}>
                            <AlertCircle size={16} /> {error}
                        </div>
                    )}

                    <button className="btn btn-primary" type="submit" disabled={loading || !isFormValid}>
                        {loading ? <div className="loading-spinner"></div> : (isLogin ? 'Login Now' : 'Create Account')}
                        {!loading && (isLogin ? <LogIn size={18} /> : <UserPlus size={18} />)}
                    </button>
                </form>

                <div className="auth-toggle">
                    {isLogin ? "Don't have an account? " : "Already have an account? "}
                    <b onClick={() => setIsLogin(!isLogin)}>{isLogin ? 'Sign Up' : 'Log In'}</b>
                </div>
            </div>
        </div>
    );
};

export default AuthPage;
